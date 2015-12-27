import craigslist_scraper
import indeed_scraper
import python_org_scraper
import json
import os
from threading import Thread

class ScraperThread(Thread):
    def __init__(self, scraper, queries, test=False):
        super().__init__()
        self.scraper = scraper
        self.queries = queries
        self.test = test
        #print("Created scraper for {}".format(self.scraper.base_url))

    def run(self):
        print("Beginning to scrape from {}".format(self.scraper.base_url))
        self.scraper.scrape(self.queries, test=self.test)

def wrangle(test=False):
    if test:
        print("Running abbreviated scrape for all users")
    
    os.chdir('users')
    users = os.listdir()
    threads = []
    for user in users:
        if user == 'example' and not test:
            continue
        os.chdir(user)
        files = os.listdir()
        csvs = [x for x in files if '.csv' in x]
        with open(user + '.json') as f:
            j = json.load(f)
        queries = []
        for query in j['search']:
            queries.append(query.strip())
        threads = []
        threads.append(ScraperThread(craigslist_scraper, queries, test))
        threads.append(ScraperThread(indeed_scraper, queries, test))
        for thread in threads:
            thread.run()
        while threads:
            for i in range(len(threads)):
                if not threads[i].is_alive():
                    thread = threads.pop(i)
                    print("Finished for {} on {}".format(user, thread.scraper.base_url))
                    break
        os.chdir('..')
    os.chdir('..')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print("Running web_wrangler.py as a test")
        wrangle(sys.argv[1] == 'test')
    else:
        print("Running web_wrangler.py on all users")
        wrangle()

