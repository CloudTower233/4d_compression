import shutil
import sys
import os
import yaml
import pandas as pd
import torch
import numpy as np

from argparse import ArgumentParser
from gaussian_renderer import GaussianModel
from compression.compression_exp import decompress_attr


def run_single_decompression(compressed_dir, iter):

    compr_info = pd.read_csv(os.path.join(compressed_dir, "compression_info.csv"), index_col=0)

    with open(os.path.join(compressed_dir, "compression_config.yml"), 'r') as stream:
        experiment_config = yaml.safe_load(stream)

    decompressed_gaussians = GaussianModel(experiment_config['max_sh_degree'], experiment_config['disable_xyz_log_activation'])
    decompressed_gaussians.active_sh_degree = experiment_config['active_sh_degree']

    for attribute in experiment_config['attributes']:
        attr_name = attribute["name"]
        # compressed_bytes = compressed_attrs[attr_name]
        # compressed_file = os.path.join(compressed_dir, compr_info.loc[attr_name, "file"])
        compressed_file = os.path.join("decoding",attr_name,attr_name + f"_{iter+1:03}.png")

        decompress_attr(decompressed_gaussians, attribute, compressed_file, compr_info.loc[attr_name, "min"], compr_info.loc[attr_name, "max"])

    return decompressed_gaussians

def decompress():
    model_path = "decoding"
    origin_model_path = os.path.join("output","compression")
    scene_data = []
    for t in range(150):
        csv_path = os.path.join(origin_model_path,f"iteration_{t}","PNG 16")
        decompressed_gaussians = run_single_decompression(csv_path,t)
        # params
        rendervar = {
            'means3D': decompressed_gaussians._xyz,
            'colors_precomp': decompressed_gaussians._features_dc,
            'rotations': decompressed_gaussians._rotation,
            'opacities': decompressed_gaussians._opacity,
            'scales': decompressed_gaussians._scaling,
        }
        scene_data.append(params2cpu(rendervar))
    # save
    save_params(scene_data)
    print('参数解码完成')

def params2cpu(params):
    res = {k: v.detach().cpu().contiguous().numpy() for k, v in params.items()}
    
    return res

def save_params(output_params):
    to_save = {}
    for k in output_params[0].keys():
        if k in output_params[1].keys():
            to_save[k] = np.stack([params[k] for params in output_params])
        else:
            to_save[k] = output_params[0][k]
    np.savez(f"./output/rendervar", **to_save)

if __name__ == "__main__":
    decompress()
