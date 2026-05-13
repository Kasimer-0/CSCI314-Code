# seed_db.py
import random
from faker import Faker
import bcrypt
from database import SessionLocal, engine, Base
from Entities.user_account import UserAccount
from Entities.user_profile import UserProfile
from Entities.platform_category import Category
from Entities.fundraising_activity import Activity
from Entities.donation import Donation
from Entities.donee_favorite import Bookmark

# Initialize Faker for generating fake data
fake = Faker('en_US') # Change to Faker('zh_CN') if you want Chinese data

def seed_database():
    print("🧹 Cleaning old data and rebuilding table structure...")
    # This step will clear existing tables in your database and create empty tables to ensure clean data
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # For convenient testing, all generated account passwords are set to: password123
        print("🔑 Generating unified password hash (password123)...")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw("password123".encode('utf-8'), salt).decode('utf-8')

        print("👤 Generating 100 User Accounts and User Profiles...")
        donees = []
        fundraisers = []
        
        for i in range(100):
            # Assign roles: 5 admins, 10 platform managers, 45 donees, 40 fundraisers
            if i < 5: role_id = 0
            elif i < 15: role_id = 3
            elif i < 60: role_id = 1
            else: role_id = 2

            # 1. Create Account
            acc = UserAccount(
                email=fake.unique.email(),
                password_hash=hashed_password,
                status="Active"
            )
            db.add(acc)
            db.commit() # Must commit first to get the account_id

            # 2. Create associated Profile
            prof = UserProfile(
                account_id=acc.account_id,
                profile_name=fake.name(),                   # Generate a random name
                profile_description=fake.sentence(),        # Generate a random profile description
                role_id=role_id
            )
            db.add(prof)
            db.commit()

            # Store specific roles in lists for convenient use when generating activities and donations
            if role_id == 1: donees.append(prof)
            if role_id == 2: fundraisers.append(prof)

        print("🏷️  Generating 100 Categories...")
        categories = []
        for _ in range(100):
            cat = Category(
                name=fake.unique.word().capitalize() + " " + fake.word().capitalize(),
                description=fake.sentence(),
                is_archived=random.choice([True, False, False, False]) # Most are not archived
            )
            db.add(cat)
            categories.append(cat)
        db.commit()

        print("📢 Generating 100 Activities...")
        activities = []
        for _ in range(100):
            act = Activity(
                fundraiser_id=random.choice(fundraisers).profile_id, # Randomly select a fundraiser
                category_id=random.choice(categories).category_id,   # Randomly select a category
                title=fake.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                target_amount=round(random.uniform(1000.0, 50000.0), 2),
                current_amount=round(random.uniform(0.0, 5000.0), 2),
                status=random.choice(["Ongoing", "Ongoing", "Closed", "Suspended"]),
                view_count=random.randint(0, 1000)
            )
            db.add(act)
            activities.append(act)
        db.commit()

        print("💰 Generating 100+ Donations...")
        for _ in range(120): # Generate 120 to ensure requirement is met
            don = Donation(
                activity_id=random.choice(activities).activity_id,
                user_id=random.choice(donees).profile_id, # Only Donees can donate
                amount=round(random.uniform(10.0, 500.0), 2),
                message=fake.sentence() if random.random() > 0.5 else None,
                is_anonymous=random.choice([True, False])
            )
            db.add(don)
        db.commit()

        print("⭐ Generating 100+ Bookmarks...")
        bookmark_count = 0
        while bookmark_count < 110:
            donee_id = random.choice(donees).profile_id
            act_id = random.choice(activities).activity_id
            
            # Ensure no duplicate bookmark records are generated
            existing = db.query(Bookmark).filter(Bookmark.user_id == donee_id, Bookmark.activity_id == act_id).first()
            if not existing:
                bm = Bookmark(user_id=donee_id, activity_id=act_id)
                db.add(bm)
                bookmark_count += 1
        db.commit()

        print("\n🎉 Success! All tables have been successfully populated with at least 100 records that perfectly satisfy foreign key constraints!")
        print("\n" + "="*80)
        print("📋 TEST ACCOUNT INFORMATION")
        print("="*80)
        
        # Query and display test accounts by role
        admin_accs = db.query(UserAccount).join(UserProfile).filter(UserProfile.role_id == 0).limit(3).all()
        pm_accs = db.query(UserAccount).join(UserProfile).filter(UserProfile.role_id == 3).limit(3).all()
        donee_accs = db.query(UserAccount).join(UserProfile).filter(UserProfile.role_id == 1).limit(3).all()
        fundraiser_accs = db.query(UserAccount).join(UserProfile).filter(UserProfile.role_id == 2).limit(3).all()
        
        print("\n👨‍💼 USER ADMIN (role_id: 0)")
        for acc in admin_accs:
            print(f"   Email: {acc.email} | Password: password123")
        
        print("\n📊 PLATFORM MANAGER (role_id: 3)")
        for acc in pm_accs:
            print(f"   Email: {acc.email} | Password: password123")
        
        print("\n💚 DONEE (role_id: 1)")
        for acc in donee_accs:
            print(f"   Email: {acc.email} | Password: password123")
        
        print("\n✨ FUNDRAISER (role_id: 2)")
        for acc in fundraiser_accs:
            print(f"   Email: {acc.email} | Password: password123")
        
        print("\n" + "="*80)
        print("💡 All passwords are: password123")
        print("="*80 + "\n")

    except Exception as e:
        print(f"❌ Error occurred while inserting data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()