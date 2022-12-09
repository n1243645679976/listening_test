import json
#with open('VCC2020-scores-JapaneseListeners.json') as f:
with open('VCC2020-scores-EnglishListeners.json') as f:
    a = json.load(f)

r = 0
dic = {}
sys_dic = {}
sample_pair_dic = {}
sample_pair_score_dic = {}
sample_pair_mean_score_dic = {}

for query in a['result']['scores']:
    if 'similarity' in query['question']['sentence'] or '類似度' in query['question']['sentence']:
        r+=1
        key = query['samples']['sample_a']['name']
        sys = key.split('-')[0]
        if key[:4] != 'ref-':
            assert int(key[-5:]) > 30000 and int(key[-5:]) <= 30005, key
        else:
            assert (int(key[-5:]) > 30020 and int(key[-5:]) <= 30025) or (int(key[-5:]) > 40020 and int(key[-5:]) <= 40025), key
        assert (int(query['samples']['sample_b']['name'][-5:]) >= 30021 and int(query['samples']['sample_b']['name'][-5:]) <= 30025) \
            or (int(query['samples']['sample_b']['name'][-5:]) >= 40021 and int(query['samples']['sample_b']['name'][-5:]) <= 40025), query['samples']['sample_b']['name']
        assert query['samples']['sample_b']['name'][:4] == 'ref-' # query reference is ground_truth
        assert query['samples']['sample_a']['name'].split('-')[1][:4] == query['samples']['sample_b']['name'].split('-')[1][:4] # check how similar to target only ( no pair compare to source

        sample_pair = query['samples']['sample_a']['name']+','+query['samples']['sample_b']['name']
        if sample_pair not in sample_pair_dic:
            sample_pair_dic[sample_pair] = 0
            sample_pair_score_dic[sample_pair] = []
        sample_pair_dic[sample_pair] += 1
        sample_pair_score_dic[sample_pair].append(query['score_value'])

        if sys not in sys_dic:
            sys_dic[sys] = 0
        if key not in dic:
            dic[key] = 0
        dic[key]+=1 
        sys_dic[sys]+=1

for key in sample_pair_dic.keys():
    if key[:4] != 'ref-':
        assert dic[key[:29]] == sample_pair_dic[key]

for _q in sorted(list(dic.keys())):
    assert dic[_q] == 4 if 'cross' in _q else 6

for _q in sorted(list(sys_dic.keys())):
    assert sys_dic[_q] == 480

with open('VCC2020-scores-JapaneseListeners.json') as f:
    a = json.load(f)

for query in a['result']['scores']:
    if 'similarity' in query['question']['sentence'] or '類似度' in query['question']['sentence']:
        r+=1
        sample_pair = query['samples']['sample_a']['name']+','+query['samples']['sample_b']['name']
        sample_pair_dic[sample_pair] -= 1
        sample_pair_score_dic[sample_pair].append(query['score_value'])

import numpy as np
np.random.seed(1006)
sys_list = list(sys_dic.keys())
sys_list.remove('ref')
np.random.shuffle(sys_list)

train_set = sys_list[:51] + ['ref']
eval_set = sys_list[:-10]

def write_score(f, key, scores):
    for score in scores:
        f.write(f'{key},{score}\n')

with open('train_list.txt', 'w+') as wtrain, open('dev_list.txt', 'w+') as wdev, open('eval_list_in_text.txt', 'w+') as weval_in, open('eval_list_out_text.txt', 'w+') as weval_out:
    for key in sample_pair_dic.keys():
        sample_pair_mean_score_dic[key] = sum(sample_pair_score_dic[key])/len(sample_pair_score_dic[key])
        sample1_num = int(key.split(',')[0][-5:])
        sample1_sys = key.split('-')[0]
        if sample1_sys in train_set:
            if sample1_num != 30005 or sample1_sys == 'ref':
                write_score(wtrain, key, sample_pair_score_dic[key])
            else:
                write_score(wdev, key, sample_pair_score_dic[key])
        else:
            if sample1_num != 30005:
                write_score(weval_in, key, sample_pair_score_dic[key])
            else:
                write_score(weval_out, key, sample_pair_score_dic[key])
        assert sample_pair_dic[key] == 0, f'key: {key} not same between JP and EN...'



print(len(list(sample_pair_dic.keys())))
        
#print(len(dic))
#print([(_q, dic[_q]) for _q in sorted(list(dic.keys()))])
#print([(_q, sys_dic[_q]) for _q in sorted(list(sys_dic.keys()))])
#print(r)
