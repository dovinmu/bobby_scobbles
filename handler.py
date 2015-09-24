#TODO: web wrangling might need to be in a separate script file

import os
import sys

had_error = False
wd_start = os.getcwd()
print('running handler.py')

try:
    import user_updater
    user_updater.update()
except:
    had_error = True
    print('user_updater.py had an error')
    e = sys.exc_info()
    print(e)
os.chdir(wd_start)

try:
    import web_wrangler
    web_wrangler.wrangle()
except:
    had_error = True
    print('web_wrangler.py had an error')
    e = sys.exc_info()
    print(e)
os.chdir(wd_start)

try:
    import job_scorer
    job_scorer.score_all()
except:
    had_error = True
    print('job_scorer.py had an error')
    e = sys.exc_info()
    print(e)
os.chdir(wd_start)

if had_error:
   print("Somebody has got to get these monkey flippin' errors off this Monday-to-Friday software!") #TODO send a special email
else: 
    print('completed with no errors, handler.py checking out')


