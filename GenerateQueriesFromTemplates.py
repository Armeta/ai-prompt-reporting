from sentence_transformers import SentenceTransformer
import json
import struct
import base64
import os
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

# add src to system path
sys.path.append('src')

from lib import code_library

modelName = 'all-distilroberta-v1'
#modelName = './LocalModel/'

templateFile = 'src/json/templates/QueryTemplatesAll.json'

incremental = False
loadSnowflake = False

connectionString = open('src/json/connection_details.json', "r")
connectionString = json.loads(connectionString.read())
session          = code_library.snowconnection(connectionString)    

model = SentenceTransformer(modelName)

f = open(templateFile)
templates = json.load(f)['templates']
f.close()

outputpath = 'src/outputs/all-distilroberta-v1/'
if(modelName == './LocalModel/'):
    outputpath = 'src/outputs/LocalModel/'

ops = open('src/outputs/GeneratedOptions.txt', 'w')
#ak = open('src/json/answerKey.csv', 'w')

stageQ = open(outputpath+'toStageQuery.csv', 'w')
stageQ.write('DESC|DASHBOARD|QUERY|ENCODING|ENCODING_JSON\n')

stageD = open(outputpath+'toStageDashboard.csv', 'w')
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

        ops.write(newDesc+'\n')
        #ak.write(newQuestion+'|'+newDesc+'\n')

        #DESC, DASHBOARD, QUERY, ENCODING, ENCODING_JSON
        stageQ.write('%s|%s|%s|%s|%s\n' % (newDesc, template['category'], newQuery, enc_bin, enc_json))
        
        #DESC, DASHBOARD, URL, ENCODING, ENCODING_JSON, FILTER, QUERY
        stageD.write('%s|%s|%s|%s|%s|%s|%s\n' % (newDesc, template['category'], newURL, enc_bin, enc_json, newURLFilter, newURLQuery))

        if(len(paramCount) > 0):
            paramCount[0] += 1
            for i in range(len(paramCount)):
                if(paramCount[i] >= paramMaxCount[i]):
                    if(i == len(paramCount)-1):
                        done = True
                    else:
                        paramCount[i+1] += 1
                        paramCount[i] = 0
        else:
            done = True

        count += 1
        if(count % 100 == 0):
            print(count)

stageQ.close()
stageD.close()
print('Generated %d options' % (count))

if loadSnowflake:
    tableDashboard = 'OptionsDashboard'
    tableQuery = 'OptionsQuery'
    if modelName == './LocalModel/':
        tableDashboard = 'OptionsDashboardLocal'
        tableQuery = 'OptionsQueryLocal'

    print('Using tables %s, %s' % (tableDashboard, tableQuery))

    if not incremental:
        print('Truncating Existing Tables...')
        session.sql('TRUNCATE TABLE MODEL."%s";' % (tableDashboard)).collect()
        session.sql('TRUNCATE TABLE MODEL."%s";' % (tableQuery)).collect()

    print('Clearing Stages...')
    session.sql('REMOVE @dashboard_option_stage;').collect()
    session.sql('REMOVE @query_option_stage;').collect()

    print('Uploading Stages...')
    session.sql('PUT file://%s/%stoStageDashboard.csv @dashboard_option_stage;' % (str(os.getcwd()), outputpath)).collect()
    session.sql('PUT file://%s/%stoStageQuery.csv @query_option_stage;' % (str(os.getcwd()), outputpath)).collect()

    print('Loading Stages Into Tables...')
    session.sql('COPY INTO "MODEL"."%s" (DESC, DASHBOARD, URL, ENCODING, ENCODING_JSON, FILTER, QUERY) FROM @dashboard_option_stage file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');' % (tableDashboard)).collect()
    session.sql('COPY INTO "MODEL"."%s" (DESC, DASHBOARD, QUERY, ENCODING, ENCODING_JSON) FROM @query_option_stage file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');' % (tableQuery)).collect()
