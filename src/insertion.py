import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongo_url = os.getenv("MONGODB_URI")
db_name = os.getenv("DATABASE_NAME")

client = MongoClient(mongo_url)
db = client[db_name]


csv_collections = {
    "categorie": r"..\data\raw\category_tree.csv",
    "events": r"..\data\raw\events.csv",
    "itempp1": r"..\data\raw\item_properties_part1.csv",
    "itempp2": r"..\data\raw\item_properties_part2.csv"
}

collections_to_insert = ["categorie"]  # Ex: ["categorie", "events"]


for col_name in collections_to_insert:
    csv_path = csv_collections[col_name]

    # Lecture CSV
    df = pd.read_csv(csv_path)

    # Conversion en liste de dictionnaires
    documents = df.to_dict(orient="records")

    # Optionnel : vider la collection avant insertion pour éviter doublons
    db[col_name].delete_many({})

    # Insertion dans MongoDB
    result = db[col_name].insert_many(documents)
    print(f"{len(result.inserted_ids)} documents insérés dans la collection '{col_name}'.")

print(" Toutes les insertions demandées sont terminées.")