import os
import boto3
from urllib.parse import urljoin
from config import Config


def delete_existing_objects(s3, bucket_name: str, prefix: str):
    """object_prefix配下にある全てのファイルを削除"""
    existing_objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in existing_objects:
        print(f"Found {len(existing_objects['Contents'])} files under '{prefix}'.")
        for obj in existing_objects['Contents']:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
        print("All files deleted.")
    else:
        print(f"No files found under '{prefix}'.")


def upload_to_r2(local_dir: str, object_prefix: str, config: Config):
    """Cloudflare R2 にHLSファイル群をアップロード"""
    config.validate_r2_config()

    s3 = boto3.client(
        "s3",
        endpoint_url=config.R2_ENDPOINT,
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )

    #  object_prefix配下のファイルが既に存在するか確認
    existing_objects = s3.list_objects_v2(Bucket=config.R2_BUCKET_NAME, Prefix=object_prefix)
    if 'Contents' in existing_objects:
        while True:
            user_input = input(f"Files already exist under '{object_prefix}'. Do you want to delete them and continue? (y/n): ").strip().lower()
            if user_input == 'y':
                delete_existing_objects(s3, config.R2_BUCKET_NAME, object_prefix)
                break
            elif user_input == 'n':
                print("Upload canceled.")
                return
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    # アップロード開始
    print(f"[INFO] Uploading files to R2: bucket={config.R2_BUCKET_NAME}, prefix={object_prefix}")
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, local_dir)
            key = f"{object_prefix}/{rel_path}"

            try:
                print(f"Uploading '{key}'...")
                s3.upload_file(local_path, config.R2_BUCKET_NAME, key)
                print(f"[UPLOAD] {key}")
            except Exception as e:
                print(f"[ERROR] Failed to upload '{key}': {e}")

    m3u8_url = urljoin(f"{config.R2_ENDPOINT}/{config.R2_BUCKET_NAME}/", f"{object_prefix}/index.m3u8")
    print("[INFO] Upload complete.")
    return m3u8_url