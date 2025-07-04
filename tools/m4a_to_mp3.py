import os
import sys
import subprocess

def m4a_to_mp3(input_path, output_path=None, bitrate="192k"):
    """
    Convert an M4A file to MP3 using ffmpeg.

    Args:
        input_path (str): Path to the input .m4a file.
        output_path (str, optional): Path to the output .mp3 file. If None, replaces extension.
        bitrate (str, optional): Bitrate for the output mp3. Default is '192k'.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".mp3"

    command = [
        "ffmpeg",
        "-y",  # Overwrite output files without asking
        "-i", input_path,
        "-vn",  # No video
        "-ab", bitrate,
        "-ar", "44100",
        "-f", "mp3",
        output_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e.stderr.decode())
        raise

    return output_path
