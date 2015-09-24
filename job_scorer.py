import pandas as pd
import re
import random
import time
import datetime
import gmail_client
import json
import os
from sendEmail import CreateMessage, SendMessage

#TODO: use NLTK or another language parser or regex because this is terrible. 
#and with CL I even need to handle stupid weird unicode characters
def clean_text(text):
    return text.lower().replace('. ',' . ').replace(',','').replace('!','').replace('\n',' ').replace('(','').replace(')','').replace('\xa0',' ').replace('"','').replace('?','').replace(';','')
    title = result[1].title.lower().replace('.','').replace(',','').replace('!','').replace('\n',' ').replace('(','').replace(')','').replace('\xa0',' ').replace('"','').replace('?','').replace(';','').replace('*','')

### research studies ###
#df = pd.DataFrame.from_csv('craigslist_unscored_research_studies')
#df['pay'] = 0

def is_research_study(item):
    return True

def is_paid(item):
    text = clean_text(item[1].text)
    title = clean_text(item[1].title)
    if 'paid' in title or 'paid' in text:
        return True
    if 'earn up to' in text or 'earn up to' in title:
        return True
    if '$' in text or '$' in title:
        return True
    return False

def paid_amount(item):
    text = clean_text(item.text).replace(',','')
    title = clean_text(item.title).replace(',','')
    reg1 = re.compile("\$(\d+.\d+)")
    reg2 = re.compile("\$(\d+)")
    amounts = set()
    #find anywhere a dollar amount is mentioned
    amounts = reg1.findall(title) + reg1.findall(text) + reg2.findall(title) + reg2.findall(text)
    #penalize posts that obfuscate exact dollar amount  
    #TODO: instead just have a separate confidence indicator
    '''  
    if 'up to $' in text or 'up to $' in title:
        highest = 0.
        for amount in amounts:
            if float(amount) > highest:
                highest = float(amount)
        amounts.append(str(highest * 0.5))
    '''
    #get average of all dollar amounts mentioned in post
    total = 0
    for amount in amounts:
        total += float(amount)
    if len(amounts) > 0:
        return int(total / len(amounts))
    return 0

def compute_pay_research_studies(df):
    for i in range(len(df)):
        item = df.loc[i]
        #print('%d: %s..., %s, study (pred): %s, paid (pred): %s' % (item[0], item[1].title[:30], item[1].time, is_research_study(item), is_paid(item)))
        df['pay'][i] = paid_amount(item)
        print('%d: %s, %s\n%s\npay: %s\n\n\n' % (i, item.title, item.time, item.text.replace('\n\n\n','\n').replace('\n\n','\n'), df.loc[i].pay) )
    return df

def update_word_bucket(df):
    return
    # TODO: load and modify a single universal word bucket
    word_bucket = {}
    word_to_last_url = {}
    for word in text.split(' '):
        if word in word_bucket:
            word_bucket[word] += 1
        else:
            word_bucket[word] = 1
        word_to_last_url[word] = result

def score_dev_jobs(df, keywords):
    keywords_important = keywords['keywords_important']
    keywords_pos = keywords['keywords_positive']
    keywords_good = keywords['keywords_good']
    keywords_meh = keywords['keywords_meh']
    keywords_neg = keywords['keywords_negative']
    
    # time to score the job postings!
    
    scores = []
    #for result in df.items():
    for result in df.iterrows():
        text = clean_text(result[1].text)
        title = clean_text(result[1].title)
        score = 0
        for kw in keywords_important:
            if kw in text:
                score += 4
            if kw in title:
                score += 8

        for kw in keywords_pos:
            if kw in text:
                score += 1
            if kw in title:
                score += 2

        for kw in keywords_good:
            if kw in text:
                score += 0.25
            if kw in title:
                score += 0.5

        for kw in keywords_meh:
            if kw in text:
                score -= 0.25
            if kw in title:
                score -= 0.5

        for kw in keywords_neg:
            if kw in text:
                score -= 1
            if kw in title:
                score -= 2

        scores.append((result[1].title, result[1].URL, result[1].text.strip(), result[1].date, score))
    df = pd.DataFrame(scores, columns=['title', 'URL','text','date', 'score'])
#    print(df.head())
    return df

