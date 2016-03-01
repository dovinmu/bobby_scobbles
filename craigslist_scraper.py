from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import datetime
import random
import eventlet

eventlet.monkey_patch()
base_url = 'http://seattle.craigslist.org'

def scrape(queries, list_to_search='jjj', daysBack=1, test=False, return_df=False):
    query = ''
    for q in queries[:-1]:
        query += q.strip() + '+'
    query += queries[-1].strip()
    params = {'query':query, 'sort':'date'}
    list_to_search = '/search/' + list_to_search
    
    r = requests.get(base_url + list_to_search, params=params)
    html = BeautifulSoup(r.text, 'html.parser')
    jobs = html.find_all('p', attrs={'class':'row'})
    print('Got %d jobs from %s' % (len(jobs), r.url))    
    results = []
    raw_html = []
    today = datetime.date.today().day
    for job in jobs:
        date = int(job.find('time').text.split(' ')[1])
        if date < today - daysBack:
            continue
        url = base_url + job.find('a', attrs={'class':'i'}).get('href')
        start = time.time()
        try:
            with eventlet.Timeout(10):
                rj = requests.get( url )
            rj.text
        except:
            print('could not connect to %s' % url)
            continue
        print('{0} seconds to get {1}'.format(time.time() - start, url))
        raw = rj.text
        html = BeautifulSoup(raw, 'html.parser')
        try:
            text = html.find('section', attrs={'id':'postingbody'}).text
            date = html.find(attrs={'class':'postinginfo','id':'display-date'}).time.text
        except:
            continue
        results.append((html.find('title').text, url, text.strip(), date))        
        raw_html.append(html)
        if test:
            break
        else:
            time.sleep(random.randint(1,5))
    
    fname = 'craigslist_' + query.replace('+','_') + '.csv'
    if len(results) > 0:
        df = pd.DataFrame(results, columns=['title','URL','text', 'date'])
        if test:
            print('found %d jobs' % len(results))
        else:
            df.to_csv(fname)
            print('wrote to %s' % fname)
        if return_df:
            return df
    else:
        print('no jobs found')

