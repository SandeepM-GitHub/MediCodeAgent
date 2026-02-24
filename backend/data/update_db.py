from backend.data.db import init_db

print("Updating database schema...")
init_db()
print("Database schema updated! 'claims' table created.")