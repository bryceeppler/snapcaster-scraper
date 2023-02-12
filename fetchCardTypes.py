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

# get the set of values used in the following fields for all cards
# object
# layout

objects = set()
layouts = set()

for card in cards_collection.find():
    objects.add(card['object'])
    layouts.add(card['layout'])

print(f'objects: {objects}')
print(f'layouts: {layouts}')

client.close()  


