import json
import os


def hash_list(value):
    res = ''
    for item in value:
        res += f'{item};'
    return res[:-1]


def run():
    added = set()
    with open(os.path.join(os.path.dirname(__file__), 'train'), 'w') as r:
        with open(os.path.join(os.path.dirname(__file__), 'collected'), 'r') as f:
            data = f.read()
        r.write('[\n')
        for d in data.split('\n'):
            if d == 'end_turn' or not d:
                continue
            record = json.loads(d)
            for item in record:
                hash_ = hash_list(item['data'][:-1])
                if hash_ not in added:
                    added.add(hash_)

                    evaluated = eval(item['data'])
                    w = dict(data=item['data'][:11], res=evaluated)
                    r.write(json.dumps(w))
                    r.write(',\n')
        r.write(']\n')


def eval(vector):
    res = 0.
    res += vector[0] * 0.34  # successful_atack_p

    res += vector[1] * 0.015  # attacker_max_regio_flag
    res += vector[2] * 0.015  # defender_max_regio_flag

    if vector[3] > vector[4]:
        res += vector[3] * 0.24  # attacker_region_occupancy
        res += vector[4] * 0.04  # defender_region_occupancy
    else:
        res += vector[3] * 0.09  # attacker_region_occupancy
        res += vector[4] * 0.19  # defender_region_occupancy

    res += vector[5] * 0.015  # attacker_dice_proportion
    res += vector[6] * 0.015  # defender_dice_proportion

    if vector[7] > vector[8]:
        res += vector[7] * 0.09  # attacker_dice_proportion
        res += vector[8] * 0.09  # defender_dice_proportion
    else:
        res += vector[7] * 0.075  # attacker_dice_proportion
        res += vector[8] * 0.105  # defender_dice_proportion

    res += vector[9] * 0.04  # reserve
    res += vector[10] * 0.1  # enemy_score

    # res += vector[0] * 0.35  # successful_atack_p  350
    #
    # res += vector[1] * 0.1  # attacker_max_regio_flag  100
    # res += vector[2] * 0.05  # defender_max_regio_flag  50
    #
    # res += vector[3] * 0.15  # attacker_region_occupancy  150
    # res += vector[4] * 0.15  # defender_region_occupancy  150
    #
    # res += vector[5] * 0.05  # attacker_dice_proportion  50
    # res += vector[6] * 0.05  # defender_dice_proportion  50
    #
    # res += vector[7] * 0.05  # attacker_dice_proportion  50
    # res += vector[8] * 0.05  # defender_dice_proportion  50
    #
    # res += vector[9] * 0.2  # reserve  200
    # res += vector[10] * 0.1  # enemy_score  100
    # res /= 1.3

    return res


if __name__ == '__main__':
    run()
