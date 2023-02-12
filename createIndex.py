# Remove all tokens from card list to improve performance
import pymongo
import os
from dotenv import load_dotenv
load_dotenv()

# Connect to the database
client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['snapcaster']
cards_collection = db.cards
price_entry_collection = db.price_entry
print(f'Connected to database: {db.name}')

cards_collection.create_index([("oracle_id", pymongo.ASCENDING)])
price_entry_collection.create_index([("oracle_id", pymongo.ASCENDING)])

# close the connection
client.close()