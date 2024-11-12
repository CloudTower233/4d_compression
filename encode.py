import ffmpeg
import os
import subprocess

def encode_images_to_h265():
     # 创建 FFmpeg 命令行
    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_opacity_l/_opacity_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gray',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_opacity_l.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_opacity_h/_opacity_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gray',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_opacity_h.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_rotation_l_rgb/_rotation_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_rotation_l_rgb.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_rotation_h_rgb/_rotation_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_rotation_h_rgb.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_rotation_l_a/_rotation_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gray',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_rotation_l_a.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_rotation_h_a/_rotation_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gray',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_rotation_h_a.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)


    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_xyz_l/_xyz_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_xyz_l.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_xyz_h/_xyz_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_xyz_h.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_scaling_l/_scaling_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_scaling_l.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_scaling_h/_scaling_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_scaling_h.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_dc_l/_features_dc_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_dc_l.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_dc_h/_features_dc_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_dc_h.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_rest_r_l/_features_rest_r_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_rest_r_l.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_rest_r_h/_features_rest_r_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_rest_r_h.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_rest_g_l/_features_rest_g_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_rest_g_l.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_rest_g_h/_features_rest_g_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_rest_g_h.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_rest_b_l/_features_rest_b_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_rest_b_l.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-framerate', '1',  # 设置帧率
        '-i', 'coding/_features_rest_b_h/_features_rest_b_%03d.png',         # 输入图片序列（如 'image_%03d.png'）
        '-c:v', 'libx265',            # 使用 H.264 编码器
        '-preset', 'veryslow',        # 使用 'veryslow' 预设，压缩效果最好
        '-x265-params', 'lossless=1',                   # 设置量化参数为 0，保证无损
        '-pix_fmt', 'gbrp',        # 使用 YUV 4:4:4 格式，保留所有颜色信息
        'coding/_features_rest_b_h.mp4'                   # 输出文件名
    ]
    
    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    print('图片已通过h265编码完成')

if __name__ == "__main__":
    # 示例调用
    encode_images_to_h265()