def concat_item(item):
    text = item.text.iloc[0].replace('\n\n\n','\n').replace('\n\n','\n')
    s = '\n'  + item.title.iloc[0] + '\tscore: ' + str(item.score.iloc[0]) + '\t' + str(item.date.iloc[0])  + '\n' + ' - ' * 20 + '\n' 
    if len(text) > 1000:
        s += text[:text.find(' ',1000)]
        s += '[...]'
    else:
        s += text
    s += '\n' + item.URL.iloc[0] + '\n\n'
    return s

class PostingsProcessor():
    def __init__(self, user):
        self.user = user
        self.valid = True
        #get all the .csv files in this folder and turn them into dataframes
    
        if os.getcwd().split('/')[-1] != self.user:
            print('Need to be in user folder %s')
            self.invalidate()       
            return

        files = os.listdir()
        csvs = [x for x in files if '.csv' in x and '~' not in x and '.scored' not in x]
        if len(csvs) == 0:
            print('No csv files to analyze!')
            self.invalidate()
            return
        dfs = []
        for csv in csvs:
            dfs.append(pd.DataFrame.from_csv(csv))
        self.df = pd.concat(dfs)
        self.df = self.df.drop_duplicates(subset=['text'])
        
        # extract keywords from the json file
        jsons = [x for x in files if '.json' in x and '.old' not in x and '~' not in x]
        if len(jsons) != 1:
            print('Cannot score %s, number of valid keyword files=%d' % (os.getcwd(),len(jsons)))
            self.invalidate()            
            return
        with open(jsons[0],'r') as f:
            self.j = json.load(f)
            self.to = self.j['email'][0]
            self.delivery = int(self.j['delivery'][0])
            self.sendCount = int(self.j['send'][0])
            self.search = self.j['search'][0]

    def invalidate(self):
        self.valid = False

    def process_jobs(self):
        if not self.valid:
            print('PostingsProcessor object is invalid; try reinstantiating')
            return
        print('Scoring %s...' %self.user)
        self.df = score_dev_jobs(self.df, self.j)
        self.df.sort('score',inplace=True,ascending=False)

    def send_summary(self):
        content = self.generate_user_message()
        self.send_message(content)
        
    def generate_user_message(self, only_bestof=True):
        if not self.valid:
            print('PostingsProcessor object is invalid; try reinstantiating')
            return
        content = '\n'
        content += '*' * 70 + '\nCraigslist search results for "' + self.search + '", scored using word-counting\n' + '*' * 70 + '\n\n'
        content += '=' * 50 + '\n\tHighest scoring:\n'  + '=' * 50
        for i in range(self.sendCount):
            content += concat_item(self.df[i:i+1])
        if not only_bestof:
            content += '\n'  + '=' * 50 + '\n\tWorst scoring:\n' + '=' * 50
            content += concat_item(self.df[-1:])
            content += '\n' + '=' * 50 + '\n\tRandom entries\n'  + '=' * 50 + '\n'
            for n in range(3):
                i = random.randint(0,len(self.df)-1)
                content += concat_item(self.df[i:i+1])
        content += '\n\n\nScobble, (v.): To devour hastily.\n-Urban Dictionary'
        return content

    def send_message(self,content):
        if not self.valid:
            print('PostingsProcessor object is invalid; try reinstantiating')
            return
        service = gmail_client.get_service()
        message = CreateMessage('Bob the Job Scobbler', self.to, datetime.date.today().strftime('Jobs report for %A, %B %d, %Y'), content)
        SendMessage(service, 'bob.the.job.scobbler@gmail.com', message)
        print('Sent mail at ' + time.ctime())

    def save(self):
        if not self.valid:
            print('PostingsProcessor object is invalid; try reinstantiating')
            return
        fname = self.user.strip() + '_' + self.search.strip() + '.scored.csv'
        self.df.to_csv(fname)
        print('Saved %s to %s' % (fname, os.getcwd()))
    
def score_all():
    #iterate through all user folders
    os.chdir('users')
    users = os.listdir()
    for user in users:
        os.chdir(user)
        pp = PostingsProcessor(user)
        pp.process_jobs()
        pp.send_summary()
        pp.save()
        os.chdir('..')
    os.chdir('..')
    
    # todo: move towards hypothesis-testing and attribute-determining method instead of just counting tokens. then a general classifier will attempt to classify into 'boring', 'unexpected', and 'interesting'
    ## example hypotheses: this posting wants a senior developer, python is the most important language for this job, this job is temporary or part-time. e.g. predictions that have confidence intervals
    ## example attribute: lots of buzzspeak, too many exclamation marks, word or phrase is used too much. easily identified properties of the posting itself 

