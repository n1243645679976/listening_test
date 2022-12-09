import json
import numpy as np
import os

##run from the main function

def prev_setting(prev):
    if prev == 'en':
        lang = 'English'                  #Test for English listeners
        exp_id = 'Oa6njJozBbP9'           #Experiment ID , no need to change this
        test_id = '5dGKjR5KqEYV'            ##Test  ID, no need to change this
        exp_manifest_id_1 = '3aW7q2AMO5V2' #question id for the first question (quality evaluation)
        exp_manifest_id_2 = 'WKL5qMLbOM9g' #question id for the second question (similarity evaluation)
        resfile = 'VCC2020-scores-EnglishListeners.json' # results file
        path_sys_abbr = 'system_abbr_en_vcc20.json' #system abbreviation
    elif prev == 'jp':
        lang = 'Japanese'               #Test for Japanese listeners
    # class JPClass:
        exp_id = 'LOkmjYerjYlX'         #Experiment ID, no need to change this
        test_id = 'gjLXGAqKGvPK'        ##Test  ID, no need to change this
        exp_manifest_id_1 = 'rve6o1b6Odw2' #question id for the first question (quality evaluation)
        exp_manifest_id_2 = 'Ew6LBKN3q5J1' #question id for the second question (similarity evaluation)
        resfile = 'VCC2020-scores-JapaneseListeners.json'  # results file
        path_sys_abbr = 'system_abbr_ja_vcc20.json'   #system abbreviation
    return lang, exp_id, test_id , exp_manifest_id_1,exp_manifest_id_2, resfile, path_sys_abbr

# class EnClass:


source_spks = ['SEF1','SEF2','SEM1','SEM2']
target_spks = ['TFF1',   'TFM1',   'TGF1',   'TGM1',   'TMF1',   'TMM1']
L1_langs = ['English']
L2_langs = ['Finnish', 'German', 'Mandarin']

def get_system_abbr(path_sys_abbr):
    with open(path_sys_abbr, 'r') as f:
        data = json.load(f)
    systems = [x['abbreviation'] for x in data]
    return systems


def get_scores(systems, scores, exp_manifest):
    res = dict((x,[]) for x in systems)
    del res['ref']
    res['ref_intra'] = []
    res['ref_cross'] = []
    for score_unit in scores['result']['scores']:
        if score_unit['listener']['state'] == 'Valid' and score_unit['question']['experimental_manifest_id'] == exp_manifest:
            abbr =  score_unit['samples']['sample_a']['system']['abbreviation']
            if 'ref' not in abbr:
                if abbr not in systems:
                    print('error')
                else:
                    res[abbr].append(score_unit['score_value'])
            else:
                if 'TE' in score_unit['samples']['sample_a']['name']:
                    res['ref_intra'].append(score_unit['score_value'])
                else:
                    res['ref_cross'].append(score_unit['score_value'])
    return res



def get_source_spk_scores(system_name, spks, scores, exp_manifest):
    res = dict((x,[]) for x in spks)
    for score_unit in scores['result']['scores']:
        if score_unit['listener']['state'] == 'Valid' and score_unit['question']['experimental_manifest_id'] == exp_manifest:
            file_name =  score_unit['samples']['sample_a']['file_name']
            for spk in spks:
                if spk in file_name:
                    res[spk].append(score_unit['score_value'])
    return res

def get_mean(score):
    return dict((x, np.mean(score[x])) for x in score.keys())


def divide_intra_cross(score):

    intra = dict((x.split('_')[0], score[x]) for x in score.keys() if 'intra' in x  )
    cross = dict((x.split('_')[0], score[x])   for x in score.keys() if 'cross' in x)
    # ref = dict((x, score[x])   for x in score.keys() if 'ref' in x)
    intra['source'] = intra['team34']
    cross['source'] = cross['team34']
    intra['target'] = intra['ref']
    cross['target'] = cross['ref']
    del intra['team34']
    del cross['team34']
    del intra['ref']
    del cross['ref']
    return intra, cross

def rank_dict(x):
    data = {k: v for k, v in sorted(x.items(), key=lambda item: item[1], reverse =False)}
    return data
    # i = 0
    # for x in data.keys():
    #     print(i, x, data[x])
    #     i += 1
def rank_by_key(x):
    data = {k: v for k, v in sorted(x.items(), key=lambda item: item[0], reverse =False)}
    return data
def rank_qua(qua):
    same_score = rank_dict(get_mean(qua))
    return {x:qua[x]  for x in same_score.keys()}

def rank_sim(sim):
    # syss = sim.keys()
    # same_score = {}
    # for ss in syss:
    #     if len(sim[ss]) == 0:
    #         print(ss)
    #         exit ()
    #     same_score[ss] = (sim[ss].count(3) + sim[ss].count(4))/len(sim[ss])
    #
    # same_score = rank_dict(same_score)
    same_score = rank_dict(get_mean(sim))
    return {x:sim[x]  for x in same_score.keys()}

def get_same_sim_score(sim):
    syss = sim.keys()
    same_score = {}
    for ss in syss:
        same_score[ss] = (sim[ss].count(3) + sim[ss].count(4))/len(sim[ss])
    return same_score

def merge_two_dicts(x, y):
  z = x.copy()   # start with x's keys and values
  z.update(y)    # modifies z with y's keys and values & returns None
  return z

