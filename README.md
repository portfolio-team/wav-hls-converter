# What?
🎵 WAV to HLS Uploader (for Cloudflare R2)

このツールは、WAVファイルを HLS 形式（.m3u8 + .ts）に分割し、
Cloudflare R2 ストレージへ自動でアップロードする Python バッチです。


### 機能概要
- WAVファイルをHLS形式に変換
    - ffmpeg を使用して .m3u8 と .ts ファイルを生成

- Cloudflare R2 への自動アップロード
    - boto3 経由で .ts / .m3u8 ファイルをアップロード


# Usage
### 1. python環境の構築
<省略>


### 2. ffmpegのinstall
```bash
brew install ffmpeg
```

### 3. .env ファイルを作成
```bash
cp .env.sample .env
```

.env の中身を以下のように設定します
```
# Cloudflare R2 認証情報
R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxx
R2_SECRET_ACCESS_KEY=yyyyyyyyyyyyyyyyyyyy

# Cloudflare R2 の設定
R2_BUCKET_NAME=xxxxxxxxxx
R2_ACCOUNT_ID=<accountID>
R2_ENDPOINT=https://<accountID>.r2.cloudflarestorage.com 
```

### 4. hlsにコンバートしてアップしたいファイルを指定して、コマンド実行
```bash
python main.py ./input_wav_file/audio.wav
```

