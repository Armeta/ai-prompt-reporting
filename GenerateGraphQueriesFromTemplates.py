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

#modelName = 'all-distilroberta-v1'
modelName = './LocalModel/'

templateFile = 'src/json/templates/GraphTemplates.json'

incremental = False
loadSnowflake = True

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

stageG = open(outputpath + 'toStageGraph.csv', 'w')
stageG.write('DESC|QUERY|ENCODING|ENCODING_JSON\n')

count = 0

for template in templates:
    paramCount = [0 for param in template['parameters']]
    paramMaxCount = [len(param['values']) for param in template['parameters']]
    done = False
    while not done:

        newQuestion  = template['question']
        newDesc      = template['desc']
        newQuery     = template['query']

        for p in range(len(template['parameters'])):
            newQuestion = newQuestion.replace(template['parameters'][p]['name'], template['parameters'][p]['values'][paramCount[p]])
            newDesc = newDesc.replace(template['parameters'][p]['name'], template['parameters'][p]['values'][paramCount[p]])
            newQuery = newQuery.replace(template['parameters'][p]['name'], template['parameters'][p]['values'][paramCount[p]])

        enc      = model.encode(newDesc).tolist()
        enc_json = '{"encoding": '+str(enc)+'}'
        enc_bin  = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])

        ops.write(newDesc+'\n')
        #ak.write(newQuestion+'|'+newDesc+'\n')

        #DESC, QUERY, ENCODING, ENCODING_JSON
        stageG.write('%s|%s|%s|%s\n' % (newDesc, newQuery, enc_bin, enc_json))        
 
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

stageG.close()
print('Generated %d options' % (count))

if loadSnowflake:
    tableGraph = 'OPTIONS_GRAPH'

    print('Using tables %s' % (tableGraph))

    if not incremental:
        print('Truncating Existing Tables...')
        session.sql('TRUNCATE TABLE MODEL."%s";' % (tableGraph)).collect()

    print('Clearing Stages...')
    session.sql('REMOVE @GRAPH_OPTION_STAGE;').collect()

    print('Uploading Stages...')
    session.sql('PUT file://%s/%stoStageGraph.csv @GRAPH_OPTION_STAGE;' % (str(os.getcwd()), outputpath)).collect()

    print('Loading Stages Into Tables...')
    session.sql('COPY INTO "MODEL"."%s" (DESC, QUERY, ENCODING, ENCODING_JSON) FROM @GRAPH_OPTION_STAGE file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');' % (tableGraph)).collect()
