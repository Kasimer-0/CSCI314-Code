from database import engine, Base

# 从新的 Entity 文件夹里把所有模型导入进来，让 SQLAlchemy 认识它们
from Entities.user_account import UserAccount
from Entities.user_profile import UserProfile
from Entities.platform_category import Category
from Entities.fundraising_activity import Activity
from Entities.donation import Donation
from Entities.donee_favorite import Bookmark

print("Sending create table command to PostgreSQL database...")
Base.metadata.create_all(bind=engine)
print("✅ All data tables created successfully!")