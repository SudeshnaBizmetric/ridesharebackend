from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

Base = declarative_base()


DATABASE_URL = (
    "mssql+pyodbc://Sudeshna:admin%40123@demoserver972.database.windows.net/demodb?"
    "driver=ODBC+Driver+18+for+SQL+Server"
    "&Encrypt=yes"
    "&TrustServerCertificate=no"
    "&Connection Timeout=30"
)



try:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
   

 
    print("Database connected successfully and tables created.")
except OperationalError as e:
    print(f"Failed to connect to the database: {e}")
Local_Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

