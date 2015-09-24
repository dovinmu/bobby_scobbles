import craigslist_scraper
import json
import os

def wrangle():
    os.chdir('users')
    users = os.listdir()
    for user in users:
        os.chdir(user)
        files = os.listdir()
        csvs = [x for x in files if '.csv' in x]
        jsons = [x for x in files if '.json' in x and '.old' not in x]
        if len(jsons) != 1:
            print('Wrong number of jsons: %d\n%s' % (len(jsons), os.getcwd()))
            continue
        with open(jsons[0]) as f:
            j = json.load(f)
        craigslist_scraper.scrape(j['search'][0])
        os.chdir('..')
    os.chdir('..')
