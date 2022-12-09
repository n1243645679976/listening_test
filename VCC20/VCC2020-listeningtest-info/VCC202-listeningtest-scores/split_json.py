import json
a = {}
for files in ['VCC2020-scores-JapaneseListeners.json', 'VCC2020-scores-EnglishListeners.json']:
    with open(files) as f:
    #with open('VCC2020-scores-EnglishListeners.json') as f:
        b = json.load(f)
    r = 0
    dic = {}
    sys_dic = {}
    for query in a['result']['scores']:
        if 'similarity' in query['question']['sentence'] or '類似度' in query['question']['sentence']:
            r+=1
            key = query['samples']['sample_a']['name']
            sys = key.split('-')[0]
            assert query['samples']['sample_b']['name'][:4] == 'ref-' # query reference is ground_truth
            if 'cross' not in query['samples']['sample_a']['name']:
                print(query['samples']['sample_a']['name'][-10:], query['samples']['sample_b']['name'][-10:])
    
            if sys not in sys_dic:
                sys_dic[sys] = 0
            if key not in dic:
                dic[key] = 0
            dic[key]+=1 
            sys_dic[sys]+=1
    
    for _q in sorted(list(dic.keys())):
        assert dic[_q] == 8 if 'cross' in _q else 12, (_q, dic[_q])
    
    for _q in sorted(list(sys_dic.keys())):
        assert sys_dic[_q] == 960
#print(len(dic))
#print([(_q, dic[_q]) for _q in sorted(list(dic.keys()))])
#print([(_q, sys_dic[_q]) for _q in sorted(list(sys_dic.keys()))])
#print(r)
