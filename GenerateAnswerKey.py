from sentence_transformers import SentenceTransformer
import json
import datetime
import struct
import base64


f = open('src/json/AnswerTemplates.json')
jsonFile = json.load(f)
templates = jsonFile['templates']
paramLists = jsonFile['parameterLists']
f.close()

ak = open('src/outputs/answerKey.csv', 'w')
ak.write(str(datetime.datetime.now())+'\n')

qs = open('src/outputs/GeneratedQuestions.txt', 'w')

count = 0

for template in templates:
    paramCount = [0 for param in template['parameters']]
    paramMaxCount = [len(paramLists[param]['values']) for param in template['parameters']]
    done = False
    while not done:

        newQuestion = template['question']
        newDesc = template['desc']

        for p in range(len(template['parameters'])):
            
            DescParam = paramLists[template['parameters'][p]]['values'][paramCount[p]]
            QuestionParam = paramLists[template['parameters'][p]]['questionValues'][paramCount[p]]
            #template['parameters'][p]['values'][paramCount[p]]

            newQuestion = newQuestion.replace(template['parameters'][p], QuestionParam)
            newDesc = newDesc.replace(template['parameters'][p], DescParam)
        
        ak.write(newQuestion+'|'+newDesc+'\n')
        qs.write(newQuestion+'\n')

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

ak.close()
qs.close()
print('Generated %d questions' % (count))
