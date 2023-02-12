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

# Delete all cards with layout: "token"
delete_result = cards_collection.delete_many({"layout": "token"})
print(f'Deleted {delete_result.deleted_count} cards with layout "token".')

# close the connection
client.close()

