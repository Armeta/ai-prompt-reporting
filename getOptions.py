import json

f = open('src/json/answerKey.json','r')
key = json.load(f)
f.close()
f = open('src/json/Options.json','r')
options = json.load(f)
f.close()

"""
pages = []
for pair in key['pairs']:
    if(pair['ans'][:5] == 'https'):
        if(pair['ans'].find('?') > 0):
            page = pair['ans'][37:pair['ans'].find('?')]
        else:
            page = pair['ans'][37:]
        if page not in pages:
            pages.append(page)
print(pages)
"""

pagesDesc = {'sales-retail':'Analysis of sales data showing ',
             'sales-opportunity':'Potential sales opportunity ',
             'sales-compare':'Comparing revenue, item on hand cost, item on hand value, and item on hand units against each other ',
             'sales-digital':'Digital website metrics, such as conversion rate and average order value by site ',
             'analysis-product':'Insight on how certain products are selling ',
             'location-review':'Sales and inventory for specific locations and stores ',
             'top-styles':'Highlighting the top products at a specified location '}

prefixes = ['What was the ', 'What are the ', 'What is the ', 'What\'s the', 'Whats the ', 'What are ', 'What ', 'How are the ', 'How often do ', 'How many ', 'How does ', 'How do ', 'I need to ', 'Show me ', 'Which ']
count = 0
for pair in key['pairs']:
    if(pair['ans'][:5] == 'https'):
        if(pair['ans'].find('?') > 0):
            page = pair['ans'][37:pair['ans'].find('?')]
        else:
            page = pair['ans'][37:]
        pageDesc = pagesDesc[page]

        promptDesc = ''
        for prefix in prefixes:
            if(pair['prompt'].find(prefix) == 0):
                promptDesc = pageDesc + (pair['prompt'].replace(prefix, '').replace('?', '.'))
                break
        if(promptDesc == ''):
            print(pair['prompt'])
        else:
            options['options'].append({'type': 'url','url': pair['ans'], 'desc': promptDesc, 'encoding':None})
            count += 1

f = open('src/json/Options.json','w')
f.write(json.dumps(options).replace('{', '\n{').replace('",', '",\n').replace('"}', '"\n}'))
f.close()

print('Added %d options' % (count))