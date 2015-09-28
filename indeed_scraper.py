from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import datetime
import random
from urllib.parse import urlparse
base_url = 'http://www.indeed.com'
limit = 100
locations = ['Seattle']

def scrape(queries, daysBack=1, test=False):
    fail = [0,0]
    query = ''
    for q in queries[:-1]:
        query += q.strip().replace(' ','+') + ','
    query += queries[-1].strip().replace(' ','+')
    results = []
    raw_html = []
    for loc in locations:
        params = {'q':query, 'l':loc, 'sort':'date', 'limit':limit, 'fromage':daysBack}
        try:
            r = requests.get(base_url + '/jobs', params=params)
        except:
            print('Failed to get page with params=', params)
            print('Building url by hand')
            url = base_url + '/jobs?'
            for key in params.keys():
                url += key + '=' + str(params[key]) + '&'
            url = url[:-1]
            r = requests.get( url )
        html = BeautifulSoup(r.text, 'html.parser')
        jobs = html.find_all('div', attrs={'class':'  row result'})
        if len(jobs) == 0:
            params['fromage'] += 1
            r = requests.get(base_url + '/jobs', params=params)
            html = BeautifulSoup(r.text, 'html.parser')
            jobs = html.find_all('div', attrs={'class':'  row result'})
        print('Got %d jobs from %s' % (len(jobs), r.url))
        for job in jobs:
            url = base_url + job.find('a').get('href')
            try:
                rj = requests.get( url )
            except:
                #print('Could not get %s, trying again' % url)
                print('failed to connect to %s' % url)
                #try:
                #    rj = requests.get( url )
                #except requests.exceptions.RequestException:
                #    print('Could not get %s, giving up' % url)
                continue
            #print('Got %s' % rj.url)
            html = BeautifulSoup(rj.text)
            for script in html(['script','style']):
                script.extract()
            raw_html.append(html)
            lines = [line.strip() for line in html.get_text().splitlines() if line.strip()]
            text = '\n'.join(lines)
            url = rj.url
            title = job.find('a').get('title')
            date = job.find('span',attrs={'class':'date'}).text
            results.append((title, url, text, date))
            if test:
                break
    fname = 'indeed_' + query.replace('+','-').replace(',','_') + '.csv'
    if len(results) > 0:
        df = pd.DataFrame(results, columns=['title','URL','text', 'date'])
        if test:
            print('found %d jobs' % len(df))
        else:
            df.to_csv(fname)
            print('Wrote %d results to %s' % (len(df),fname))
        

if __name__ == "__main__":
    scrape(['pizza cook','artisan'], test=False)

