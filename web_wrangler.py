import craigslist_scraper
import indeed_scraper
import python_org_scraper
import json
import os

def wrangle(test=False):
    os.chdir('users')
    users = os.listdir()
    for user in users:
        if user == 'example' and not test:
            continue
        print('gathering info for %s' % user)
        os.chdir(user)
        files = os.listdir()
        csvs = [x for x in files if '.csv' in x]
        jsons = [x for x in files if '.json' in x and '.old' not in x and '~' not in x]
        if len(jsons) != 1:
            print('Wrong number of jsons: %d, %s' % (len(jsons), os.getcwd()))
            #continue
        with open(jsons[0]) as f:
            j = json.load(f)
        queries = []
        for query in j['search']:
            queries.append(query.strip())
        craigslist_scraper.scrape(queries,test=test)
        indeed_scraper.scrape(queries,test=test)
        if user == 'rowan':
            python_org_scraper.scrape(test=test)
        os.chdir('..')
    os.chdir('..')

if __name__ == '__main__':
    import sys
    print(sys.argv)
    if len(sys.argv) == 1:
        wrangle()
    else:
        print(sys.argv[1:])
        wrangle(sys.argv[1] == 'True')
