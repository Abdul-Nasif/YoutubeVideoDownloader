# app/services/ffmpeg_android.py
from jnius import autoclass
import os

# The wrapper class provided by the FFmpeg-Kit-Python project
FFMPEG = autoclass('com.sahib.pyff.ffpy')

def run_ffmpeg_command(command):
    """
    Executes an FFmpeg command on Android using the bundled FFmpegKit.
    
    :param command: A string of the FFmpeg command to run (e.g., "-i input.mp4 output.mp3").
    :return: The output of the command as a string, or None on failure.
    """
    try:
        # The .Run() method executes the command and returns the output
        output = FFMPEG.Run(command)
        print(f"FFmpeg command executed successfully. Output: {output}")
        return output
    except Exception as e:
        print(f"Error executing FFmpeg command via FFmpegKit: {e}")
        return None

# Example usage:
# if __name__ == "__main__":
#     output_file = os.path.join(os.path.expanduser("~"), "test.mp3")
#     command = f"-i /path/to/your/video.mp4 -vn -acodec libmp3lame -q:a 2 {output_file}"
#     result = run_ffmpeg_command(command)
#     if result:
#         print(f"Successfully created {output_file}")