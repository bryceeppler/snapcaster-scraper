from bs4 import BeautifulSoup
import requests
from .Scraper import Scraper
import json


class AetherVaultScraper(Scraper):
    """
    AetherVault can be scraped by creating a URL from their advanced search
    This allows us to search for cards that are in stock

    Identical to Jeux3DragonsScraper using crystalcommerce


    Split cards can be searched using "//" as a split
    Spaces are replaced with "+"
    Slashes - %2F
    Commas - %2C
    Apostrophes - %27
    """

    def __init__(self, cardName):
        Scraper.__init__(self, cardName)
        self.baseUrl = 'https://www.aethervaultgames.com'
        self.url = self.createUrl()
        self.website = 'aethervault'
    

    def createUrl(self):
        # https://www.aethervaultgames.com/advanced_search?utf8=%E2%9C%93&search%5Bfuzzy_search%5D=
        # Elspeth%2C+Sun%27s+Champion
        # &search%5Btags_name_eq%5D=&search%5Bsell_price_gte%5D=&search%5Bsell_price_lte%5D=&search%5Bbuy_price_gte%5D=&search%5Bbuy_price_lte%5D=&search%5Bin_stock%5D=0&search%5Bin_stock%5D=1&buylist_mode=0&search%5Bcategory_ids_with_descendants%5D%5B%5D=&search%5Bcategory_ids_with_descendants%5D%5B%5D=&search%5Bsort%5D=name&search%5Bdirection%5D=ascend&commit=Search&search%5Bcatalog_group_id_eq%5D=
        # make card name url friendly
        #         Spaces are replaced with "+"
        # Slashes - %2F
        # Commas - %2C
        # Apostrophes - %27
        urlCardName = self.cardName.replace(
            ' ', '+').replace('/', '%2F').replace(',', '%2C').replace("'", '%27')
        searchPrepend = '/advanced_search?utf8=%E2%9C%93&search%5Bfuzzy_search%5D='
        # the searchAppend may cause an error
        searchAppend = '&search%5Btags_name_eq%5D=&search%5Bsell_price_gte%5D=&search%5Bsell_price_lte%5D=&search%5Bbuy_price_gte%5D=&search%5Bbuy_price_lte%5D=&search%5Bin_stock%5D=0&search%5Bin_stock%5D=1&buylist_mode=0&search%5Bcategory_ids_with_descendants%5D%5B%5D=&search%5Bcategory_ids_with_descendants%5D%5B%5D=&search%5Bsort%5D=name&search%5Bdirection%5D=ascend&commit=Search&search%5Bcatalog_group_id_eq%5D='
        return self.baseUrl + searchPrepend + urlCardName + searchAppend

    def scrape(self):
        page = requests.get(self.url)

        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find_all('li', class_='product')

        if len(results) == 0:
            return None

        for result in results:
            try:
                name = result.find('h4', class_='name')
                if name:
                    name = name.text
                else:
                    continue

                if self.cardName.lower() not in name.lower():
                    continue

                # foil status is in the name as - Foil, same with Borderless
                foil = False
                borderless = False
                if ' - Foil' in name:
                    foil = True
                    name = name.replace(' - Foil', '')
                    if " Etched" in name:
                        name = name.replace(" Etched", "")
                if ' - Borderless' in name:
                    borderless = True
                    name = name.replace(' - Borderless', '')

                if ' - ' in name:
                    # split card
                    name = name.split(' - ')[0]


                # get the href from the a tag with an itemprop="url" attribute
                link = self.baseUrl + \
                    result.select_one('a[itemprop="url"]')['href']
                if 'magic' and 'single' not in link:
                    # not a magic card
                    continue

                if 'art_series' in link:
                    continue

                # get the set from div.meta span.category
                setName = result.select_one('div.meta span.category').text

                # sometimes there are weird tags like setName (MISC4) or setName (MISC3)
                # we want to remove any tags like that if they contain MISC
                if 'MISC' in setName:
                    setName = setName.split(' (')[0]
                if 'COM' in setName:
                    setName = setName.split(' (')[0]

                # weird thing where they have tournament legality in setName
                if ' (Not Tournament Legal)' in setName:
                    setName = setName.replace(' (Not Tournament Legal)', '')

                # remove any other tags we dont want
                if ' - ' in setName:
                    setName = setName.split(' - ')[0]

                # get the image src from inside from the div with image class
                image = result.select_one('div.image img')['src']

                # need to do this for each variant
                for variant in result.select('div.variants div.variant-row'):
                    condition = variant.select_one(
                        'span.variant-short-info').text
                    if 'Mint' in condition:
                        condition = 'NM'
                    elif 'Light' in condition:
                        condition = 'LP'
                    elif 'Moderat' in condition:
                        condition = 'MP'
                    elif 'Heav' in condition:
                        condition = 'HP'
                    elif "Damag" in condition:
                        condition = 'DMG'
                    elif "Hero" in condition:
                        condition = 'LP'

                    # price comes from the span with class = "regular price"
                    price = variant.select_one(
                        'span.regular.price').text.replace('CAD$ ', '')

                    card = {
                        'name': name,
                        'set': setName,
                        'condition': condition,
                        'price': price,
                        'link': link,
                        'image': image,
                        'foil': foil,
                        'website': self.website
                    }
                    self.results.append(card)
            except Exception as e:
                print('******************************')
                print(f'Error searching for {self.cardName} on {self.website}')
                print(e.args)
                print(f'Error on line {e.__traceback__.tb_lineno} ')
                print('card name: ', name)
                print('link: ', self.url)
                print('******************************')


                continue
