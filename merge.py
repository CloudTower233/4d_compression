import os
import numpy as np
import cv2

def merge():
    # 输入和输出文件夹路径
    output_folder = ['decoding/_xyz','decoding/_scaling','decoding/_opacity','decoding/_features_dc','decoding/_rotation_rgb','decoding/_rotation_a']
    input_folder_l = ['decoding/_xyz_l','decoding/_scaling_l','decoding/_opacity_l','decoding/_features_dc_l','decoding/_rotation_l_rgb','decoding/_rotation_l_a']
    input_folder_h = ['decoding/_xyz_h','decoding/_scaling_h','decoding/_opacity_h','decoding/_features_dc_h','decoding/_rotation_h_rgb','decoding/_rotation_h_a']


    for i in range(len(input_folder_l)):
        # 遍历输入文件夹中的所有 PNG 文件
        for filename in os.listdir(input_folder_l[i]):
            if filename.endswith('.png'):  # 仅处理 PNG 文件
                # 加载 RGBA 图像
                input_image_path = os.path.join(input_folder_l[i], filename)
                input_image_l = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
                input_image_path = os.path.join(input_folder_h[i], filename)
                input_image_h = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)

                image = (input_image_h.astype(np.uint16) << 8) | input_image_l.astype(np.uint16)
                # 构建输出文件名
                output_path = os.path.join(output_folder[i], filename)

                # 保存 RGB 图像和 Alpha 灰度图像
                cv2.imwrite(output_path, image)
                # print(f"处理完成：{filename}")

    print("16bit合成已处理完成。")

    output_folder = 'decoding/_rotation'
    input_folder_rgb = 'decoding/_rotation_rgb'
    input_folder_a = 'decoding/_rotation_a'

    # 遍历输入文件夹中的所有 PNG 文件
    for filename in os.listdir(input_folder_rgb):
        if filename.endswith('.png'):  # 仅处理 PNG 文件
            input_image_path = os.path.join(input_folder_rgb, filename)
            input_image_rgb = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
            input_image_path = os.path.join(input_folder_a, filename)
            input_image_a = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)

            # 创建一个空的 RGBA 图像
            rgba_image = np.zeros((input_image_rgb.shape[0], input_image_rgb.shape[1], 4), dtype=np.uint16)

            # 将 RGB 图像的颜色通道复制到 RGBA 图像
            rgba_image[:, :, 0:3] = input_image_rgb  # 将 R, G, B 通道赋值

            # 将灰度图像作为 Alpha 通道
            rgba_image[:, :, 3] = input_image_a  # 将 Alpha 通道赋值

            # 保存 RGBA 图像
            cv2.imwrite(os.path.join(output_folder,filename), rgba_image)

    print("旋转已合成完成。")
    print("图像合并已完成。")

if __name__ == "__main__":
    merge()
