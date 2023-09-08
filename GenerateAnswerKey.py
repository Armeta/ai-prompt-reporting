from sentence_transformers import SentenceTransformer
import json
import struct
import base64


f = open('src/json/AnswerTemplates.json')
templates = json.load(f)['templates']
f.close()

ak = open('src/outputs/answerKey.csv', 'w')

qs = open('src/outputs/GeneratedQuestions.txt', 'w')

count = 0

for template in templates:
    paramCount = [0 for param in template['parameters']]
    paramMaxCount = [len(param['values']) for param in template['parameters']]
    done = False
    while not done:

        newQuestion = template['question']
        newDesc = template['desc']

        for p in range(len(template['parameters'])):
            DescParam = template['parameters'][p]['values'][paramCount[p]]
            QuestionParam = template['parameters'][p]['values'][paramCount[p]]

            newQuestion = newQuestion.replace(template['parameters'][p]['name'], QuestionParam)
            newDesc = newDesc.replace(template['parameters'][p]['name'], DescParam)
        
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
