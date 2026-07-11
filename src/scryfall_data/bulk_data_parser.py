import gzip
import json
import requests
import time

stock = {}
start_time = time.time()

# obtaining the bulk files metadata from scryfall...
hdr = {
    'User-Agent': 'mtg-collectron',
    'From': 'gucsantana@gmail.com'
}
req = requests.get('https://api.scryfall.com/bulk-data',headers=hdr)
if req.status_code == 200:
    mdata = json.loads(req.content)['data']
    url = next(dt['download_uri'] for dt in mdata if dt['type'] == 'default_cards')
    # with the url in hands, we then download the default_cards bulk data file, should take a moment
else:
    print(f'API call returned status code {req.status_code}, aborting operation.')
    exit()

print('Downloading the default_cards bulk data file from Scryfall...')
# NOTE: we need to start very soon using the JSONL file instead, and it comes gzipped, use the below line to unpack it
# with gzip.open('file.txt.gz', 'rb') as f_in:
req = requests.get(url)
fj = json.loads(req.content)
print(f'Bulk data downloaded. Total time so far: {time.time() - start_time} seconds')

print('Processing card objects...')

# for each card object, we save it to the corresponding set object in our current stock
counter = 0
for card_obj in fj:
    if 'paper' not in card_obj['games']: # we don't care for cards that don't exist in paper, like arena and alchemy versions
        continue
    if 'all_parts' in card_obj: # roundabout check to see if a card is a melded pair; we don't want those either
        try:
            # to note: we're checking if the card has an 'all_parts' block, and the part listed as meld_result has the same name as the 'card' we're looking at
            if list(filter(lambda x: x['component'] == 'meld_result',card_obj['all_parts']))[0]['name'] == card_obj['name']:
                continue
        except Exception:
            pass
    counter += 1
    if card_obj['set'] not in stock:
        stock[card_obj['set']] = []
    stock[card_obj['set']].append(card_obj)

print(f'Total {counter} cards processed. Saving set files...')
for set in stock.keys():
    with open(f'{set}_data.json','w') as s:
        # sort cards by collector number before saving into their respective files
        try:
            s.write(json.dumps(sorted(stock[set], key=lambda x: int(''.join(c for c in x['collector_number'] if c.isdigit() ) if (''.join(c for c in x['collector_number'] if c.isdigit() )) != '' else '0' ) ) ) )
        except Exception as e:
            print(f"Set {set} could not be sorted due to collector number fuckery, saving in original (random) order. :/")
            s.write(json.dumps(stock[set]) )
print(f'All set files saved. Total time so far: {time.time() - start_time} seconds')

print('Querying for sets data...')
# obtaining the sets metadata from scryfall...
req = requests.get('https://api.scryfall.com/sets',headers=hdr)
if req.status_code == 200:
    with open('sets.json','w') as fs:
        fs.write(req.text)
        print(f'Set information saved, execution complete. Total time: {time.time() - start_time} seconds')
else:
    print(f'API call returned status code {req.status_code}, aborting operation.')
    exit()