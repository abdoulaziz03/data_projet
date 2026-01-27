from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()



client = MongoClient(
    os.getenv("MONGODB_URI"),
    tls=True,
    tlsAllowInvalidCertificates=True
)

try:
    client.admin.command("ping")
    print("Connexion MongoDB Atlas réussie")
except Exception as e:
    print("Erreur de connexion à MongoDB:", e)
