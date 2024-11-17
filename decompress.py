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


def run_single_decompression(csv_dir, iter):

    compr_info = pd.read_csv(os.path.join(csv_dir, f"compression_info_{iter}.csv"), index_col=0)

    with open(os.path.join(csv_dir, f"compression_config.yml"), 'r') as stream:
        experiment_config = yaml.safe_load(stream)

    decompressed_gaussians = GaussianModel(experiment_config['max_sh_degree'], experiment_config['disable_xyz_log_activation'])
    decompressed_gaussians.active_sh_degree = experiment_config['active_sh_degree']

    for attribute in experiment_config['attributes']:
        attr_name = attribute["name"]
        # compressed_bytes = compressed_attrs[attr_name]
        # compressed_file = os.path.join(compressed_dir, compr_info.loc[attr_name, "file"])
        compressed_file = os.path.join("coding",attr_name,attr_name + f"_{iter:03}.png")

        decompress_attr(decompressed_gaussians, attribute, compressed_file, compr_info.loc[attr_name, "min"], compr_info.loc[attr_name, "max"])
    # num_prune = experiment_config['extra_gaussians']

    # decompressed_gaussians.prune_to_origin(num_prune)

    return decompressed_gaussians

def decompress():
    model_path = "decoding"
    origin_model_path = os.path.join("output","compression")
    scene_data = []
    
    for t in range(300):
        print(f"frame {t}")
        csv_path = os.path.join("coding","config")
        decompressed_gaussians = run_single_decompression(csv_path,t)
        output_path = os.path.join("output","decompress",f"frame_{t}.ply")
        decompressed_gaussians.merge_features()
        decompressed_gaussians.save_ply(output_path)
    # save
    print('参数解码完成')


if __name__ == "__main__":
    decompress()
