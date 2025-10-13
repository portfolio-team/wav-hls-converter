#!/usr/bin/env python3
import os
import sys
import tempfile
from utils.r2 import upload_to_r2
from utils.hls_convert import cmd_to_aac_hls, cmd_to_uncomp_hls, excecute_convert
from config import Config


def main():
    config = Config()

    if len(sys.argv) != 3:
        print("Usage: python main.py <input_wav_path> --comp | --uncomp")
        print("Example: python main.py ./input/song.wav --uncomp")
        sys.exit(1)

    input_wav = sys.argv[1]
    if not os.path.exists(input_wav):
        print(f"[ERROR] Input file not found: {input_wav}")
        sys.exit(1)

    comp_option = sys.argv[2]
    if comp_option not in ["--comp", "--uncomp"]:
        print("[ERROR] comp option must be --comp or --uncomp")
        sys.exit(1)

    # ファイル名をベースにR2上のディレクトリを決定
    filename = os.path.splitext(os.path.basename(input_wav))[0]
    object_prefix = f"audio/{filename}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # 非圧縮と圧縮を選択可能
        if comp_option == "--uncomp":
            print("[INFO] Converting to uncompressed HLS...")
            cmd = cmd_to_uncomp_hls(input_wav, tmpdir)
        else:
            print("[INFO] Converting to compressed HLS...")
            cmd = cmd_to_aac_hls(input_wav, tmpdir)
        excecute_convert(cmd, tmpdir)
        hls_url = upload_to_r2(tmpdir, object_prefix, config)
        print(f"[SUCCESS] HLS uploaded: {hls_url}")


if __name__ == "__main__":
    main()
