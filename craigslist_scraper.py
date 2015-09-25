from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import datetime
import random
base_url = 'http://seattle.craigslist.org'

def scrape(queries, list_to_search='jjj', daysBack=1, test=False):
    query = ''
    for q in queries[:-1]:
        query += q.strip() + '+'
    query += queries[-1].strip()
    params = {'query':query, 'sort':'date'}
    list_to_search = '/search/' + list_to_search
    fname = 'craigslist_' + query + '.csv'
    
    r = requests.get(base_url + list_to_search, params=params)
    html = BeautifulSoup(r.text, 'html.parser')
    jobs = html.find_all('p', attrs={'class':'row'})
    print('Got %d jobs from %s' % (len(jobs), r.url))    
    results = []
    raw_html = []
    today = datetime.date.today().day
    for job in jobs:
        date = int(job.find('time').text.split(' ')[1])
        if date < today - 1:
            continue
        url = base_url + job.find('a', attrs={'class':'i'}).get('href')
        rj = requests.get( url )
        #print('Got %s' % rj.url)
        raw = rj.text
        html = BeautifulSoup(raw, 'html.parser')        
        text = html.find('section', attrs={'id':'postingbody'}).text
        date = html.find(attrs={'class':'postinginfo','id':'display-date'}).time.text
        results.append((html.find('title').text, url, text.strip(), date))        
        raw_html.append(html)
        if test:
            break
        else:
            time.sleep(random.randint(1,5))

    if len(results) > 0:
        df = pd.DataFrame(results, columns=['title','URL','text', 'date'])
        if not test:
            df.to_csv(fname)
            print('wrote to %s' % fname)


