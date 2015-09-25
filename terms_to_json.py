import json

def convert(fname, test=False):
    with open(fname,'r') as f:
        d = {}
        order = ['email','search','delivery', 'send', 'keywords_important', 'keywords_positive', 
                 'keywords_good', 'keywords_meh', 'keywords_negative']
        i = 0
        for line in f:
            line = line.split(':')
            name = line[0].split(' ')[0].strip()
            # ensure that there's a ':' in this line, and that everything's in order
            if len(line) > 1 and name == order[i]:
                d[name] = line[1].strip().split(',')
                if len(d[name]) > 1:
            #do cleanup, especially for keywords this is important for checking for 
            #multiple versions of the same word. space at the beginning is so no keyword
            #will match if it is wholly contained inside a larger word, no space at the end
            #is to allow for plurals
                    for ii in range(len(d[name])):
                        d[name][ii] = d[name][ii].strip()
                        d[name][ii] = ' ' + d[name][ii]
                i += 1
            elif len(line) > 1:
                print('File out of order: "%s" should be "%s"' % (name, order[i]))
                break
        content = json.dumps(d)
        fname_out = fname.replace('.txt','') + '.json'
        if test:
            print('completed test conversion for %s' % fname)
        else:
            with open(fname_out, 'w') as f_out:
                f_out.write(content)
                print('wrote to %s' % fname_out)

