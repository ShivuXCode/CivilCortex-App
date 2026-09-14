from core.database import engine
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR;"))
