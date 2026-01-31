import json
import requests
import time

stock = {}
start_time = time.time()

# obtaining the bulk files metadata from scryfall...
req = requests.get('https://api.scryfall.com/bulk-data')
if req.status_code == 200:
    mdata = json.loads(req.content)['data']
    url = next(dt['download_uri'] for dt in mdata if dt['type'] == 'default_cards')
    # with the url in hands, we then download the default_cards bulk data file, should take a moment
else:
    print(f'API call returned status code {req.status_code}, aborting operation.')
    exit()

print('Downloading the default_cards bulk data file from Scryfall...')
req = requests.get(url)
fj = json.loads(req.content)
print(f'Bulk data downloaded. Total time so far: {time.time() - start_time} seconds')

print('Processing card objects...')

counter = 0
for card_obj in fj:
    counter += 1
    if card_obj['set'] not in stock:
        stock[card_obj['set']] = []
    stock[card_obj['set']].append(card_obj)

print(f'Total {counter} cards processed. Saving set files...')
for set in stock.keys():
    with open(f'{set}_data.json','w') as s:
        s.write(json.dumps(stock[set]))
print(f'All set files saved, execution complete. Total time: {time.time() - start_time} seconds')