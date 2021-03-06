'''
Control flow for the program.

TODO: provide more granularity for errors and flexibility for using outside of a cronjob.
'''

import os
import sys

test = False
had_error = False
wd_start = os.getcwd()
if test:
    print('~~~handler.py test~~~')
else:
    print('~~~handler.py~~~')
print('~user updater~')
try:
    import user_updater
    user_updater.update(test)
except:
    had_error = True
    print('user_updater.py had an error')
    e = sys.exc_info()
    fname = os.path.split(e[2].tb_frame.f_code.co_filename)[1]
    print(e[0], fname, e[2].tb_lineno)
os.chdir(wd_start)
print('~web wrangler~')
try:
    import web_wrangler
    web_wrangler.wrangle(test)
except:
    had_error = True
    print('web_wrangler.py had an error')
    e = sys.exc_info()
    fname = os.path.split(e[2].tb_frame.f_code.co_filename)[1]
    print(e[0], fname, e[2].tb_lineno)
os.chdir(wd_start)
print('~job scorer~')
try:
    import job_scorer
    job_scorer.score_all(test)
except:
    had_error = True
    print('job_scorer.py had an error')
    e = sys.exc_info()
    fname = os.path.split(e[2].tb_frame.f_code.co_filename)[1]
    print(e[0], fname, e[2].tb_lineno)
os.chdir(wd_start)

if not had_error:
    print('~emailer~')
    try:
        import gmail_client
        gmail_client.send_all()
    except:
        had_error = True
        print('gmail_client.py had an error')
        e = sys.exc_info()
        fname = os.path.split(e[2].tb_frame.f_code.co_filename)[1]
        print(e[0], fname, e[2].tb_lineno)

if had_error:
   print("Somebody has got to get these monkey flippin' errors off this Monday-to-Friday software!") #TODO send a special email
else:
    print('Completed with no errors, handler.py checking out')
