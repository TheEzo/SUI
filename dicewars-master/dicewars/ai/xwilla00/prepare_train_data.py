import json
import os


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
            # vector = [item['data'][0], item['data'][1], item['data'][2], item['data'][3],
            #           item['data'][4], item['data'][9], item['data'][10]]
            # bez flagu
            # vector = [item['data'][0], item['data'][3], item['data'][4], item['data'][9], item['data'][10]]
            vector = item['data']

            hash_ = hash_list(vector)
            if hash_ not in added:
                added.add(hash_)

                evaluated = eval(vector)
                if item['choosen'] and evaluated < 0.5 and vector[0] > 0.49:
                    evaluated += 0.1
                w = dict(data=vector, res=evaluated)
                train_data.append(w)

    results = [d['res'] for d in train_data]
    results = normalize(results)

    updated = False
    with open(os.path.join(os.path.dirname(__file__), 'train'), 'w') as r:
        r.write('[\n\t')
        for i, item in enumerate(train_data):
            if updated:
                r.write(',\n\t')
            w = dict(data=item['data'], res=results[i])
            r.write(json.dumps(w))
            updated = True
        r.write('\n]\n')


def normalize(data):
    low = min(data)
    high = max(data) - low
    return [(r - low) / high for r in data]


def eval(vector):
    res = 0.

    # bez flagu
    # for i, item in enumerate(vector):
    #     if i == 0:
    #         res += item * 1
    #     elif i == 1:
    #         res += item * 0.8
    #     elif i == 2:
    #         res += item * -0.75
    #     elif i == 3:
    #         res += item * 0.8
    #     elif i == 4:
    #         res += item * 0.7
    # return res
    #
    # for i, item in enumerate(vector):
    #     if i == 0:
    #         res += item * 1
    #     elif i == 1:
    #         res += item * 0.6
    #     elif i == 2:
    #         res += item * 0.8
    #     elif i == 3:
    #         res += item * -0.8
    #     elif i == 4:
    #         res += item * 0.75
    #     elif i == 5:
    #         res += item * 0.8
    #     elif i == 6:
    #         res += item * 0.7
    # return res

    for i, item in enumerate(vector):
        if i == 0:
            res += item * 1       # successful_atack_p
        elif i == 1:
            res += item * 0.6     # attacker_max_regio_flag
        elif i == 2:
            res += item * 0.8     # defender_max_regio_flag
        elif i == 3:
            res += item * 0.8    # attacker_region_occupancy
        elif i == 4:
            res += item * -0.8    # defender_region_occupancy
        elif i == 5:
            res += item * 0.6     # attacker_dice_proportion
        elif i == 6:
            res += item * -0.6     # defender_dice_proportion
        elif i == 7:
            res += item * 0.5       # attacker_area_proportion
        elif i == 8:
            res += item * -0.5       # defender_area_proportion
        elif i == 9:
            res += item * 0.9       # reserve
        elif i == 10:
            res += item * 0.7       # enemy_score
        elif i == 11:
            val = 1 if item else 0
            res += val * 0.6
    return res


if __name__ == '__main__':
    run()
