from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import datetime

modelsToTest = ['bert-base-nli-mean-tokens', 'all-mpnet-base-v2', 'all-distilroberta-v1', 'all-MiniLM-L12-v2', 'multi-qa-distilbert-cos-v1', 'all-MiniLM-L6-v2', 'multi-qa-MiniLM-L6-cos-v1', 'paraphrase-albert-small-v2', 'paraphrase-MiniLM-L3-v2']


f = open('json\\Options.json','r')
optionsDash = json.load(f)
f.close()
f = open('json\\QueryOptions.json','r')
optionsQuery = json.load(f)
f.close()
f = open('json\\answerKey.json','r')
answers = json.load(f)
f.close()

results = {}

dash_opts = [option['url'] for option in optionsDash['options']]
dash_desc = [option['desc'] for option in optionsDash['options']]
query_opts = [option['query'] for option in optionsQuery['options']]
query_desc = [option['desc'] for option in optionsQuery['options']]
test_pairs = [(pair['prompt'], pair['ans']) for pair in answers['pairs']]


for modelName in modelsToTest:
    model = SentenceTransformer(modelName)
    results[modelName] = {'score': 0.0, 'time': None, 'results':[]}
    starttime = datetime.datetime.now()

    dashEncodings = model.encode(dash_desc)
    queryEncodings = model.encode(query_desc)
    for prompt, ans in test_pairs:
        promptEncoding = model.encode(prompt)
        if(ans[:5] == 'https'): # dashboard
            sim = cosine_similarity([promptEncoding], dashEncodings)
            guess = dash_opts[sim[0].tolist().index(max(sim[0]))]
        else: # query
            sim = cosine_similarity([promptEncoding], queryEncodings)
            guess = query_opts[sim[0].tolist().index(max(sim[0]))]
        if(guess == ans):
            results[modelName]['score'] += 1
        results[modelName]['results'].append([guess == ans, prompt, guess])
    results[modelName]['score'] /= len(test_pairs)
    endtime = datetime.datetime.now()
    results[modelName]['time'] = (endtime-starttime).seconds
    print('%2.0f%% %s' % (results[modelName]['score']*100, modelName))


f = open('json\\TestResults.json','w')
f.write(json.dumps(results, indent=4))
f.close()
