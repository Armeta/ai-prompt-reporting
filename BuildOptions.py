from sentence_transformers import SentenceTransformer
import json
import struct
import base64
import os
import datetime
import   sys
from     snowflake.snowpark           import Session
from     snowflake.snowpark.functions import col, to_timestamp
from     snowflake.snowpark.types     import IntegerType, StringType, StructField, StructType, DateType,LongType,DoubleType

# add src to system path
sys.path.append('src')

from lib import code_library


def main(templateFilename = 'AllTemplates.json', useBaseModel = True, incrementalLoad = True, loadSnowflake = False, runQueries = False):
    
    # load template json
    templateFile = open('src/json/'+templateFilename)
    templateJSON = json.load(templateFile)
    templates = templateJSON['templates']
    paramLists = templateJSON['parameterLists']
    templateFile.close()

    # load model
    baseModelName = 'all-distilroberta-v1'
    if(useBaseModel):
        modelName = baseModelName
    else:
        modelName = './LocalModel/'
    model = SentenceTransformer(modelName)

    # prepare output files
    ak = open('src/csv/answerKey.csv', 'w')
    ak.write(str(datetime.datetime.now())+'\n')
    stageQ = None
    stageD = None
    if(loadSnowflake):
        stageQ = open('toStageQuery.csv', 'w')
        stageQ.write('DESC|DASHBOARD|QUERY|ENCODING|ENCODING_JSON|RESULT_CACHE\n')
        stageD = open('toStageDashboard.csv', 'w')
        stageD.write('DESC|DASHBOARD|URL|ENCODING|ENCODING_JSON|FILTER|QUERY\n')
        session = code_library.snowconnection()    


    count = 0

    for template in templates:
        paramCount = [0 for param in template['parameters']]
        paramMaxCount = [len(paramLists[param]['descriptionValues']) for param in template['parameters']]
        done = False
        while not done: # for each parameter combination

            # base options
            newDesc = template['desc']
            newQuestions = template['questions']
            newQuery = template['query']
            newURL = 'https://ip.armeta.com/snowflake/analytics/'+template['urlpage']
            newURLFilter = template['urlfilter']
            newURLQuery = template['urlquery']

            # replace parameter placeholders with values
            for p in range(len(template['parameters'])):
                paramName = template['parameters'][p]
                DescParam = paramLists[paramName]['descriptionValues'][paramCount[p]]
                QuestionParam = paramLists[paramName]['questionValues'][paramCount[p]]
                queryParam = paramLists[paramName]['queryValues'][paramCount[p]]
                urlParam = paramLists[paramName]['urlValues'][paramCount[p]]

                newDesc = newDesc.replace(paramName, DescParam)
                newQuestions = [newQuestion.replace(paramName, QuestionParam) for newQuestion in newQuestions]
                newQuery = newQuery.replace(paramName, queryParam)
                newURLFilter = newURLFilter.replace(paramName, urlParam)
                newURLQuery = newURLQuery.replace(paramName, urlParam)
            
            if(newURLFilter != '' and newURLQuery != ''):
                newURL = newURL + '?filter=' + str(base64.b64encode(newURLFilter.encode("ascii")))[2:-1].replace('=', '%3D') + '&query=' + str(base64.b64encode(newURLQuery.encode("ascii")))[2:-1].replace('=', '%3D')
            elif(newURLFilter != ''):
                newURL = newURL + '?filter=' + str(base64.b64encode(newURLFilter.encode("ascii")))[2:-1].replace('=', '%3D')
            elif(newURLQuery != ''):
                newURL = newURL + '?query=' + str(base64.b64encode(newURLQuery.encode("ascii")))[2:-1].replace('=', '%3D')


            # output question variations with answers
            for newQuestion in newQuestions:
                ak.write(newQuestion+'|'+newDesc+'\n')

            # append to stage file if loading to snowflake
            if(loadSnowflake):
                enc = model.encode(newDesc).tolist()
                enc_json = '{"encoding": '+str(enc)+'}'
                enc_bin = ''.join([''.join(['%02x' % (b) for b in bytearray(struct.pack('d', d))]) for d in enc])

                query_cache = 'NULL'
                if(runQueries):
                    query_cache = session.sql(newQuery).collect()
                    if(len(query_cache) == 0 or query_cache[0] == None):
                        query_cache = 'No results'
                    elif(len(query_cache[0]) == 0 or query_cache[0][0] == None):
                        query_cache = 'No results'
                    else:
                        query_cache = query_cache[0][0]
                    
                #DESC, DASHBOARD, QUERY, ENCODING, ENCODING_JSON, RESULT_CACHE
                stageQ.write('%s|%s|%s|%s|%s|%s\n' % (newDesc, template['urlpage'], newQuery, enc_bin, enc_json, query_cache))
                #DESC, DASHBOARD, URL, ENCODING, ENCODING_JSON, FILTER, QUERY
                stageD.write('%s|%s|%s|%s|%s|%s|%s\n' % (newDesc, template['urlpage'], newURL, enc_bin, enc_json, newURLFilter, newURLQuery))

            # get next combination of parameters
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

            # progress tracker
            count += 1
            if(count % 100 == 0):
                print(count)

    # finished generating options
    ak.close()
    print('Generated %d options' % (count))

    # load staged records
    if loadSnowflake:
        stageQ.close()
        stageD.close()
        schema = 'PC'
        tableDashboard = 'OPTIONS_DASHBOARD'
        tableQuery = 'OPTIONS_QUERY'
        stageDashboard = '@PC.PC_DASHBOARD_OPTION_STAGE'
        stageQuery = '@PC.PC_QUERY_OPTION_STAGE'

        print('Using tables %s, %s' % (schema+'.'+tableDashboard, schema+'.'+tableQuery))

        if not incrementalLoad:
            print('Truncating Existing Tables...')
            session.sql('TRUNCATE TABLE %s."%s";' % (schema, tableDashboard)).collect()
            session.sql('TRUNCATE TABLE %s."%s";' % (schema, tableQuery)).collect()

        print('Clearing Stages...')
        session.sql('REMOVE %s;' % (stageDashboard)).collect()
        session.sql('REMOVE %s;' % (stageQuery)).collect()

        print('Uploading Stages...')
        session.sql('PUT file://%s/toStageDashboard.csv %s;' % (str(os.getcwd()), stageDashboard)).collect()
        session.sql('PUT file://%s/toStageQuery.csv %s;' % (str(os.getcwd()), stageQuery)).collect()

        print('Loading Stages Into Tables...')
        session.sql('COPY INTO %s.%s (DESC, DASHBOARD, URL, ENCODING, ENCODING_JSON, FILTER, QUERY) FROM %s file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');' % (schema, tableDashboard, stageDashboard)).collect()
        session.sql('COPY INTO %s.%s (DESC, DASHBOARD, QUERY, ENCODING, ENCODING_JSON, RESULT_CACHE) FROM %s file_format = (type = \'CSV\' SKIP_HEADER = 1 FIELD_DELIMITER = \'|\');' % (schema, tableQuery, stageQuery)).collect()

        os.remove('toStageDashboard.csv')
        os.remove('toStageQuery.csv')


if __name__ == '__main__':
    main(incrementalLoad = False, loadSnowflake = True, runQueries = True)
