from sqlalchemy import create_engine
import os


engine = create_engine(
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST', 'localhost')}:{os.getenv('MYSQL_PORT', 3306)}/"
    f"{os.getenv('MYSQL_DATABASE')}",
    pool_size=5,         # Pool size (same as before)
    max_overflow=10,     # Additional connections if the pool is full
    pool_timeout=30,     # Time to wait for a connection before raising an error
    pool_recycle=3600    # Recycle connections after 1 hour to avoid stale connections
)
    


