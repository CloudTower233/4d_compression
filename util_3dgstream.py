import numpy as np
import tinycudann as tcnn
import torch
import json
import os
from plyfile import PlyData, PlyElement
from NTC import NeuralTransformationCache
from renderer_cuda import GaussianDataCUDA, gaus_cuda_from_cpu
from util_gau import load_ply
@torch.no_grad()
def inverse_sigmoid(x):
    return torch.log(x/(1-x))

def construct_list_of_attributes(gau_cuda:GaussianDataCUDA):
    l = ['x', 'y', 'z', 'nx', 'ny', 'nz']
    # All channels except the 3 DC
    for i in range(1*3):
        l.append('f_dc_{}'.format(i))
    #TODO: SH > 1
    for i in range((gau_cuda.sh_dim-1)*3):
        l.append('f_rest_{}'.format(i))
    l.append('opacity')
    for i in range(gau_cuda.scale.shape[1]):
        l.append('scale_{}'.format(i))
    for i in range(gau_cuda.rot.shape[1]):
        l.append('rot_{}'.format(i))
    return l
    
def load_NTCs(FVV_path, gau_cuda:GaussianDataCUDA, total_frames:int = 150):
    NTC_paths=[os.path.join(FVV_path, 'NTCs', f'NTC_{frame_id:06}.pth') for frame_id in range(0, total_frames-1)]
    config_path=os.path.join(FVV_path, 'NTCs', 'config.json')
    xyz_bound = gau_cuda.get_xyz_bound()
    with open(config_path) as f:
        NTC_conf = json.load(f)
    models=[tcnn.NetworkWithInputEncoding(n_input_dims=3, n_output_dims=8, encoding_config=NTC_conf["encoding"], network_config=NTC_conf["network"]).to(torch.device("cuda")) for path in NTC_paths]
    NTCs=[NeuralTransformationCache(model,xyz_bound[0],xyz_bound[1]) for model in models]
    for frame_id, ntc in enumerate(NTCs):
        ntc.load_state_dict(torch.load(NTC_paths[frame_id]))
    return NTCs

def load_Additions(FVV_path, total_frames:int = 150):
    addition_paths=[os.path.join(FVV_path, 'additional_3dgs', f'additions_{frame_id:06}.ply') for frame_id in range(0, total_frames-1)]
    additions_gaus=[load_ply(path) for path in addition_paths]
    additions_gaus_cuda=[gaus_cuda_from_cpu(gaus) for gaus in additions_gaus]
    return additions_gaus_cuda

def get_per_frame_3dgs(FVV_path, gau_cuda:GaussianDataCUDA, total_frames:int = 150):
    raise NotImplementedError("This function is not implemented yet")

def save_gau_cuda(gau_cuda:GaussianDataCUDA, path:str):
    xyz = gau_cuda.xyz.cpu().numpy()
    rotation = gau_cuda.rot.cpu().numpy()
    normals = np.zeros_like(xyz)
    f_dc = gau_cuda.sh[:,0:1,:].transpose(1, 2).flatten(start_dim=1).contiguous().cpu().numpy()
    f_rest = gau_cuda.sh[:,1:,:].transpose(1, 2).flatten(start_dim=1).contiguous().cpu().numpy()
    opacities = inverse_sigmoid(gau_cuda.opacity).cpu().numpy()
    scale = torch.log(gau_cuda.scale).cpu().numpy()
    dtype_full = [(attribute, 'f4') for attribute in construct_list_of_attributes(gau_cuda)]  
    elements = np.empty(xyz.shape[0], dtype=dtype_full)
    attributes = np.concatenate((xyz, normals, f_dc, f_rest, opacities, scale, rotation), axis=1)
    elements[:] = list(map(tuple, attributes))
    el = PlyElement.describe(elements, 'vertex')
    PlyData([el]).write(path)