from sentence_transformers import SentenceTransformer
import json
import struct
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

model = SentenceTransformer('all-distilroberta-v1')

f = open('src/json/QueryTemplates2.json')
templates = json.load(f)['templates']
f.close()

qs = open('GeneratedQuestions.txt', 'w')
#ak = open('src/json/answerKey.csv', 'w')

stageQ = open('toStageQuery.csv', 'w')
stageQ.write('DESC|DASHBOARD|QUERY|ENCODING|ENCODING_JSON\n')

stageD = open('toStageDashboard.csv', 'w')
stageD.write('DESC|DASHBOARD|URL|ENCODING|ENCODING_JSON|FILTER|QUERY\n')


count = 0

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
        
        if(newURLFilter != '' and newURLQuery != ''):
            newURL = newURL + '?filter=' + str(base64.b64encode(newURLFilter.encode("ascii")))[2:-1].replace('=', '%3D') + '&query=' + str(base64.b64encode(newURLQuery.encode("ascii")))[2:-1].replace('=', '%3D')
        elif(newURLFilter != ''):
            newURL = newURL + '?filter=' + str(base64.b64encode(newURLFilter.encode("ascii")))[2:-1].replace('=', '%3D')
        elif(newURLQuery != ''):
            newURL = newURL + '?query=' + str(base64.b64encode(newURLQuery.encode("ascii")))[2:-1].replace('=', '%3D')

        enc = model.encode(newDesc).tolist()
        enc_json = '{"encoding": '+str(enc)+'}'
        enc_bin = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])

        qs.write(newQuestion+'\n')
        #ak.write(newQuestion+'|'+newDesc+'\n')

        #DESC, DASHBOARD, QUERY, ENCODING, ENCODING_JSON
        stageQ.write('%s|%s|%s|%s|%s\n' % (newDesc, template['category'], newQuery, enc_bin, enc_json))
        
        #DESC, DASHBOARD, URL, ENCODING, ENCODING_JSON, FILTER, QUERY
        stageD.write('%s|%s|%s|%s|%s|%s|%s\n' % (newDesc, template['category'], newURL, enc_bin, enc_json, newURLFilter, newURLQuery))

        paramCount[0] += 1
        for i in range(len(paramCount)):
            if(paramCount[i] >= paramMaxCount[i]):
                if(i == len(paramCount)-1):
                    done = True
                else:
                    paramCount[i+1] += 1
                    paramCount[i] = 0

        count += 1
        if(count % 100 == 0):
            print(count)

qs.close()
stageQ.close()
stageD.close()
print('Generated %d options' % (count))


print('uploading stages...')
session.sql('PUT file://C:/Users/JonathanWhite/source/repos/Armeta/ai-prompt-reporting/toStageDashboard.csv @dashboard_option_stage;').collect()
print('Uplaoded Dashboards')
session.sql('PUT file://C:/Users/JonathanWhite/source/repos/Armeta/ai-prompt-reporting/toStageQuery.csv @query_option_stage;').collect()
print('Uplaoded Queries')
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