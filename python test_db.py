from sqlalchemy import create_engine
import urllib.parse
import pandas as pd

password = urllib.parse.quote_plus("Sureshsk@12345")  # your MySQL password
engine = create_engine(f"mysql+pymysql://root:{password}@localhost/vehicle")

try:
    df = pd.read_sql("SELECT COUNT(*) AS rows FROM traffic_project", engine)
    print(df)
except Exception as e:
    print("❌ DB Connection error:", e)