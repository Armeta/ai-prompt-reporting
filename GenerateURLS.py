import json

topStyleQ = [
{'name':'timeframe', 'values':['MTD', 'WTD']},
{'name':'location', 'values':list(range(1,69+1))},
{'name':'metrics', 'values':['DOLLARS', 'UNITS']},
{'name':'productFamily', 'values':list(range(0,9+1))+[None]},
{'name':'week', 'values':['LW', 'TW']}
]


urls = [{}]

for metric in topStyleQ:
    addl_urls = []
    for url in urls:
        for val in metric['values']:
            if val != None:
                url[metric['name']] = val
            addl_urls.append(url)
    urls = addl_urls
for url in urls:
    queryString = json.dumps(url).replace(', ', ',').replace(': ', ':')
    url['query'] = queryString
    break

print(urls[0])

1/0

url_queries = ['{']
for metric in topStyleQ:
    addl_urls = []
    for url in url_queries:
        for val in metric['values']:
            if val == None:
                addl_urls.append(url)
            else:
                addl_urls.append(url+'"'+metric['name']+'":'+str(val)+',')
    url_queries = addl_urls
url_queries = [url[:-1]+'}' for url in url_queries]

print(url_queries[0:10])


