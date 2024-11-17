#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#
import torch
import numpy as np
from utils.general_utils import inverse_sigmoid, get_expon_lr_func, build_rotation
from torch import nn
import os
from utils.system_utils import mkdir_p
from plyfile import PlyData, PlyElement
from utils.sh_utils import RGB2SH
from simple_knn._C import distCUDA2
from utils.graphics_utils import BasicPointCloud
from utils.general_utils import strip_symmetric, build_scaling_rotation

import kornia
from plas import sort_with_plas
import torch.nn.functional as F

from renderer_cuda import GaussianDataCUDA

def log_transform(x):
    return torch.sign(x) * torch.log1p(torch.abs(x))

def inverse_log_transform(y):
    assert y.max() < 20, "Probably mixed up linear and log values for xyz. These going in here are supposed to be quite small (log scale)"
    return torch.sign(y) * (torch.expm1(torch.abs(y)))


class GaussianModel:

    def setup_functions(self):
        def build_covariance_from_scaling_rotation(scaling, scaling_modifier, rotation):
            L = build_scaling_rotation(scaling_modifier * scaling, rotation)
            actual_covariance = L @ L.transpose(1, 2)
            symm = strip_symmetric(actual_covariance)
            return symm

        if self.disable_xyz_log_activation:
            self.xyz_activation = lambda x: x
            self.inverse_xyz_activation = lambda x: x
        else:
            self.xyz_activation = inverse_log_transform
            self.inverse_xyz_activation = log_transform

        self.scaling_activation = torch.exp
        self.scaling_inverse_activation = torch.log

        self.covariance_activation = build_covariance_from_scaling_rotation

        self.opacity_activation = torch.sigmoid
        self.inverse_opacity_activation = inverse_sigmoid

        self.rotation_activation = torch.nn.functional.normalize


    def __init__(self, sh_degree : int, disable_xyz_log_activation):
        self.active_sh_degree = 0
        self.max_sh_degree = sh_degree
        self._xyz = torch.empty(0)
        self._features_dc = torch.empty(0)
        self._features_rest = torch.empty(0)
        self._features_rest_r = torch.empty(0)
        self._features_rest_g = torch.empty(0)
        self._features_rest_b = torch.empty(0)
        self._scaling = torch.empty(0)
        self._rotation = torch.empty(0)
        self._opacity = torch.empty(0)
        self.max_radii2D = torch.empty(0)
        self.xyz_gradient_accum = torch.empty(0)
        self.denom = torch.empty(0)
        self.optimizer = None
        self.percent_dense = 0
        self.spatial_lr_scale = 0
        self.disable_xyz_log_activation = disable_xyz_log_activation
        self.extra_gaussians = 0
        self.setup_functions()

    def capture(self):
        return (
            self.active_sh_degree,
            self._xyz,
            self._features_dc,
            self._features_rest,
            self._scaling,
            self._rotation,
            self._opacity,
            self.max_radii2D,
            self.xyz_gradient_accum,
            self.denom,
            self.optimizer.state_dict(),
            self.spatial_lr_scale,
        )

    def restore(self, model_args, training_args):
        (self.active_sh_degree,
        self._xyz,
        self._features_dc,
        self._features_rest,
        self._scaling,
        self._rotation,
        self._opacity,
        self.max_radii2D,
        xyz_gradient_accum,
        denom,
        opt_dict,
        self.spatial_lr_scale) = model_args
        self.training_setup(training_args)
        self.xyz_gradient_accum = xyz_gradient_accum
        self.denom = denom
        self.optimizer.load_state_dict(opt_dict)

    @property
    def get_scaling(self):
        return self.scaling_activation(self._scaling)

    @property
    def get_rotation(self):
        return self.rotation_activation(self._rotation)

    @property
    def get_xyz(self):
        activated = self.xyz_activation(self._xyz)
        return activated

    @property
    def get_features(self):
        features_dc = self._features_dc
        if self.active_sh_degree == 0:
            return features_dc
        features_rest = self._features_rest
        return torch.cat((features_dc, features_rest), dim=1)

    @property
    def get_features_dc(self):
        return self._features_dc
    
    @property
    def get_features_rest(self):
        return self._features_rest

    @property
    def get_opacity(self):
        return self.opacity_activation(self._opacity)
    
    @property
    def get_features_rest_r(self):
        return self._features_rest_r
    
    @property
    def get_features_rest_g(self):
        return self._features_rest_g
    
    @property
    def get_features_rest_b(self):
        return self._features_rest_b

    def get_attr_flat(self, attr_name):
        attr = getattr(self, f"_{attr_name}")
        return attr.flatten(start_dim=1)

    def get_activated_attr_flat(self, attr_name):
        getter_method = f"get_{attr_name}"
        attr = getattr(self, getter_method)
        return attr.flatten(start_dim=1)

    def get_covariance(self, scaling_modifier = 1):
        return self.covariance_activation(self.get_scaling, scaling_modifier, self._rotation)

    def oneupSHdegree(self):
        if self.active_sh_degree < self.max_sh_degree:
            self.active_sh_degree += 1

    def create_from_pcd(self, pcd : BasicPointCloud, spatial_lr_scale : float):
        self.spatial_lr_scale = spatial_lr_scale
        fused_point_cloud = torch.tensor(np.asarray(pcd.points)).float().cuda()
        fused_color = RGB2SH(torch.tensor(np.asarray(pcd.colors)).float().cuda())
        features = torch.zeros((fused_color.shape[0], 3, (self.max_sh_degree + 1) ** 2)).float().cuda()
        features[:, :3, 0 ] = fused_color
        features[:, 3:, 1:] = 0.0

        print("Number of points at initialisation : ", fused_point_cloud.shape[0])

        dist2 = torch.clamp_min(distCUDA2(torch.from_numpy(np.asarray(pcd.points)).float().cuda()), 0.0000001)
        scales = torch.log(torch.sqrt(dist2))[...,None].repeat(1, 3)
        rots = torch.zeros((fused_point_cloud.shape[0], 4), device="cuda")
        rots[:, 0] = 1

        opacities = inverse_sigmoid(0.1 * torch.ones((fused_point_cloud.shape[0], 1), dtype=torch.float, device="cuda"))

        self._xyz = nn.Parameter(self.inverse_xyz_activation(fused_point_cloud).requires_grad_(True))
        self._features_dc = nn.Parameter(features[:,:,0:1].transpose(1, 2).contiguous().requires_grad_(True))
        self._features_rest = nn.Parameter(features[:,:,1:].transpose(1, 2).contiguous().requires_grad_(True))
        self._scaling = nn.Parameter(scales.requires_grad_(True))
        self._rotation = nn.Parameter(rots.requires_grad_(True))
        self._opacity = nn.Parameter(opacities.requires_grad_(True))
        self.max_radii2D = torch.zeros((self.get_xyz.shape[0]), device="cuda")

    def training_setup(self, training_args):
        self.percent_dense = training_args.percent_dense
        self.xyz_gradient_accum = torch.zeros((self.get_xyz.shape[0], 1), device="cuda")
        self.denom = torch.zeros((self.get_xyz.shape[0], 1), device="cuda")

        l = [
            {'params': [self._xyz], 'lr': training_args.position_lr_init * self.spatial_lr_scale, "name": "xyz"},
            {'params': [self._features_dc], 'lr': training_args.feature_lr, "name": "f_dc"},
            {'params': [self._features_rest], 'lr': training_args.feature_lr / 20.0, "name": "f_rest"},
            {'params': [self._opacity], 'lr': training_args.opacity_lr, "name": "opacity"},
            {'params': [self._scaling], 'lr': training_args.scaling_lr, "name": "scaling"},
            {'params': [self._rotation], 'lr': training_args.rotation_lr, "name": "rotation"}
        ]

        self.optimizer = torch.optim.Adam(l, lr=0.0, eps=1e-15)
        self.xyz_scheduler_args = get_expon_lr_func(lr_init=training_args.position_lr_init*self.spatial_lr_scale,
                                                    lr_final=training_args.position_lr_final*self.spatial_lr_scale,
                                                    lr_delay_mult=training_args.position_lr_delay_mult,
                                                    max_steps=training_args.position_lr_max_steps)

    def update_learning_rate(self, iteration):
        ''' Learning rate scheduling per step '''
        for param_group in self.optimizer.param_groups:
            if param_group["name"] == "xyz":
                lr = self.xyz_scheduler_args(iteration)
                param_group['lr'] = lr
                return lr

    def construct_list_of_attributes(self):
        l = ['x', 'y', 'z', 'nx', 'ny', 'nz']
        # All channels except the 3 DC
        for i in range(self._features_dc.shape[1]*self._features_dc.shape[2]):
            l.append('f_dc_{}'.format(i))

        # if self.active_sh_degree > 0:
        for i in range(self._features_rest.shape[1]*self._features_rest.shape[2]):
            l.append('f_rest_{}'.format(i))
        l.append('opacity')
        for i in range(self._scaling.shape[1]):
            l.append('scale_{}'.format(i))
        for i in range(self._rotation.shape[1]):
            l.append('rot_{}'.format(i))
        return l

    def save_ply(self, path):
        mkdir_p(os.path.dirname(path))

        xyz = self.get_xyz.detach().cpu().numpy()
        normals = np.zeros_like(xyz)
        f_dc = self._features_dc.detach().transpose(1, 2).flatten(start_dim=1).contiguous().cpu().numpy()
        # if self.active_sh_degree != 0:
        f_rest = self._features_rest.detach().transpose(1, 2).flatten(start_dim=1).contiguous().cpu().numpy()
        opacities = self._opacity.detach().cpu().numpy()
        scale = self._scaling.detach().cpu().numpy()
        rotation = self._rotation.detach().cpu().numpy()
        # opacities = inverse_sigmoid(self._opacity).detach().cpu().numpy()
        # scale = torch.log(self._scaling).detach().cpu().numpy()

        dtype_full = [(attribute, 'f4') for attribute in self.construct_list_of_attributes()]

        elements = np.empty(xyz.shape[0], dtype=dtype_full)

        # TODO: may need to add empty shs for SIBR_viewer?
        # if self.active_sh_degree > 0:
        attributes = np.concatenate((xyz, normals, f_dc, f_rest, opacities, scale, rotation), axis=1)
        # else:
            # attributes = np.concatenate((xyz, normals, f_dc, opacities, scale, rotation), axis=1)
        elements[:] = list(map(tuple, attributes))
        el = PlyElement.describe(elements, 'vertex')
        PlyData([el]).write(path)

    def reset_opacity(self):
        opacities_new = inverse_sigmoid(torch.min(self.get_opacity, torch.ones_like(self.get_opacity)*0.01))
        optimizable_tensors = self.replace_tensor_to_optimizer(opacities_new, "opacity")
        self._opacity = optimizable_tensors["opacity"]

    def load_ply(self, path):
        plydata = PlyData.read(path)

        xyz = np.stack((np.asarray(plydata.elements[0]["x"]),
                        np.asarray(plydata.elements[0]["y"]),
                        np.asarray(plydata.elements[0]["z"])),  axis=1)
        opacities = np.asarray(plydata.elements[0]["opacity"])[..., np.newaxis]

        features_dc = np.zeros((xyz.shape[0], 3, 1))
        features_dc[:, 0, 0] = np.asarray(plydata.elements[0]["f_dc_0"])
        features_dc[:, 1, 0] = np.asarray(plydata.elements[0]["f_dc_1"])
        features_dc[:, 2, 0] = np.asarray(plydata.elements[0]["f_dc_2"])

        extra_f_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("f_rest_")]
        extra_f_names = sorted(extra_f_names, key = lambda x: int(x.split('_')[-1]))
        assert len(extra_f_names)==3*(self.max_sh_degree + 1) ** 2 - 3

        if self.max_sh_degree > 0:
            features_extra = np.zeros((xyz.shape[0], len(extra_f_names)))
            for idx, attr_name in enumerate(extra_f_names):
                features_extra[:, idx] = np.asarray(plydata.elements[0][attr_name])
            # Reshape (P,F*SH_coeffs) to (P, F, SH_coeffs except DC)
            features_extra = features_extra.reshape((features_extra.shape[0], 3, (self.max_sh_degree + 1) ** 2 - 1))

        scale_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("scale_")]
        scale_names = sorted(scale_names, key = lambda x: int(x.split('_')[-1]))
        scales = np.zeros((xyz.shape[0], len(scale_names)))
        for idx, attr_name in enumerate(scale_names):
            scales[:, idx] = np.asarray(plydata.elements[0][attr_name])

        rot_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("rot")]
        rot_names = sorted(rot_names, key = lambda x: int(x.split('_')[-1]))
        rots = np.zeros((xyz.shape[0], len(rot_names)))
        for idx, attr_name in enumerate(rot_names):
            rots[:, idx] = np.asarray(plydata.elements[0][attr_name])

        self._xyz = nn.Parameter(torch.tensor(xyz, dtype=torch.float, device="cuda").requires_grad_(True))
        self._features_dc = nn.Parameter(torch.tensor(features_dc, dtype=torch.float, device="cuda").transpose(1, 2).contiguous().requires_grad_(True))
        
        if self.max_sh_degree > 0:
            self._features_rest = nn.Parameter(torch.tensor(features_extra, dtype=torch.float, device="cuda").transpose(1, 2).contiguous().requires_grad_(True))
        else:
            self._features_rest = nn.Parameter(torch.empty(0, dtype=torch.float, device="cuda").requires_grad_(True))
        self._opacity = nn.Parameter(torch.tensor(opacities, dtype=torch.float, device="cuda").requires_grad_(True))
        self._scaling = nn.Parameter(torch.tensor(scales, dtype=torch.float, device="cuda").requires_grad_(True))
        self._rotation = nn.Parameter(torch.tensor(rots, dtype=torch.float, device="cuda").requires_grad_(True))

        self.active_sh_degree = self.max_sh_degree

    def replace_tensor_to_optimizer(self, tensor, name):
        optimizable_tensors = {}
        for group in self.optimizer.param_groups:
            if group["name"] == name:
                stored_state = self.optimizer.state.get(group['params'][0], None)
                stored_state["exp_avg"] = torch.zeros_like(tensor)
                stored_state["exp_avg_sq"] = torch.zeros_like(tensor)

                del self.optimizer.state[group['params'][0]]
                group["params"][0] = nn.Parameter(tensor.requires_grad_(True))
                self.optimizer.state[group['params'][0]] = stored_state

                optimizable_tensors[group["name"]] = group["params"][0]
        return optimizable_tensors

    def _prune_optimizer(self, mask):
        optimizable_tensors = {}
        for group in self.optimizer.param_groups:
            stored_state = self.optimizer.state.get(group['params'][0], None)
            if stored_state is not None:
                stored_state["exp_avg"] = stored_state["exp_avg"][mask]
                stored_state["exp_avg_sq"] = stored_state["exp_avg_sq"][mask]

                del self.optimizer.state[group['params'][0]]
                group["params"][0] = nn.Parameter((group["params"][0][mask].requires_grad_(True)))
                self.optimizer.state[group['params'][0]] = stored_state

                optimizable_tensors[group["name"]] = group["params"][0]
            else:
                group["params"][0] = nn.Parameter(group["params"][0][mask].requires_grad_(True))
                optimizable_tensors[group["name"]] = group["params"][0]
        return optimizable_tensors

    def prune_points(self, mask):
        valid_points_mask = ~mask
        optimizable_tensors = self._prune_optimizer(valid_points_mask)

        self._xyz = optimizable_tensors["xyz"]
        self._features_dc = optimizable_tensors["f_dc"]
        self._features_rest = optimizable_tensors["f_rest"]
        self._opacity = optimizable_tensors["opacity"]
        self._scaling = optimizable_tensors["scaling"]
        self._rotation = optimizable_tensors["rotation"]

        self.xyz_gradient_accum = self.xyz_gradient_accum[valid_points_mask]

        self.denom = self.denom[valid_points_mask]
        self.max_radii2D = self.max_radii2D[valid_points_mask]

    def cat_tensors_to_optimizer(self, tensors_dict):
        optimizable_tensors = {}
        for group in self.optimizer.param_groups:
            assert len(group["params"]) == 1
            extension_tensor = tensors_dict[group["name"]]
            stored_state = self.optimizer.state.get(group['params'][0], None)
            if stored_state is not None:

                stored_state["exp_avg"] = torch.cat((stored_state["exp_avg"], torch.zeros_like(extension_tensor)), dim=0)
                stored_state["exp_avg_sq"] = torch.cat((stored_state["exp_avg_sq"], torch.zeros_like(extension_tensor)), dim=0)

                del self.optimizer.state[group['params'][0]]
                group["params"][0] = nn.Parameter(torch.cat((group["params"][0], extension_tensor), dim=0).requires_grad_(True))
                self.optimizer.state[group['params'][0]] = stored_state

                optimizable_tensors[group["name"]] = group["params"][0]
            else:
                group["params"][0] = nn.Parameter(torch.cat((group["params"][0], extension_tensor), dim=0).requires_grad_(True))
                optimizable_tensors[group["name"]] = group["params"][0]

        return optimizable_tensors

    def densification_postfix(self, new_xyz, new_features_dc, new_features_rest, new_opacities, new_scaling, new_rotation):
        d = {"xyz": new_xyz,
        "f_dc": new_features_dc,
        "f_rest": new_features_rest,
        "opacity": new_opacities,
        "scaling" : new_scaling,
        "rotation" : new_rotation}

        optimizable_tensors = self.cat_tensors_to_optimizer(d)
        self._xyz = optimizable_tensors["xyz"]
        self._features_dc = optimizable_tensors["f_dc"]
        self._features_rest = optimizable_tensors["f_rest"]
        self._opacity = optimizable_tensors["opacity"]
        self._scaling = optimizable_tensors["scaling"]
        self._rotation = optimizable_tensors["rotation"]

        self.xyz_gradient_accum = torch.zeros((self.get_xyz.shape[0], 1), device="cuda")
        self.denom = torch.zeros((self.get_xyz.shape[0], 1), device="cuda")
        self.max_radii2D = torch.zeros((self.get_xyz.shape[0]), device="cuda")

    def densify_and_split(self, grads, grad_threshold, scene_extent, N=2):
        n_init_points = self.get_xyz.shape[0]
        # Extract points that satisfy the gradient condition
        padded_grad = torch.zeros((n_init_points), device="cuda")
        padded_grad[:grads.shape[0]] = grads.squeeze()
        selected_pts_mask = torch.where(padded_grad >= grad_threshold, True, False)
        selected_pts_mask = torch.logical_and(selected_pts_mask,
                                              torch.max(self.get_scaling, dim=1).values > self.percent_dense*scene_extent)

        stds = self.get_scaling[selected_pts_mask].repeat(N,1)
        means =torch.zeros((stds.size(0), 3),device="cuda")
        samples = torch.normal(mean=means, std=stds)
        rots = build_rotation(self._rotation[selected_pts_mask]).repeat(N,1,1)
        new_xyz = self.inverse_xyz_activation(torch.bmm(rots, samples.unsqueeze(-1)).squeeze(-1) + self.get_xyz[selected_pts_mask].repeat(N, 1))
        new_scaling = self.scaling_inverse_activation(self.get_scaling[selected_pts_mask].repeat(N,1) / (0.8*N))
        new_rotation = self._rotation[selected_pts_mask].repeat(N,1)
        new_features_dc = self._features_dc[selected_pts_mask].repeat(N,1,1)
        new_features_rest = self._features_rest[selected_pts_mask].repeat(N,1,1)
        new_opacity = self._opacity[selected_pts_mask].repeat(N,1)

        self.densification_postfix(new_xyz, new_features_dc, new_features_rest, new_opacity, new_scaling, new_rotation)

        prune_filter = torch.cat((selected_pts_mask, torch.zeros(N * selected_pts_mask.sum(), device="cuda", dtype=bool)))
        self.prune_points(prune_filter)

    def densify_and_clone(self, grads, grad_threshold, scene_extent):
        # Extract points that satisfy the gradient condition
        selected_pts_mask = torch.where(torch.norm(grads, dim=-1) >= grad_threshold, True, False)
        selected_pts_mask = torch.logical_and(selected_pts_mask,
                                              torch.max(self.get_scaling, dim=1).values <= self.percent_dense*scene_extent)

        new_xyz = self._xyz[selected_pts_mask]
        new_features_dc = self._features_dc[selected_pts_mask]
        new_features_rest = self._features_rest[selected_pts_mask]
        new_opacities = self._opacity[selected_pts_mask]
        new_scaling = self._scaling[selected_pts_mask]
        new_rotation = self._rotation[selected_pts_mask]

        self.densification_postfix(new_xyz, new_features_dc, new_features_rest, new_opacities, new_scaling, new_rotation)

    def densify_and_prune(self, max_grad, min_opacity, extent, max_screen_size):
        grads = self.xyz_gradient_accum / self.denom
        grads[grads.isnan()] = 0.0

        self.densify_and_clone(grads, max_grad, extent)
        self.densify_and_split(grads, max_grad, extent)

        prune_mask = (self.get_opacity < min_opacity).squeeze()
        if max_screen_size:
            big_points_vs = self.max_radii2D > max_screen_size
            big_points_ws = self.get_scaling.max(dim=1).values > 0.1 * extent
            prune_mask = torch.logical_or(torch.logical_or(prune_mask, big_points_vs), big_points_ws)
        self.prune_points(prune_mask)

        torch.cuda.empty_cache()

    def add_densification_stats(self, viewspace_point_tensor, update_filter):
        self.xyz_gradient_accum[update_filter] += torch.norm(viewspace_point_tensor.grad[update_filter,:2], dim=-1, keepdim=True)
        self.denom[update_filter] += 1


    # SSGS implementation

    def prune_all_but_these_indices(self, indices):

        if self.optimizer is not None:

            optimizable_tensors = self._prune_optimizer(indices)

            self._xyz = optimizable_tensors["xyz"]
            self._features_dc = optimizable_tensors["f_dc"]
            self._features_rest = optimizable_tensors["f_rest"]
            self._opacity = optimizable_tensors["opacity"]
            self._scaling = optimizable_tensors["scaling"]
            self._rotation = optimizable_tensors["rotation"]

            self.xyz_gradient_accum = self.xyz_gradient_accum[indices]
            self.denom = self.denom[indices]
            self.max_radii2D = self.max_radii2D[indices]
        else:
            indices = indices.cuda()
            self._xyz = self._xyz[indices]
            self._features_dc = self._features_dc[indices]
            self._features_rest = self._features_rest[indices]
            self._features_rest_r = self._features_rest_r[indices]
            self._features_rest_g = self._features_rest_g[indices]
            self._features_rest_b = self._features_rest_b[indices]
            self._opacity = self._opacity[indices]
            self._scaling = self._scaling[indices]
            self._rotation = self._rotation[indices]


    def prune_to_square_shape(self, sort_by_opacity=True, verbose=True):
        num_gaussians = self._xyz.shape[0]

        self.grid_sidelen = int(np.sqrt(num_gaussians))
        if(self.grid_sidelen%2==1):
            self.grid_sidelen = self.grid_sidelen - 1
        num_removed = num_gaussians - self.grid_sidelen * self.grid_sidelen

        if verbose:
            print(f"Removing {num_removed}/{num_gaussians} gaussians to fit the grid. ({100 * num_removed / num_gaussians:.4f}%)")
        if self.grid_sidelen * self.grid_sidelen < num_gaussians:
            if sort_by_opacity:
                alpha = self.get_opacity[:, 0]
                _, keep_indices = torch.topk(alpha, k=self.grid_sidelen * self.grid_sidelen)
            else:
                shuffled_indices = torch.randperm(num_gaussians)
                keep_indices = shuffled_indices[:self.grid_sidelen * self.grid_sidelen]
            sorted_keep_indices = torch.sort(keep_indices)[0]
            self.prune_all_but_these_indices(sorted_keep_indices)

    
    def prune_to_origin(self, num_removed, sort_by_opacity=True, verbose=True):
        num_gaussians = self._xyz.shape[0]

        if verbose:
            print(f"Removing {num_removed}/{num_gaussians} gaussians")
        if sort_by_opacity:
            alpha = self.get_opacity[:, 0]
            _, keep_indices = torch.topk(alpha, k=num_gaussians - num_removed)
        else:
            shuffled_indices = torch.randperm(num_gaussians)
            keep_indices = shuffled_indices[:num_gaussians - num_removed]
        sorted_keep_indices = torch.sort(keep_indices)[0]
        self.prune_all_but_these_indices(sorted_keep_indices)

    def add_to_square_shape(self):
        num_gaussians = self._xyz.shape[0]

        self.grid_sidelen = int(np.sqrt(num_gaussians))
        if(self.grid_sidelen%2==1):
            self.grid_sidelen = self.grid_sidelen + 1

        num_added = self.grid_sidelen * self.grid_sidelen - num_gaussians
        self.extra_gaussians = num_added

        print(f"Adding {num_added}/{num_gaussians} gaussians to fit the grid. ({100 * num_added / num_gaussians:.4f}%)")

        shape = list(self._xyz.shape)
        shape[0] = num_added
        new_xyz = torch.zeros(shape).cuda()
        self._xyz = torch.cat((self._xyz, new_xyz), dim = 0)

        shape = list(self._opacity.shape)
        shape[0] = num_added
        new_opacity = torch.zeros(shape).cuda()
        self._opacity = torch.cat((self._opacity, new_opacity), dim = 0)

        shape = list(self._scaling.shape)
        shape[0] = num_added
        new_scaling = torch.zeros(shape).cuda()
        self._scaling = torch.cat((self._scaling, new_scaling), dim = 0)

        shape = list(self._rotation.shape)
        shape[0] = num_added
        new_rotation = torch.zeros(shape).cuda()
        self._rotation = torch.cat((self._rotation, new_rotation), dim = 0)

        shape = list(self._features_dc.shape)
        shape[0] = num_added
        new_features_dc = torch.zeros(shape).cuda()
        self._features_dc = torch.cat((self._features_dc, new_features_dc), dim = 0)

        shape = list(self._features_rest.shape)
        shape[0] = num_added
        new_features_rest = torch.zeros(shape).cuda()
        self._features_rest = torch.cat((self._features_rest, new_features_rest), dim = 0)

        shape = list(self._features_rest_r.shape)
        shape[0] = num_added
        new_features_rest_r = torch.zeros(shape).cuda()
        self._features_rest_r = torch.cat((self._features_rest_r, new_features_rest_r), dim = 0)

        shape = list(self._features_rest_g.shape)
        shape[0] = num_added
        new_features_rest_g = torch.zeros(shape).cuda()
        self._features_rest_g = torch.cat((self._features_rest_g, new_features_rest_g), dim = 0)

        shape = list(self._features_rest_b.shape)
        shape[0] = num_added
        new_features_rest_b = torch.zeros(shape).cuda()
        self._features_rest_b = torch.cat((self._features_rest_b, new_features_rest_b), dim = 0)
        
        
    @staticmethod
    def normalize(tensor):
        tensor = tensor - tensor.mean()
        if tensor.std() > 0:
            tensor = tensor / tensor.std()
        return tensor

    def sort_into_grid(self, sorting_cfg, verbose):
        
        normalization_fn = self.normalize if sorting_cfg.normalize else lambda x: x
        attr_getter_fn = self.get_activated_attr_flat if sorting_cfg.activated else self.get_attr_flat
        
        params_to_sort = []
        
        for attr_name, attr_weight in sorting_cfg.weights.items():
            if attr_weight > 0:
                params_to_sort.append(normalization_fn(attr_getter_fn(attr_name)) * attr_weight)
                    
        params_to_sort = torch.cat(params_to_sort, dim=1)
        
        if sorting_cfg.shuffle:
            shuffled_indices = torch.randperm(params_to_sort.shape[0], device=params_to_sort.device)
            params_to_sort = params_to_sort[shuffled_indices]

        grid_to_sort = self.as_grid_img(params_to_sort).permute(2, 0, 1)
        _, sorted_indices = sort_with_plas(grid_to_sort, improvement_break=sorting_cfg.improvement_break, verbose=verbose)
        
        sorted_indices = sorted_indices.squeeze().flatten()
        
        if sorting_cfg.shuffle:
            sorted_indices = shuffled_indices[sorted_indices]
        
        # self.prune_all_but_these_indices(sorted_indices)
        return sorted_indices

    def as_grid_img(self, tensor):
        if not hasattr(self, "grid_sidelen"):
            raise "Gaussians not pruned yet!"

        if self.grid_sidelen * self.grid_sidelen != tensor.shape[0]:
            raise "Tensor shape does not match img sidelen, needs pruning?"

        img = tensor.reshape((self.grid_sidelen, self.grid_sidelen, -1))
        return img

    def attr_as_grid_img(self, attr_name):
        tensor = getattr(self, attr_name)
        return self.as_grid_img(tensor)

    def set_attr_from_grid_img(self, attr_name, img):

        if self.optimizer is not None:
            raise "Overwriting Gaussians during training not implemented yet! - Consider pruning method implementations"

        attr_shapes = {
            "_xyz": (3,),
            # "_features_dc": (1, 3),
            "_features_dc": (3,),
            "_features_rest_r": (3,),
            "_features_rest_g": (3,),
            "_features_rest_b": (3,),
            # "_features_rest": ((self.max_sh_degree + 1) ** 2 - 1, 3),
            "_rotation": (4,),
            "_scaling": (3,),
            "_opacity": (1,),
        }

        target_shape = attr_shapes[attr_name]
        img_shaped = img.reshape(-1, *target_shape)
        tensor = torch.tensor(img_shaped, dtype=torch.float, device="cuda")

        setattr(self, attr_name, tensor)

    def neighborloss_2d(self, tensor, neighbor_cfg, squeeze_dim=None):
        if neighbor_cfg.normalize:
            tensor = self.normalize(tensor)

        if squeeze_dim:
            tensor = tensor.squeeze(squeeze_dim)

        img = self.as_grid_img(tensor)
        img = img.permute(2, 0, 1).unsqueeze(0)

        blurred_x = kornia.filters.gaussian_blur2d(
            img.detach(),
            kernel_size=(1, neighbor_cfg.blur.kernel_size),
            sigma=(neighbor_cfg.blur.sigma, neighbor_cfg.blur.sigma),
            border_type="circular",
        )

        blurred_xy = kornia.filters.gaussian_blur2d(
            blurred_x,
            kernel_size=(neighbor_cfg.blur.kernel_size, 1),
            sigma=(neighbor_cfg.blur.sigma, neighbor_cfg.blur.sigma),
            border_type="reflect",
        )

        if neighbor_cfg.loss_fn == "mse":
            loss = F.mse_loss(blurred_xy, img)
        elif neighbor_cfg.loss_fn == "huber":
            loss = F.huber_loss(blurred_xy, img)
        else:
            assert False, "Unknown loss function"
        
        return loss
    
    def load_dg(self,params):
        self._xyz = params["means3D"]
        self._features_dc = params["colors_precomp"]
        self._scaling = params['scales']
        self._rotation = params['rotations']
        self._opacity = params['opacities']
        return
    
    def load_3dgstream(self, gau : GaussianDataCUDA):
        self._xyz = gau.xyz
        self._features_dc = gau.sh[:,0:1,:]
        self._features_rest_r = gau.sh[:,1:2,:]
        self._features_rest_g = gau.sh[:,2:3,:]
        self._features_rest_b = gau.sh[:,3:,:]
        self._features_rest = gau.sh[:,1:,:]
        self._scaling = gau.scale
        self._rotation = gau.rot
        self._opacity = gau.opacity

        self._opacity = inverse_sigmoid(self._opacity)
        self._scaling = torch.log(self._scaling)

        return
    
    def merge_features(self):
        self._features_rest_r = self._features_rest_r.unsqueeze(-2)
        self._features_rest_g = self._features_rest_g.unsqueeze(-2)
        self._features_rest_b = self._features_rest_b.unsqueeze(-2)
        self._features_rest = torch.cat((self._features_rest_r,self._features_rest_g,self._features_rest_b),dim=-2)
        self._features_dc = self._features_dc.unsqueeze(-2)