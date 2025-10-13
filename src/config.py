import os
from dotenv import load_dotenv


class Config:
    """環境変数を管理するクラス"""
    def __init__(self):
        # .envファイルを読み込む
        load_dotenv()

        # R2関連の環境変数
        self.R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
        self.R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
        self.R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
        self.R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
        self.R2_ENDPOINT = os.getenv("R2_ENDPOINT")

    def validate_r2_config(self):
        """R2関連の設定が揃っているかを検証"""
        if not all([self.R2_ACCESS_KEY_ID, self.R2_SECRET_ACCESS_KEY, self.R2_BUCKET_NAME, self.R2_ENDPOINT]):
            print("[ERROR] Missing R2 configuration. Please check your .env file.")
            import sys
            sys.exit(1)

