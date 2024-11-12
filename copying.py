import cv2
import os
import imagecodecs
import numpy as np
import shutil

def copy_images():
    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_xyz.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        os.makedirs(os.path.join("coding","_xyz"), exist_ok=True)
        output_path = os.path.join("coding","_xyz",f"_xyz_{t:03d}.png")
        t=t+1
        cv2.imwrite(output_path,image)

    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_scaling.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        output_path = os.path.join("coding","_scaling",f"_scaling_{t:03d}.png")
        os.makedirs(os.path.join("coding","_scaling"), exist_ok=True)
        t=t+1
        cv2.imwrite(output_path,image)

    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_rotation.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        output_path = os.path.join("coding","_rotation",f"_rotation_{t:03d}.png")
        os.makedirs(os.path.join("coding","_rotation"), exist_ok=True)
        t=t+1
        cv2.imwrite(output_path,image)

    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_opacity.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        output_path = os.path.join("coding","_opacity",f"_opacity_{t:03d}.png")
        os.makedirs(os.path.join("coding","_opacity"), exist_ok=True)
        t=t+1
        cv2.imwrite(output_path,image)

    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_features_dc.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        output_path = os.path.join("coding","_features_dc",f"_features_dc_{t:03d}.png")
        os.makedirs(os.path.join("coding","_features_dc"), exist_ok=True)
        t=t+1
        cv2.imwrite(output_path,image)

    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_features_rest_r.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        output_path = os.path.join("coding","_features_rest_r",f"_features_rest_r_{t:03d}.png")
        os.makedirs(os.path.join("coding","_features_rest_r"), exist_ok=True)
        t=t+1
        cv2.imwrite(output_path,image)

    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_features_rest_g.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        output_path = os.path.join("coding","_features_rest_g",f"_features_rest_g_{t:03d}.png")
        os.makedirs(os.path.join("coding","_features_rest_g"), exist_ok=True)
        t=t+1
        cv2.imwrite(output_path,image)

    # 设置输入路径和输出文件名
    input_path = os.path.join("output","compression")
    # output_file = '_features_dc.mp4'
    # 获取输入路径下所有图像文件
    image_files = []
    for t in range(300):
        compr_path = os.path.join(input_path,f"frame_{t}","PNG 16")
        image_files.append(os.path.join(compr_path,"_features_rest_b.png"))

    t = 0
    for image_path in image_files:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        output_path = os.path.join("coding","_features_rest_b",f"_features_rest_b_{t:03d}.png")
        os.makedirs(os.path.join("coding","_features_rest_b"), exist_ok=True)
        t=t+1
        cv2.imwrite(output_path,image)

    print('图片已复制完成')

def copy_csv():
    origin_model_path = os.path.join("output","compression")
    config_path = os.path.join(origin_model_path,"frame_0","PNG 16")
    config_path = os.path.join(config_path,"compression_config.yml")
    output_path = os.path.join("coding","config","compression_config.yml")
    os.makedirs(os.path.join("coding","config"), exist_ok=True)
    shutil.copy(config_path, output_path)

    for t in range(300):
        csv_path = os.path.join(origin_model_path,f"frame_{t}","PNG 16")
        csv_path = os.path.join(csv_path, "compression_info.csv")
        output_path = os.path.join("coding","config",f"compression_info_{t}.csv")
        os.makedirs(os.path.join("coding","config"), exist_ok=True)
        shutil.copy(csv_path, output_path)

    print("参数文件已复制完成")


if __name__ == "__main__":
    copy_images()
    copy_csv()