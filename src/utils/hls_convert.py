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
    """セグメントの長さは 10 秒"""

    allow_sample_rates = [44100, 48000, 88200, 96000, 176400, 192000]
    with wave.open(input_wav, 'rb') as wav_file:
        bits_sample = wav_file.getsampwidth() * 8  # サンプル幅（バイト）をビットに変換
        sample_rate = wav_file.getframerate()
    if not (sample_rate in allow_sample_rates):
        raise ValueError(f"Unsupported sample rate: {sample_rate}")

    cmd = [
        "ffmpeg",
        "-i", input_wav,  # 入力ファイル
        "-ar", str(sample_rate),  # 出力音声のサンプリングレート
        "-ac", "2",  # チャンネル数にステレオを指定
        "-f", "segment",  # 出力フォーマットに分割出力を指定
        "-segment_time", "10",  # 1分割の長さ（10 秒ごとに分割）
        "-segment_format", "wav",  # 分割後ファイルの形式
        "-segment_list", "index.m3u8",  # インデックスファイル名
        "-segment_list_type", "m3u8",  # インデックスファイル形式
    ]

    # 音声コーデックの指定
    # インプット音源に合わせて16bit PCM or 24bit PCMを指定
    if bits_sample == 24:
        cmd.extend(["-c:a", "pcm_s24le"])
    else:
        cmd.extend(["-c:a", "pcm_s16le"])

    cmd.append(os.path.join(output_dir, "segment_%03d.wav"))

    return cmd


def excecute_convert(cmd: list, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] Running: {' '.join(cmd)}")
    ffmpeg_result = subprocess.run(cmd, capture_output=True, text=True)
    if ffmpeg_result.returncode != 0:
        print("[ERROR] FFmpeg failed:", ffmpeg_result.stderr)
        sys.exit(1)

    mv_result = subprocess.run(["mv", "index.m3u8", output_dir], capture_output=True, text=True)
    if mv_result.returncode != 0:
        print("[ERROR] mv index.m3u8 failed:", mv_result.stderr)
        sys.exit(1)

    print("[INFO] HLS conversion completed.")
