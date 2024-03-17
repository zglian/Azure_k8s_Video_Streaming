import psycopg2
import config

DATABASE_URL = config.DATABASE_URL

def connect_to_db():
    return psycopg2.connect(DATABASE_URL)

def get_db():
    db = connect_to_db()
    try:
        yield db
    finally:
        db.close()
