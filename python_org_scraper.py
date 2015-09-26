import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape(test=False):
    url = 'https://www.python.org/jobs/feed/rss'
    r = requests.get(url)
    xml = BeautifulSoup(r.text, 'xml')
    items = xml.find_all('item')
    results = []
    for item in items:
        text = BeautifulSoup(item.description.text).text
        results.append((item.title.text, item.link.text, text, 'nan'))
        #print('Processed %s' % item.title.text)

    fname = 'python.org.csv'
    df = pd.DataFrame(results, columns=['title','URL','text', 'date'])
    if test:
        print('Found %d jobs' % len(df))
    else:
        df.to_csv(fname)
        print('Wrote %d results to %s' % (len(df),fname))

if __name__ == '__main__':
    scrape(True)
