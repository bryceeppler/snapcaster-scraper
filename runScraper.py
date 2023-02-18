from scrapers.base.GauntletScraper import GauntletScraper
from scrapers.base.Four01Scraper import Four01Scraper
from scrapers.base.FusionScraper import FusionScraper
from scrapers.base.KanatacgScraper import KanatacgScraper
from scrapers.base.HouseOfCardsScraper import HouseOfCardsScraper
from scrapers.base.EverythingGamesScraper import EverythingGamesScraper
from scrapers.base.MagicStrongholdScraper import MagicStrongholdScraper
from scrapers.base.FaceToFaceScraper import FaceToFaceScraper
from scrapers.base.ConnectionGamesScraper import ConnectionGamesScraper
from scrapers.base.SequenceScraper import SequenceScraper
from scrapers.base.TopDeckHeroScraper import TopDeckHeroScraper
from scrapers.base.Jeux3DragonsScraper import Jeux3DragonsScraper
from scrapers.base.AtlasScraper import AtlasScraper
from scrapers.base.GamezillaScraper import GamezillaScraper
from scrapers.base.HairyTScraper import HairyTScraper
from scrapers.base.ExorGamesScraper import ExorGamesScraper
from scrapers.base.GameKnightScraper import GameKnightScraper
from scrapers.base.EnterTheBattlefieldScraper import EnterTheBattlefieldScraper
from scrapers.base.ManaforceScraper import ManaforceScraper
from scrapers.base.FirstPlayerScraper import FirstPlayerScraper
from scrapers.base.OrchardCityScraper import OrchardCityScraper
from scrapers.base.BorderCityScraper import BorderCityScraper
from scrapers.base.AetherVaultScraper import AetherVaultScraper
from scrapers.base.FantasyForgedScraper import FantasyForgedScraper

import concurrent.futures
from datetime import datetime, timedelta
import pymongo
import os
import time
from dotenv import load_dotenv
load_dotenv()

def fetchScrapers(cardName):
    # Arrange scrapers
    houseOfCardsScraper = HouseOfCardsScraper(cardName)
    gauntletScraper = GauntletScraper(cardName)
    kanatacgScraper = KanatacgScraper(cardName)
    fusionScraper = FusionScraper(cardName)
    four01Scraper = Four01Scraper(cardName)
    everythingGamesScraper = EverythingGamesScraper(cardName)
    magicStrongholdScraper = MagicStrongholdScraper(cardName)
    faceToFaceScraper = FaceToFaceScraper(cardName)
    connectionGamesScraper = ConnectionGamesScraper(cardName)
    topDeckHeroScraper = TopDeckHeroScraper(cardName)
    jeux3DragonsScraper = Jeux3DragonsScraper(cardName)
    sequenceScraper = SequenceScraper(cardName)
    atlasScraper = AtlasScraper(cardName)
    hairyTScraper = HairyTScraper(cardName)
    gamezillaScraper = GamezillaScraper(cardName)
    exorGamesScraper = ExorGamesScraper(cardName)
    gameKnightScraper = GameKnightScraper(cardName)
    enterTheBattlefieldScraper = EnterTheBattlefieldScraper(cardName)
    manaforceScraper = ManaforceScraper(cardName)
    firstPlayerScraper = FirstPlayerScraper(cardName)
    orchardCityScraper = OrchardCityScraper(cardName)
    borderCityScraper = BorderCityScraper(cardName)
    aetherVaultScraper = AetherVaultScraper(cardName)
    fantasyForgedScraper = FantasyForgedScraper(cardName)

    # Map scrapers to an identifier keyword
    return {
        "houseofcards": houseOfCardsScraper,
        "gauntlet": gauntletScraper,
        "kanatacg": kanatacgScraper,
        "fusion": fusionScraper,
        "four01": four01Scraper,
        "everythinggames": everythingGamesScraper,
        "magicstronghold": magicStrongholdScraper,
        "facetoface": faceToFaceScraper,
        "connectiongames": connectionGamesScraper,
        "topdeckhero": topDeckHeroScraper,
        "jeux3dragons": jeux3DragonsScraper,
        'sequencegaming': sequenceScraper,
        'atlas': atlasScraper,
        'hairyt': hairyTScraper,
        'gamezilla': gamezillaScraper,
        'exorgames': exorGamesScraper,
        'gameknight': gameKnightScraper,
        'enterthebattlefield': enterTheBattlefieldScraper,
        'firstplayer': firstPlayerScraper,
        'manaforce': manaforceScraper,
        'orchardcity': orchardCityScraper,
        'bordercity': borderCityScraper,
        'aethervault': aetherVaultScraper,
        'fantasyforged': fantasyForgedScraper
    }

# Scraper function
def transform(scraper):
    scraper.scrape()
    scraperResults = scraper.getResults()
    for result in scraperResults:
        results.append(result)
    return


numCardAdded = 0
timer = time.time()
# Connect to the database
client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['snapcaster']
cards_collection = db.cards
price_entry_collection = db.price_entry
print(f'Connected to database: {db.name}')
# print(f'Number of cards in DB: {cards_collection.count_documents({})}')
# print(f'Number of price entries in DB: {price_entry_collection.count_documents({})}')

today = datetime.now()
thirty_days_ago = today - timedelta(days=30)
# print("Today's date:", today)


pipeline = [
    {
        "$lookup": {
            "from": "price_entry",
            "let": {"oracle_id": "$oracle_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$oracle_id", "$$oracle_id"]}}},
            ],
            "as": "price_entry"
        }
    },
    {"$match": {"price_entry": { "$eq": []}}},
    {"$limit": 30}
]

cards = list(cards_collection.aggregate(pipeline))

# List to store results from all threads
results = []

print(f'Fetched {len(cards)} cards')
# Execute scrapers for each card name
for card in cards:
    # Execute the bulk scrape for the current card name
    scraperMap = fetchScrapers(card["name"])
    scrapers = scraperMap.values()
    # scrapers = [scraperMap['magicstronghold']]

    print(f'{card["name"]} - scraping')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        threadResults = executor.map(transform, scrapers)

    # Wait for all threads to finish
    for result in threadResults:
        pass
    
    # now we have all the data from the scrape in the results list
    # create a pricelist for each condition
    price_list = []
    for result in results:
        try:
            price_list.append({
                'price': result['price'],
                'foil': result['foil'],
                'condition': result['condition'],
                'website': result['website']
            })
        except:
            print(f'Error adding {card["name"]}')
            pass

    # create the price_entry object
    price_entry = {
        'oracle_id': card["oracle_id"],
        'date': today,
        'price_list': price_list
    }

    # insert the price_entry into the database
    price_entry_collection.insert_one(price_entry)
    print(f'{card["name"]} - inserted into db')
    numCardAdded += 1

# close the connection
client.close()
# print time in 2 decimales
print(f'Scraped {numCardAdded} cards in {round(time.time() - timer, 2)} seconds')
print(f'Average time per successful card: {round((time.time() - timer) / numCardAdded, 2)} seconds')
print(f'{datetime.now()}')
print("===============================================")
