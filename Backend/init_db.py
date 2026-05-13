from database import engine, Base

# Import all models from the new Entity folder so that SQLAlchemy can recognize them.
from Entities.user_account import UserAccount
from Entities.user_profile import UserProfile
from Entities.platform_category import Category
from Entities.fundraising_activity import Activity
from Entities.donation import Donation
from Entities.donee_favorite import Bookmark

print("Sending create table command to PostgreSQL database...")
Base.metadata.create_all(bind=engine)
print("✅ All data tables created successfully!")
