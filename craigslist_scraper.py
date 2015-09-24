from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import datetime
import random
base_url = 'http://seattle.craigslist.org'

def scrape(query, list_to_search = 'jjj', daysBack = 1):
    params = {'query':query}
    list_to_search = '/search/' + list_to_search
    fname = 'craigslist_' + query + '.csv'
    r = requests.get(base_url + list_to_search, params=params)
    html = BeautifulSoup(r.text, 'html.parser')
    jobs = html.find_all('p', attrs={'class':'row'})
    results = []
    raw_html = []
    today = datetime.date.today().day
    for job in jobs:
        date = int(job.find('time').text.split(' ')[1])
        if date < today - 1:
            continue
        url = base_url + job.find('a', attrs={'class':'i'}).get('href')
        rj = requests.get( url )
        html = BeautifulSoup(rj.text, 'html.parser')
        text = html.find('section', attrs={'id':'postingbody'}).text
        date = html.find(attrs={'class':'postinginfo','id':'display-date'}).time.text
        results.append((html.find('title').text, url, text.strip(), date))
        print('Got %s' % url)
        raw_html.append(html)
        time.sleep(random.randint(1,5))

    df = pd.DataFrame(results, columns=['title','URL','text', 'date'])
    df.to_csv(fname)
    print('wrote to %s' % fname)





