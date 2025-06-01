import os
import subprocess
import uuid
import shutil
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer
from azure.cognitiveservices.speech.audio import AudioOutputConfig
import azure.cognitiveservices.speech as speechsdk

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

def text_to_talking_head(text,
                         output_path=None,
                         face_image="D:/proj/Wav2Lip-master/examples/driven_video/1.png",
                         audio_path=None,
                         checkpoint_path="D:/proj/Wav2Lip-master/checkpoints/wav2lip_gan.pth",
                         wav2lip_dir="D:/proj/Wav2Lip-master/",  # 添加Wav2Lip目录参数
                         speech_lang="zh-CN",
                         voice_name="zh-cn-XiaochenNeural"):
    """
    将文本转换为口型同步的说话头视频

    参数:
        text (str): 要转换为语音的文本
        output_path (str): 输出视频的路径
        face_image (str): 面部图像的路径
        audio_path (str): 中间音频文件的保存路径
        checkpoint_path (str): Wav2Lip模型检查点路径
        wav2lip_dir (str): Wav2Lip项目目录
        speech_lang (str): 语音合成的语言
        voice_name (str): 语音合成的声音

    返回:
        bool: 是否成功
    """
    try:
        # 设置Azure语音服务
        speech_key, service_region = "CmwzTb35WSvnOYEPoY9wC12ExtiNJkI37VJlc9itceLmM6osBYstJQQJ99BAACYeBjFXJ3w3AAAYACOG1fhO", "eastus"
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

        # 设置语言和声音
        speech_config.speech_synthesis_language = speech_lang
        speech_config.speech_synthesis_voice_name = voice_name

        # 生成音频文件路径
        if not audio_path:
            audio_path = os.path.join("instance", "temp_audio", f"question_{uuid.uuid4()}.wav")

        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(audio_path)), exist_ok=True)

        # 生成语音
        audio_config = AudioOutputConfig(filename=audio_path)
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        print(f"正在生成语音: '{text}'")
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("语音生成成功")
            stream = AudioDataStream(result)
            stream.save_to_wav_file(audio_path)
            print(f"音频文件已保存: {os.path.abspath(audio_path)}")

            # 检查音频文件是否存在
            if os.path.exists(audio_path):
                print(f"音频文件已存在: {os.path.abspath(audio_path)}")
            else:
                print(f"音频文件未找到: {os.path.abspath(audio_path)}")
                return False

            # 确保输出目录存在
            if not output_path:
                output_path = os.path.join("static", "generated_videos", "questions", f"question_{uuid.uuid4()}.mp4")

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # 构建Wav2Lip命令
            inference_script = os.path.join(wav2lip_dir, "inference.py")
            command = [
                "python",
                inference_script,  # 使用完整路径
                "--checkpoint_path", checkpoint_path,
                "--face", face_image,
                "--audio", os.path.abspath(audio_path),  # 使用绝对路径
                "--outfile", os.path.abspath(output_path)  # 使用绝对路径
            ]
            print(f"Executing command: {' '.join(command)}")

            # 执行口型同步生成
            print("正在生成说话头视频...")

            # 重要: 设置工作目录为Wav2Lip项目目录
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=wav2lip_dir  # 设置工作目录
            )

            # 手动读取输出并处理编码
            stdout_data, stderr_data = process.communicate()

            # 尝试使用utf-8解码，如果失败则使用errors='replace'选项
            try:
                stdout = stdout_data.decode('utf-8')
            except UnicodeDecodeError:
                stdout = stdout_data.decode('utf-8', errors='replace')

            try:
                stderr = stderr_data.decode('utf-8')
            except UnicodeDecodeError:
                stderr = stderr_data.decode('utf-8', errors='replace')

            if process.returncode == 0:
                print("视频生成成功！")
                print(stdout)
                original_video_path = output_path

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
                        shutil.move(original_video_path, backup_path)  # 使用 move 实现重命名备份
                        logging.info(f"原始文件已备份到: {backup_path}")

                        # 2. 将重新编码好的临时文件移动到原始文件位置
                        shutil.move(reencoded_temp_path, original_video_path)
                        logging.info(f"重新编码后的文件已替换原始文件: {original_video_path}")
                        print("-" * 30)
                        print("操作成功完成！")
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

                return True
            else:
                print(f"命令执行失败，返回码: {process.returncode}")
                print(f"错误输出: {stderr}")
                return False
        else:
            print(f"语音合成失败: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"语音合成失败，原因: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"错误详细信息: {cancellation_details.error_details}")
            return False

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return False


# 使用示例
if __name__ == "__main__":
    question = "请列举并解释二叉树的主要性质。"
    success = text_to_talking_head(
        question,
        wav2lip_dir="D:/proj/Wav2Lip-master/"  # 指定Wav2Lip目录
    )
