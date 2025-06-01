import subprocess
import os
import logging
import shutil # 用于文件备份

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reencode_video_for_web(input_path, output_path, ffmpeg_path="ffmpeg"):
    """
    使用 ffmpeg 重新编码视频，优化用于 Web 播放 (H.264, AAC, faststart)。

    Args:
        input_path (str): 原始视频文件的完整路径。
        output_path (str): 重新编码后视频文件的保存路径。
        ffmpeg_path (str): ffmpeg 可执行文件的路径 (如果不在系统 PATH 中)。

    Returns:
        bool: 如果成功完成则返回 True，否则返回 False。
    """
    if not os.path.exists(input_path):
        logging.error(f"输入文件未找到: {input_path}")
        return False

    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 构建 ffmpeg 命令参数列表
    command = [
        ffmpeg_path,
        '-i', input_path,
        '-c:v', 'libopenh264',
        # --- 移除 profile 和 level ---
        # '-profile:v', 'baseline',
        # '-level', '3.0',
        # ---------------------------
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        output_path
    ]

    logging.info(f"开始重新编码: {' '.join(command)}") # 打印将要执行的命令

    try:
        # 执行 ffmpeg 命令
        # text=True (Python 3.7+) 用于自动解码 stdout/stderr 为字符串
        # check=False 表示即使 ffmpeg 返回非零退出码也不会抛出异常，我们手动检查
        result = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

        # 检查 ffmpeg 是否成功执行 (返回码为 0)
        if result.returncode == 0:
            logging.info(f"成功将 '{input_path}' 重新编码到 '{output_path}'")
            # 检查输出文件是否存在且大于0字节
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True
            else:
                logging.error(f"ffmpeg 返回成功，但输出文件 '{output_path}' 未找到或为空。")
                logging.error(f"ffmpeg stdout:\n{result.stdout}")
                logging.error(f"ffmpeg stderr:\n{result.stderr}") # 查看stderr可能有线索
                return False
        else:
            # ffmpeg 执行失败，记录错误
            logging.error(f"ffmpeg 重新编码失败，返回码: {result.returncode}")
            logging.error(f"ffmpeg stdout:\n{result.stdout}")
            logging.error(f"ffmpeg stderr:\n{result.stderr}") # stderr 通常包含具体的错误信息
            # 尝试删除可能产生的无效输出文件
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass # 忽略删除错误
            return False

    except FileNotFoundError:
        logging.error(f"错误: ffmpeg 命令 '{ffmpeg_path}' 未找到。请确保 ffmpeg 已安装并在系统 PATH 中，或者提供了正确的路径。")
        return False
    except Exception as e:
        logging.error(f"执行 ffmpeg 时发生意外错误: {e}")
        return False

# --- 如何使用这个函数 ---
if __name__ == "__main__":
    # --- 配置区 ---
    # !! 重要：请将下面的路径修改为你服务器上的实际路径 !!
    original_video_path = "static/generated_videos/courses/1/questions/question_2.mp4"

    # 定义重新编码后的临时文件路径
    reencoded_temp_path = original_video_path + ".reencoded_temp.mp4"

    # 定义原始文件的备份路径
    backup_path = original_video_path + ".backup"

    # --- 执行重新编码 ---
    logging.info(f"准备重新编码视频: {original_video_path}")
    success = reencode_video_for_web(original_video_path, reencoded_temp_path)

    if success:
        logging.info("视频重新编码成功。现在进行备份和替换...")
        try:
            # 1. 备份原始文件 (如果备份文件已存在则先删除)
            if os.path.exists(backup_path):
                logging.warning(f"备份文件已存在，将覆盖: {backup_path}")
                os.remove(backup_path)
            shutil.move(original_video_path, backup_path) # 使用 move 实现重命名备份
            logging.info(f"原始文件已备份到: {backup_path}")

            # 2. 将重新编码好的临时文件移动到原始文件位置
            shutil.move(reencoded_temp_path, original_video_path)
            logging.info(f"重新编码后的文件已替换原始文件: {original_video_path}")
            print("-" * 30)
            print(f"操作成功完成！请清除浏览器缓存后，重新测试播放视频：{original_video_path}")
            print("-" * 30)

        except Exception as e:
            logging.error(f"在备份或替换文件时发生错误: {e}")
            logging.error("请检查文件权限和路径。可能需要手动恢复或替换文件。")
            # 尝试恢复原始文件（如果临时文件还在）
            if os.path.exists(backup_path) and not os.path.exists(original_video_path):
                 try:
                     shutil.move(backup_path, original_video_path)
                     logging.info("已尝试从备份恢复原始文件。")
                 except Exception as move_back_err:
                     logging.error(f"尝试恢复原始文件失败: {move_back_err}")
            # 清理可能残留的临时文件
            if os.path.exists(reencoded_temp_path):
                 try:
                     os.remove(reencoded_temp_path)
                 except OSError:
                     pass


    else:
        logging.error("视频重新编码失败。原始文件保持不变。")
        # 清理可能残留的临时文件
        if os.path.exists(reencoded_temp_path):
             try:
                 os.remove(reencoded_temp_path)
             except OSError:
                 pass
        print("-" * 30)
        print("操作失败。请检查上面的日志输出获取详细错误信息。")
        print("-" * 30)

