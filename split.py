import os
import cv2
import numpy as np

def split():
    # 输入和输出文件夹路径
    input_folder = ['coding/_rotation','coding/_xyz','coding/_scaling','coding/_opacity','coding/_features_dc','coding/_features_rest_r','coding/_features_rest_g','coding/_features_rest_b']
    output_folder_l = ['coding/_rotation_l','coding/_xyz_l','coding/_scaling_l','coding/_opacity_l','coding/_features_dc_l','coding/_features_rest_r_l','coding/_features_rest_g_l','coding/_features_rest_b_l']
    output_folder_h = ['coding/_rotation_h','coding/_xyz_h','coding/_scaling_h','coding/_opacity_h','coding/_features_dc_h','coding/_features_rest_r_h','coding/_features_rest_g_h','coding/_features_rest_b_h']

    # 创建输出文件夹（如果不存在）
    for i in range(len(output_folder_h)):
        os.makedirs(output_folder_l[i], exist_ok=True)
        os.makedirs(output_folder_h[i], exist_ok=True)

    for i in range(len(input_folder)):
        # 遍历输入文件夹中的所有 PNG 文件
        for filename in os.listdir(input_folder[i]):
            if filename.endswith('.png'):  # 仅处理 PNG 文件
                # 加载 RGBA 图像
                input_image_path = os.path.join(input_folder[i], filename)
                input_image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)

                high_8bit = (input_image >> 8).astype(np.uint8)  # 高 8 位
                low_8bit = (input_image & 0xFF).astype(np.uint8)  # 低 8 位

                cv2.imwrite(os.path.join(output_folder_h[i],filename), high_8bit)
                cv2.imwrite(os.path.join(output_folder_l[i],filename), low_8bit)
            


    input_folder = ['coding/_rotation_l','coding/_rotation_h']
    output_folder_rgb = ['coding/_rotation_l_rgb','coding/_rotation_h_rgb']
    output_folder_a = ['coding/_rotation_l_a','coding/_rotation_h_a']

    for i in range(len(output_folder_rgb)):
        os.makedirs(output_folder_rgb[i], exist_ok=True)
        os.makedirs(output_folder_a[i], exist_ok=True)

    for i in range(len(input_folder)):
        # 遍历输入文件夹中的所有 PNG 文件
        for filename in os.listdir(input_folder[i]):
            if filename.endswith('.png'):  # 仅处理 PNG 文件
                # 加载 RGBA 图像
                input_image_path = os.path.join(input_folder[i], filename)
                input_image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)

                # 分解通道
                b, g, r, a = cv2.split(input_image)

                # 创建 RGB 图像
                rgb_image = cv2.merge((b, g, r))

                # 将 Alpha 通道保存为灰度图像
                alpha_image = a  # 转换为灰度模式（L）

                # 构建输出文件名
                rgb_output_path = os.path.join(output_folder_rgb[i], filename)
                alpha_output_path = os.path.join(output_folder_a[i], filename)

                # 保存 RGB 图像和 Alpha 灰度图像
                cv2.imwrite(rgb_output_path, rgb_image)
                cv2.imwrite(alpha_output_path, alpha_image)

            # print(f"处理完成：{filename}")

    print("所有图像已拆分完成。")

if __name__ == "__main__":
    split()