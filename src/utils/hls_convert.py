import os
import sys
import subprocess
import wave


def cmd_to_aac_hls(input_wav: str, output_dir: str) -> list:
    """WAVをAAC圧縮フォーマットでHLS形式に変換"""
    """HLS セグメントの長さは 10 秒"""
    cmd = [
        "ffmpeg",
        "-i", input_wav,
        "-codec:a", "aac",
        "-b:a", "192k",
        "-f", "hls",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_segment_type", "mpegts",
        os.path.join(output_dir, "index.m3u8"),
    ]
    return cmd


def cmd_to_uncomp_hls(input_wav: str, output_dir: str) -> list:
    """WAVを非圧縮フォーマットでHLS形式に変換"""
    """セグメントの長さは 2 秒"""

    with wave.open(input_wav, 'rb') as wav_file:
        bits_sample = wav_file.getsampwidth() * 8  # サンプル幅（バイト）をビットに変換
        sample_rate = wav_file.getframerate()
    if not (sample_rate == 44100 or sample_rate == 48000):
        raise ValueError(f"Unsupported sample rate: {sample_rate}")

    # 例: 先頭10秒は2秒刻み、以降は6秒刻み
    cmd = [
        "ffmpeg",
        "-i", input_wav,
        "-ar", str(sample_rate),
        "-ac", "2",
        "-f", "segment",
        "-segment_time", "10",
        "-segment_format", "wav",
        "-segment_list", "index.m3u8",
        "-segment_list_type", "m3u8",
    ]

    # 24bit PCM の場合、ffmpeg の内部では s24 / s32 フォーマットを使う場合が多いため付与
    if bits_sample == 24:
        cmd.extend(["-c:a", "pcm_s24le"])
        # cmd.extend(["-sample_fmt", "s32"])
    else:
        cmd.extend(["-c:a", "pcm_s16le"])

    cmd.append(os.path.join(output_dir, "segment_%03d.wav"))

    return cmd


def excecute_convert(cmd: list, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] Running: {' '.join(cmd)}")
    ffmpeg_result = subprocess.run(cmd, capture_output=True, text=True)
    if ffmpeg_result.returncode != 0:
        print("[ERROR] FFmpeg failed:", result.stderr)
        sys.exit(1)

    mv_result = subprocess.run(["mv", "index.m3u8", output_dir], capture_output=True, text=True)
    if mv_result.returncode != 0:
        print("[ERROR] mv index.m3u8 failed:", result.stderr)
        sys.exit(1)

    print("[INFO] HLS conversion completed.")
