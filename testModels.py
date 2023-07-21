from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import datetime

modelsToTest = ['bert-base-nli-mean-tokens', 'all-mpnet-base-v2']

#model = SentenceTransformer('bert-base-nli-mean-tokens') # try other models

f = open('Options.json','r')
options = json.load(f)
f.close()
f = open('AnswerKey.json','r')
answers = json.load(f)
f.close()

results = {}

opt_url = [option['url'] for option in options['options']]
opt_desc = [option['desc'] for option in options['options']]
tst_prompt = [answer['prompt'] for answer in answers['pairs']]
tst_url = [answer['url'] for answer in answers['pairs']]

for modelName in modelsToTest:
    model = SentenceTransformer(modelName)
    results[modelName] = {'score': 0.0, 'time': None, 'results':[]}
    starttime = datetime.datetime.now()

    optEncodings = model.encode(opt_desc)
    for prompt, url in zip(tst_prompt, tst_url):
        promptEncoding = model.encode(prompt)
        sim = cosine_similarity([promptEncoding], optEncodings)
        guess_url = opt_url[sim[0].tolist().index(max(sim[0]))]
        if(guess_url == url):
            results[modelName]['score'] += 1
        results[modelName]['results'].append([guess_url == url, prompt, guess_url])
    results[modelName]['score'] /= len(tst_prompt)
    endtime = datetime.datetime.now()
    results[modelName]['time'] = (endtime-starttime).seconds

f = open('TestResults.json','w')
f.write(json.dumps(results, indent=4).replace('{', '\n{').replace(',', ',\n').replace('}', '\n}'))
f.close()