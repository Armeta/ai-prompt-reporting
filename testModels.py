from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import datetime

modelsToTest = ['bert-base-nli-mean-tokens', 'all-mpnet-base-v2', 'all-distilroberta-v1', 'all-MiniLM-L12-v2', 'multi-qa-distilbert-cos-v1', 'all-MiniLM-L6-v2', 'multi-qa-MiniLM-L6-cos-v1', 'paraphrase-albert-small-v2', 'paraphrase-MiniLM-L3-v2']


f = open('json\\Options.json','r')
options = json.load(f)
f.close()
f = open('json\\answerKey.json','r')
answers = json.load(f)
f.close()

results = {}

opts = [option['url'] if option['type'] == 'url' else option['query'] for option in options['options']]
opt_desc = [option['desc'] for option in options['options']]
tst_prompt = [answer['prompt'] for answer in answers['pairs']]
tst_ans = [answer['ans'] for answer in answers['pairs']]

for modelName in modelsToTest:
    model = SentenceTransformer(modelName)
    results[modelName] = {'score': 0.0, 'time': None, 'results':[]}
    starttime = datetime.datetime.now()

    optEncodings = model.encode(opt_desc)
    for prompt, ans in zip(tst_prompt, tst_ans):
        promptEncoding = model.encode(prompt)
        sim = cosine_similarity([promptEncoding], optEncodings)
        guess = opts[sim[0].tolist().index(max(sim[0]))]
        if(guess == ans):
            results[modelName]['score'] += 1
        results[modelName]['results'].append([guess == ans, prompt, guess])
    results[modelName]['score'] /= len(tst_prompt)
    endtime = datetime.datetime.now()
    results[modelName]['time'] = (endtime-starttime).seconds
    print('%2.0f%% %s' % (results[modelName]['score']*100, modelName))


f = open('json\\TestResults.json','w')
f.write(json.dumps(results, indent=4))
f.close()
