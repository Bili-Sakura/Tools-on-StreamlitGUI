import os
import subprocess


def mp4_to_mp3(input_path, output_path=None, bitrate="192k"):
    """Convert an MP4 file to MP3 using ffmpeg."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".mp3"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vn",
        "-ab",
        bitrate,
        "-ar",
        "44100",
        "-f",
        "mp3",
        output_path,
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e.stderr.decode())
        raise

    return output_path
