import json
import os
import numpy as np

def hash_list(value):
    res = ''
    for item in value:
        res += f'{item};'
    return res[:-1]


def run():
    added = set()
    train_data = []

    with open(os.path.join(os.path.dirname(__file__), 'collected'), 'r') as f:
        data = f.read()

    for d in data.split('\n'):
        if d == 'end_turn' or not d:
            continue

        record = json.loads(d)
        for item in record:
            vector = item['data']

            del vector[7]

            hash_ = hash_list(vector)
            if hash_ not in added:
                added.add(hash_)
                train_data.append(vector)

    train_data = np.array(train_data)
    nb_count_norm = normalize(train_data[:, -1])

    train_data[:,-1] = nb_count_norm

    evaluated_data = []

    for vector in train_data:
        evaluated = eval(vector)
        if item['choosen'] and evaluated < 0.5 and vector[0] > 0.49:
            evaluated += 0.1
        w = dict(data=vector.tolist(), res=evaluated)
        evaluated_data.append(w)

    results = [d['res'] for d in evaluated_data]
    results = normalize(results)

    updated = False
    with open(os.path.join(os.path.dirname(__file__), 'train'), 'w') as r:
        r.write('[\n\t')
        for i, item in enumerate(evaluated_data):
            if updated:
                r.write(',\n\t')
            w = dict(data=item['data'], res=results[i])
            r.write(json.dumps(w))
            updated = True
        r.write('\n]\n')

def normalize(data):
    data = np.array(data)

    low = data.min()
    high = data.max() - low
    return [(r - low) / high for r in data]


def eval(vector):
    if vector[0] > 0.67 and vector[0] < 0.84: # utok na oblasti, ktere maji o jednu kostku min
        res = vector[0] * 4.5
    elif vector[0] > 0.844 and vector[0] < 0.94: # utok na oblasti, ktere maji o dve kostky min
        res = vector[0] * 3
    elif vector[0] > 0.6: # zbytek oblasti s mensim poctem kostek
        res = vector[0] * 2
    elif vector[0] > 0.44 and vector[0] < 0.47: # utok na oblasti se stejnym poctem kostek - riskujeme pouze tehdy, pokud mame dobre rozehranou hru
        attack_prob = vector[0]

        if vector[1] > vector[2]: # utocime z nejvetsiho regionu - obrana
            attack_prob += 0.2

        if vector[3] > vector[4]: # region ma vetsi hustotu - obrana
            attack_prob += 0.3

        if vector[5] > vector[6]: # mame v prumeru vic kostek
            attack_prob += 0.3

        if vector[7] > vector[8]: # mame vic oblasti
            attack_prob += 0.2
       
        return attack_prob
    else:
        res = vector[0] * 1.5

    if vector[1] != vector[2] : # attacker_max_regio_flag, defender_max_regio_flag
        res += 0.5

    if vector[3] > vector[4]: # attacker_region_occupancy, defender_region_occupancy
        res += 0.8 # 0.8
    elif vector[3] < vector[4]:
        res -= 0.35 # 0.25

    if vector[5] > vector[6]: # attacker_dice_proportion, defender_dice_proportion
        res += 0.4 #0.5
    elif vector[5] < vector[6]:
        res -= 0.25 # 0.15

    if vector[7] > vector[8]: # attacker_area_proportion, defender_area_proportion
        res += 0.6 #0.6
    elif vector[7] < vector[8]:
        res -= 0.2 # 0.25

    # res += vector[9]  * 0.5   # reserve
    res += vector[9] * 0.3   # enemy_score 0.3
    res -= vector[10] * 0.2  # neighbours_count 0.3

    if res < 0:
        return vector[0]

    return res

if __name__ == '__main__':
    run()
    from dicewars.ai.xwilla00.nn import train
    train()
