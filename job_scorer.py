import pandas as pd
import re
import random
import time
import math
import datetime
import gmail_client
import json
import os
from sendEmail import CreateMessage, SendMessage
from difflib import SequenceMatcher

#TODO: use NLTK or another language parser or regex because this is terrible. 
#and with CL I even need to handle stupid weird unicode characters
def clean_text(text):
    return text.lower().replace('.',' ').replace(',',' ').replace('!',' ').replace('(',' ').replace(')',' ').replace('"',' ').replace('?',' ').replace(';',' ').replace('*', ' ')

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

### research studies ###
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

def score_string(s, keywords, scalar=1.0):
    keywords_important = keywords['keywords_important']
    keywords_pos = keywords['keywords_positive']
    keywords_good = keywords['keywords_good']
    keywords_meh = keywords['keywords_meh']
    keywords_neg = keywords['keywords_negative']
    score = 0
    for kw in keywords_important:
        if kw in s:
            score += 4 * scalar
    for kw in keywords_pos:
        if kw in s:
            score += 1 * scalar
    for kw in keywords_good:
        if kw in s:
            score += 0.25 * scalar
    for kw in keywords_meh:
        if kw in s:
            score -= 0.25 * scalar
    for kw in keywords_neg:
        if kw in s:
            score -= 1 * scalar
    score += sigmoid(len(s))
    return score

def score_job(job, keywords):
    text = clean_text(job.text)
    paragraphs = text.split('\n')
    title = clean_text(job.title)
    scores = {}
    for p in paragraphs:
        scores[p] = score_string(p, keywords)
    highest_par = ''
    highest = 0
    total = 0
    for p in paragraphs:
        if scores[p] > highest:
            highest_par = p
            highest = scores[p]
        total += scores[p]
    total += score_string(title, keywords, scalar=2.0)
    score = total / len(paragraphs) + scores[highest_par]
    score /= 3.
    job = (job.title, job.URL, job.text.strip(), job.date, score, highest_par, text)
    return job


def concat_item(item):
    s = '\n'  + item.title + '\tscore: %.2f' % item.score + '\t' + str(item.date)  + '\n' + ' - ' * 20 + '\n' 

    if item.best_paragraph.strip() != '':
        try:        
            i = item.cleaned_text.index(item.best_paragraph)
        except:
            i = 0
        text = item.text[i:]
        if len(text) > 1000:
            ii = item.text.find(' ',i+1000)
            s += item.text[i:ii]
            s += '[...]'
        else:
            s += text
    else:
        text = item.text
        if len(text) > 1000:
            s += text[:text.find(' ',1000)]
            s += '[...]'
        else:
            s += text
    s += '\n' + item.URL + '\n\n'
    return s

class PostingsProcessor():
    def __init__(self, user):
        self.user = user
        self.valid = True
        #get all the .csv files in this folder and turn them into dataframes
        if os.getcwd().split('/')[-1] != self.user:
            print('Need to be in user folder %s' % user)
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
        self.df['text'] = self.df['text'].astype(str)
        
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
        results = []
        #for job in self.df.iterrows():
            #results.append(score_job(job[1], self.j))
        for i in range(len(self.df)):
            job = self.df.iloc[i]
            results.append(score_job(job, self.j))
        self.df = pd.DataFrame(results, columns=['title', 'URL','text','date', 'score', 'best_paragraph', 'cleaned_text'])
        self.df.sort('score',inplace=True,ascending=False)

    def send_summary(self,test=False):
        content = self.generate_user_message()
        self.send_message(content,test)
        
    def generate_user_message(self, only_bestof=True):
        if not self.valid:
            print('PostingsProcessor object is invalid; try reinstantiating')
            return
        content = '\n'
        content += '*' * 60 + '\nSearch results for "' + self.search + '", scored using word-counting\n' + '*' * 60 + '\n\n'
        content += '=' * 50 + '\n\tHighest scoring:\n'  + '=' * 50
        i = 0
        added_posts = []
        for n in range(self.sendCount):
            for post in added_posts:
                if SequenceMatcher(None, self.df.iloc[i].text, post).ratio() > 0.8:
                    i += 1
            if i < len(self.df):
                content += concat_item(self.df.iloc[i])
                added_posts.append(self.df.iloc[i].text)
                i += 1
        if not only_bestof:
            content += '\n'  + '=' * 50 + '\n\tWorst scoring:\n' + '=' * 50
            content += concat_item(self.df.iloc[-1])
            content += '\n' + '=' * 50 + '\n\tRandom entries\n'  + '=' * 50 + '\n'
            for n in range(3):
                i = random.randint(0,len(self.df)-1)
                content += concat_item(self.df.iloc[i])
        content += '\n\n\nScobble, (v.): To devour hastily.\n-Urban Dictionary'
        return content

    def send_message(self,content,test=False):
        if not self.valid:
            print('PostingsProcessor object is invalid; try reinstantiating')
            return
        service = gmail_client.get_service()
        message = CreateMessage('Bob the Job Scobbler', self.to, datetime.date.today().strftime('Jobs report for %A, %B %d, %Y'), content)
        if test:
            fname = self.user + '.email'
            with open(fname, 'w') as f:
                f.write(datetime.date.today().strftime('Jobs report for %A, %B %d, %Y\n'))
                f.write(time.ctime())
                f.write('\n\n')
                f.write(content)
            print('Email length: %d, wrote to %s' % (len(content), fname))
        else:
            SendMessage(service, 'bob.the.job.scobbler@gmail.com', message)
            print('Sent mail at ' + time.ctime())

    def save(self):
        if not self.valid:
            print('PostingsProcessor object is invalid; try reinstantiating')
            return
        fname = self.user.strip() + '_' + self.search.strip() + '.scored.csv'
        self.df.to_csv(fname)
        print('Saved %s to %s' % (fname, os.getcwd()))
    
def score_all(test=False):
    #iterate through all user folders
    os.chdir('users')
    users = os.listdir()
    for user in users:
        if not test and user == 'example':
            continue
        os.chdir(user)
        pp = PostingsProcessor(user)
        pp.process_jobs()
        pp.send_summary(test)
        if not test:
            pp.save()
        os.chdir('..')
    os.chdir('..')
    
if __name__ == '__main__':
    score_all(True)
    # todo: move towards hypothesis-testing and attribute-determining method instead of just counting tokens. then a general classifier will attempt to classify into 'boring', 'unexpected', and 'interesting'
    ## example hypotheses: this posting wants a senior developer, python is the most important language for this job, this job is temporary or part-time. e.g. predictions that have confidence intervals
    ## example attribute: lots of buzzspeak, too many exclamation marks, word or phrase is used too much. easily identified properties of the posting itself 

