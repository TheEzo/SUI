def eval(vector):
    res = 0.
    res += vector[0] * 0.35  # successful_atack_p

    res += vector[1] * 0.025  # attacker_max_regio_flag
    res += vector[2] * 0.025  # defender_max_regio_flag

    if (vector[3] > vector[4]):
        res += vector[3] * 0.25  # attacker_region_occupancy
        res += vector[4] * 0.05  # defender_region_occupancy
    else:
        res += vector[3] * 0.1  # attacker_region_occupancy
        res += vector[4] * 0.2  # defender_region_occupancy

    res += vector[5] * 0.025  # attacker_dice_proportion
    res += vector[6] * 0.025  # defender_dice_proportion

    if (vector[7] > vector[8]):
        res += vector[7] * 0.1  # attacker_dice_proportion
        res += vector[8] * 0.1  # defender_dice_proportion
    else:
        res += vector[7] * 0.085  # attacker_dice_proportion
        res += vector[8] * 0.115  # defender_dice_proportion

    res += vector[9] * 0.05  # reserve

    return res
