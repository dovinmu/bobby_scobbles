# Bob the Job Scobbler

     Scobble, (v.): To devour hastily.
          -Urban Dictionary

Job boards crawler that emails top-ranked job postings.


Dependencies:
 * pandas
 * BeautifulSoup
 * httplib2
 * eventlet
 * Google API Client for Python (if you want to have email integration)
 
Usage:
 * Overall program flow is in handler.py.
 * If you want the service to email you, you'll need to set up your own Gmail credentials 
   (https://developers.google.com/gmail/api/) or other email method.

Scoring method:
 * For each keyword in each keyword category, check if that keyword is contained in the 
   body of the job posting and add the weight of that keyword category to the total score.
   Current keyword categories are: important, positive, good, meh, and negative; with a current 
   weight of 4, 1, 0.25, -0.25, and -1, respectively. So for example if I have the keyword
   'pizza' in the important keywords, I add 4 to the score of whatever job the word 'pizza' 
   appears in.
 * Score each job posting per paragraph to find the most interesting paragraph, giving a modest
   score bonus to longer paragraphs of up to 1 point. Then divide the total score by the 
   number of paragraphs to not favor extremely long posts (or garbage from improper scraping).

