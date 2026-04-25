import os
from dotenv import load_dotenv
from supabase import create_client, Client
from pprint import pprint

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ 请检查 .env 文件是否正确设置 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")

# 新版 API Key 推荐这样创建客户端（后端专用）
supabase: Client = create_client(
    SUPABASE_URL, 
    SUPABASE_KEY,
    options={
        "global": {
            "headers": {
                "apikey": SUPABASE_KEY   # 显式传递 apikey
            }
        }
    }
)

print("✅ Supabase 客户端初始化成功！正在测试连接...\n")