import os
from terms_to_json import convert

def update(test=False):
    os.chdir('users')
    users = os.listdir()
    for user in users:
        os.chdir(user)
        files = os.listdir()
        #TODO: check email to see if the user has sent a new keywords file


        #convert keyword file to .json equivalent
        txts = [x for x in files if '.txt' in x and '~' not in x]
        if len(txts) > 1:
            print("Error! more than one .txt file in %s"%user)
        elif len(txts) == 0:
            print("No .txt file in %s"%user)
        else:
            with open(txts[0]) as f:
                convert(f.read().split('\n'),user,test=test)
        os.chdir('..')
    os.chdir('..')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        update(sys.argv[1] == 'test')
    else:
        update()
