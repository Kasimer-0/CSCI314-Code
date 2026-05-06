# init_db.py
from database import engine, Base
import models

print("Sending create table command to PostgreSQL database...")

# This line will automatically find all classes that inherit from Base and create corresponding tables in the database
Base.metadata.create_all(bind=engine)

print("✅ All data tables created successfully!")