import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB_NAME")]      
collection = db["projet"]          
csv_path = r"../data/clean/events_clean.csv"
df = pd.read_csv(csv_path)
documents = df.to_dict(orient="records")
result = collection.insert_many(documents)
print(f" {len(result.inserted_ids)} documents insérés dans MongoDB.")