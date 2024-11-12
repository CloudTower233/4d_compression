import torch
import os
import numpy as np
import hydra

from omegaconf import DictConfig, OmegaConf
from scene import Scene, GaussianModel
from compression.compression_exp import run_compressions, run_decompressions
from compression.decompress import decompress_all_to_ply
from postprocess import postprocess
from collections import defaultdict
import util_gau
import util_3dgstream
from renderer_ogl import OpenGLRenderer, GaussianRenderBase
from renderer_cuda import CUDARenderer

BACKEND_OGL=0
g_total_frame = 300
g_renderer_list = [
    None, # ogl
]
g_renderer_idx = BACKEND_OGL
g_renderer = g_renderer_list[g_renderer_idx]


@hydra.main(version_base=None, config_path='config', config_name='training')
def main(cfg: DictConfig):
    g_renderer = CUDARenderer(800, 600)

    gau = util_gau.load_ply("D:\Raytracing\\4d_compression\data\\flame_steak\\init_3dgs.ply")
    g_renderer.update_gaussian_data(gau)

    g_FVV_path = os.path.join("data","flame_steak")
    g_renderer.NTCs = util_3dgstream.load_NTCs(g_FVV_path, g_renderer.gaussians, g_total_frame)
    g_renderer.additional_3dgs = util_3dgstream.load_Additions(g_FVV_path, g_total_frame)

    sorted_indices = []
    for timestep in range(g_total_frame):
        print("\n[Frame {}] Compressing Gaussians".format(timestep))
        compr_path = os.path.join("output", "compression", f"frame_{timestep}")
        while(timestep - g_renderer.current_timestep > 0):
            g_renderer.query_NTC(g_renderer.gaussians.xyz,g_renderer.current_timestep)
            g_renderer.current_timestep+=1
        # if g_renderer.current_timestep!=0:
        #     rendered_gaussians = g_renderer.cat_additions(g_renderer.current_timestep-1)
        # else :
        rendered_gaussians = g_renderer.gaussians

        frame_gaussians = GaussianModel(1,True)
        frame_gaussians.load_3dgstream(rendered_gaussians)

        frame_gaussians.prune_to_square_shape()
        if timestep == 0:
            sorted_indices = frame_gaussians.sort_into_grid(cfg.sorting, not cfg.run.no_progress_bar)
        else:
            frame_gaussians.prune_all_but_these_indices(sorted_indices)

        compr_results = run_compressions(frame_gaussians, compr_path, OmegaConf.to_container(cfg.compression))
        

    print("\nTraining complete.")

if __name__ == "__main__":
    main()