def divide_l1_l2(cross_systems, scores, exp_manifest):
    TE_systems = [x  for x in cross_systems]
    TF_systems = [x  for x in cross_systems]
    res_a = dict((x,[]) for x in TE_systems)
    res_b = dict((x,[]) for x in TF_systems)

    for score_unit in scores['result']['scores']:
        if score_unit['listener']['state'] == 'Valid' and score_unit['question']['experimental_manifest_id'] == exp_manifest:
            abbr =  score_unit['samples']['sample_a']['system']['abbreviation']
            if 'ref' not in abbr and 'team34' not in abbr :
                if 'cross' in abbr:
                    if '_E3' in score_unit['samples']['sample_b']['name']:
                        res_a[abbr.split('_')[0] ].append(score_unit['score_value'])
                    else:
                        res_b[abbr.split('_')[0] ].append(score_unit['score_value'])
            elif 'team34' in abbr:
                if 'cross' in abbr:
                    if '_E3' in score_unit['samples']['sample_b']['name']:
                        res_a['source'].append(score_unit['score_value'])
                    else:
                        res_b['source'].append(score_unit['score_value'])
            else:
                if '_E3' in score_unit['samples']['sample_a']['name']:
                    res_a['target'].append(score_unit['score_value'])
                else:
                    res_b['target'].append(score_unit['score_value'])
    return res_a, res_b

def divide_langs(cross_systems, scores, exp_manifest, sample_id='sample_b'):
    TE_systems = [x  for x in cross_systems]
    TF_systems = [x  for x in cross_systems]
    TG_systems = [x  for x in cross_systems]
    TM_systems = [x  for x in cross_systems]
    res_e = dict((x,[]) for x in TE_systems)
    res_f = dict((x,[]) for x in TF_systems)
    res_g = dict((x,[]) for x in TG_systems)
    res_m = dict((x,[]) for x in TM_systems)
    def assign_score(team):
        if '_E3' in score_unit['samples']['sample_b']['name']:
            res_e[team ].append(score_unit['score_value'])
        elif '_F4' in score_unit['samples']['sample_b']['name']:
            res_f[team ].append(score_unit['score_value'])
        elif '_G4' in score_unit['samples']['sample_b']['name']:
            res_g[team].append(score_unit['score_value'])
        elif '_M4' in score_unit['samples']['sample_b']['name']:
            res_m[team ].append(score_unit['score_value'])
        else:
            print('wrong system')
    for score_unit in scores['result']['scores']:
        if score_unit['listener']['state'] == 'Valid' and score_unit['question']['experimental_manifest_id'] == exp_manifest:
            abbr =  score_unit['samples']['sample_a']['system']['abbreviation']
            if 'ref' not in abbr and 'team34' not in abbr :
                if 'cross' in abbr:
                    team = abbr.split('_')[0]
                    assign_score(team)
            elif 'team34' in abbr:
                if 'cross' in abbr:
                    team = 'source'
                    assign_score(team)
            else:
                team = 'target'
                assign_score(team)

    res = {'en': res_e, 'fr': res_f, 'ge': res_g, 'ch':res_m}

    return res


def divide_l2(cross_systems, scores, exp_manifest):
    systems = [x  for x in cross_systems]
    res = dict((x, dict((y,[]) for y in systems)) for x in (L1_langs + L2_langs))

    # res_e = dict((x,[]) for x in systems)
    # res_g = dict((x,[]) for x in systems)
    # res_f = dict((x,[]) for x in systems)
    # res_m = dict((x,[]) for x in systems)

    def assign_score(team):
        if 'TE' in score_unit['samples']['sample_a']['name']:
            res['English'][team ].append(score_unit['score_value'])
        elif 'TF' in score_unit['samples']['sample_a']['name']:
            res['Finnish'][team ].append(score_unit['score_value'])
        elif 'TG' in score_unit['samples']['sample_a']['name']:
            res['German'][team ].append(score_unit['score_value'])
        elif 'TM' in score_unit['samples']['sample_a']['name']:
            res['Mandarin'][team ].append(score_unit['score_value'])
        else:
            print('wrong system')
    for score_unit in scores['result']['scores']:
        if score_unit['listener']['state'] == 'Valid' and score_unit['question']['experimental_manifest_id'] == exp_manifest:
            abbr =  score_unit['samples']['sample_a']['system']['abbreviation']
            if 'ref' not in abbr and 'team34' not in abbr :
                if 'cross' in abbr:
                    team = abbr.split('_')[0]
                    assign_score(team)
            elif 'team34' in abbr:
                if 'cross' in abbr:
                    team = 'source'
                    assign_score(team)
            else:
                team = 'target'
                assign_score(team)

    return res






def main():
    prev = 'en' ###for English listeners
    #prev = 'jp' ###for Japanese listeners

    lang, exp_id, test_id , exp_manifest_id_1,exp_manifest_id_2, resfile, path_sys_abbr = prev_setting(prev)

    with open(resfile) as json_file:
        scores = json.load(json_file) ##read all scores from results file

    systems = get_system_abbr(path_sys_abbr)
    score_qua = get_scores(systems, scores, exp_manifest_id_1) #quality score
    score_sim = get_scores(systems, scores, exp_manifest_id_2) #similarity score

    intra_score_qua, cross_score_qua = divide_intra_cross(score_qua) #quality score, different tasks
    intra_score_sim, cross_score_sim = divide_intra_cross(score_sim) #similarity  score, different tasks
