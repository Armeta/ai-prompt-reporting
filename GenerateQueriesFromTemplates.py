import json
import base64
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

# add src to system path
sys.path.append('src')

from lib import code_library

connectionString = open('src/json/connection_details.json', "r")
connectionString = json.loads(connectionString.read())
session          = code_library.snowconnection(connectionString)    


f = open('src/json/QueryTemplates.json')
templates = json.load(f)['templates']
f.close()

qs = open('GeneratedQuestions.txt', 'w')

id = 1000

for template in templates:
    paramCount = [0 for param in template['parameters']]
    paramMaxCount = [len(param['values']) for param in template['parameters']]
    done = False
    while not done:

        newQuestion = template['question']
        newDesc = template['desc']
        newQuery = template['query']
        newURL = 'https://ip.armeta.com/snowflake/analytics/'+template['category']
        newURLFilter = template['urlfilter']
        newURLQuery = template['urlquery']

        for p in range(len(template['parameters'])):
            newQuestion = newQuestion.replace(template['parameters'][p]['name'], template['parameters'][p]['values'][paramCount[p]])
            newDesc = newDesc.replace(template['parameters'][p]['name'], template['parameters'][p]['values'][paramCount[p]])
            newQuery = newQuery.replace(template['parameters'][p]['name'], template['parameters'][p]['values'][paramCount[p]])

            newURLFilter = newURLFilter.replace(template['URLparameters'][p]['name'], str(template['URLparameters'][p]['values'][paramCount[p]]))
            newURLQuery = newURLQuery.replace(template['URLparameters'][p]['name'], str(template['URLparameters'][p]['values'][paramCount[p]]))
        #newQuery = newQuery.replace('\'', '\'\'')
        if(newURLFilter != '' and newURLQuery != ''):
            newURL = newURL + '?filter=' + str(base64.b64encode(newURLFilter.encode("ascii")))[2:-1].replace('=', '%3D') + '&query=' + str(base64.b64encode(newURLQuery.encode("ascii")))[2:-1].replace('=', '%3D')
        elif(newURLFilter != ''):
            newURL = newURL + '?filter=' + str(base64.b64encode(newURLFilter.encode("ascii")))[2:-1].replace('=', '%3D')
        elif(newURLQuery != ''):
            newURL = newURL + '?query=' + str(base64.b64encode(newURLQuery.encode("ascii")))[2:-1].replace('=', '%3D')

        insertQuery = 'INSERT INTO MODEL."OptionsQuery" (SK, DESC, DASHBOARD, QUERY) VALUES(%d,\'%s\',\'%s\',\'%s\')' % (id, newDesc, template['category'], newQuery)
        insertDashboard = 'INSERT INTO MODEL."OptionsDashboard" (SK, DESC, DASHBOARD, URL) VALUES(%d,\'%s\',\'%s\',\'%s\')' % (id, newDesc, template['category'], newURL)

        qs.write(newQuestion+'\n')
        session.sql(insertQuery).collect()
        session.sql(insertDashboard).collect()

        paramCount[0] += 1
        for i in range(len(paramCount)):
            if(paramCount[i] >= paramMaxCount[i]):
                if(i == len(paramCount)-1):
                    done = True
                else:
                    paramCount[i+1] += 1
                    paramCount[i] = 0

        id += 1

qs.close()
print('Generated %d options' % (id-1000))

"""
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


"""