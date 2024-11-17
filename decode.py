import ffmpeg
import subprocess
def decode():
    # 创建 FFmpeg 解码命令
    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_opacity_l.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','gray',  # 保持帧同步
        'decoding/_opacity_l/_opacity_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    # 创建 FFmpeg 解码命令
    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_opacity_h.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','gray',  # 保持帧同步
        'decoding/_opacity_h/_opacity_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_rotation_l_rgb.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_rotation_l_rgb/_rotation_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_rotation_h_rgb.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_rotation_h_rgb/_rotation_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_rotation_l_a.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','gray',  # 保持帧同步
        'decoding/_rotation_l_a/_rotation_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_rotation_h_a.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','gray',  # 保持帧同步
        'decoding/_rotation_h_a/_rotation_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_xyz_l.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_xyz_l/_xyz_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_xyz_h.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_xyz_h/_xyz_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_scaling_l.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_scaling_l/_scaling_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_scaling_h.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_scaling_h/_scaling_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_dc_l.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_dc_l/_features_dc_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_dc_h.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_dc_h/_features_dc_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_rest_r_h.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_rest_r_h/_features_rest_r_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_rest_r_l.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_rest_r_l/_features_rest_r_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_rest_g_h.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_rest_g_h/_features_rest_g_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_rest_g_l.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_rest_g_l/_features_rest_g_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_rest_b_h.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_rest_b_h/_features_rest_b_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    ffmpeg_command = [
        'ffmpeg', '-i', 'coding/_features_rest_b_l.mp4',     # 输入 H.264 视频文件
        '-vsync', '0',
        '-pix_fmt','rgb24',  # 保持帧同步
        'decoding/_features_rest_b_l/_features_rest_b_%03d.png'                 # 输出图片序列，如 'image_%03d.png'
    ]

    # 运行 FFmpeg 命令
    subprocess.run(ffmpeg_command)

    print('图片已解码')

if __name__ == "__main__":
    decode()
