import json
f = open('json\\Options.json','r')
options = json.load(f)
f.close()
f = open('json\\answerKey.json','r')
answers = json.load(f)
f.close()


opts = [option['url'] if option['type'] == 'url' else option['query'] for option in options['options']]
tst_ans = [answer['ans'] for answer in answers['pairs']]

missing = []

for a in tst_ans:
    if a not in opts and a not in missing:
        missing.append(a)
        print(a)


