from sentence_transformers import SentenceTransformer
import json
import struct
import base64

model = SentenceTransformer('all-distilroberta-v1')

f = open('src/json/AnswerTemplates.json')
templates = json.load(f)['templates']
f.close()

ak = open('src/json/answerKey.csv', 'w')


count = 0

for template in templates:
    paramCount = [0 for param in template['DescParameters']]
    paramMaxCount = [len(param['values']) for param in template['DescParameters']]
    done = False
    while not done:

        newQuestion = template['question']
        newDesc = template['desc']

        for p in range(len(template['DescParameters'])):
            DescParam = template['DescParameters'][p]['values'][paramCount[p]]
            QuestionParam = template['QuestionParameters'][p]['values'][paramCount[p]]

            newQuestion = newQuestion.replace(template['DescParameters'][p]['name'], QuestionParam)
            newDesc = newDesc.replace(template['DescParameters'][p]['name'], DescParam)
        
        ak.write(newQuestion+'|'+newDesc+'\n')

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

ak.close()
print('Generated %d questions' % (count))
