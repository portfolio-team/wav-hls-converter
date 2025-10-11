#!/usr/bin/env python3
import os
import sys
import tempfile
import subprocess
import boto3
from urllib.parse import urljoin
from dotenv import load_dotenv

# --- .env 読み込み ---
load_dotenv()

R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

if not all([R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_ENDPOINT]):
    print("[ERROR] Missing R2 configuration. Please check your .env file.")
    sys.exit(1)


def convert_to_hls(input_wav: str, output_dir: str):
    """WAVをHLS形式に変換"""
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i", input_wav,
        "-codec:a", "aac",
        "-b:a", "128k",
        "-f", "hls",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_segment_type", "fmp4",
        os.path.join(output_dir, "index.m3u8"),
    ]

    print(f"[INFO] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] FFmpeg failed:", result.stderr)
        sys.exit(1)

    print("[INFO] HLS conversion completed.")


def upload_to_r2(local_dir: str, object_prefix: str):
    """Cloudflare R2 にHLSファイル群をアップロード"""
    s3 = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )

    print(f"[INFO] Uploading files to R2: bucket={R2_BUCKET_NAME}, prefix={object_prefix}")
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, local_dir)
            key = f"{object_prefix}/{rel_path}"

            s3.upload_file(local_path, R2_BUCKET_NAME, key)
            print(f"[UPLOAD] {key}")

    m3u8_url = urljoin(f"{R2_ENDPOINT}/{R2_BUCKET_NAME}/", f"{object_prefix}/index.m3u8")
    print("[INFO] Upload complete.")
    return m3u8_url


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_wav_path>")
        print("Example: python main.py ./input/song.wav")
        sys.exit(1)

    input_wav = sys.argv[1]
    if not os.path.exists(input_wav):
        print(f"[ERROR] Input file not found: {input_wav}")
        sys.exit(1)

    # ファイル名をベースにR2上のディレクトリを決定
    filename = os.path.splitext(os.path.basename(input_wav))[0]
    object_prefix = f"audio/{filename}"

    with tempfile.TemporaryDirectory() as tmpdir:
        convert_to_hls(input_wav, tmpdir)
        hls_url = upload_to_r2(tmpdir, object_prefix)
        print(f"[SUCCESS] HLS uploaded: {hls_url}")


if __name__ == "__main__":
    main()
