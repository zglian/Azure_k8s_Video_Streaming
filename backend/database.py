# import psycopg2
# import config

# DATABASE_URL = config.DATABASE_URL

# def connect_to_db():
#     return psycopg2.connect(DATABASE_URL)

# def get_db():
#     db = connect_to_db()
#     try:
#         yield db
#     finally:
#         db.close()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config

DATABASE_URL = config.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
