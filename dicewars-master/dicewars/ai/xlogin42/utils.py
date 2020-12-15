import logging
import numpy
import pickle
import random
import os
import numpy as np
import dicewars.client.game.board
import dicewars.client.game.area
from dicewars.client.game.board import Board
from typing import Iterator, Tuple
import collections

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand



def attacker_advantage(attacker, defender):
    return attacker.get_dice() - defender.get_dice()



def get_largest_region( player_name, board):
    largest_region = []

    players_regions = board.get_players_regions(player_name)
    max_region_size = max(len(region) for region in players_regions)
    max_sized_regions = [region for region in players_regions if len(region) == max_region_size]

    max_sized_regions[0]

    for region in max_sized_regions:
        for area in region:
            largest_region.append(area)

    return largest_region


def is_in_largest_region( area, board):
    owner  = area.get_owner_name()
    largest_region = get_largest_region(owner, board)
    if area.get_name() in largest_region:
        return 1
    else:
        return 0

def get_regio_occupancy(area, board):
    region = board.get_areas_region(area.get_name(),board.areas)
    regio_size = len(region)
    max_dice_count = 8 * regio_size
    dice_count = 0
    for ar in region:
        dice_count = dice_count + board.get_area(ar).get_dice()
    return dice_count/max_dice_count


def get_dice_proportion(player_name, board):
    dices_on_board = 0
    player_dices = board.get_player_dice(player_name)
    player_names = set(area.get_owner_name() for area in board.areas.values())
    for pl in player_names:
        dices_on_board = dices_on_board + board.get_player_dice(pl)
    return player_dices/dices_on_board

def get_area_proportion(player_name, board):
    areas_on_board = 0
    player_areas = len(board.get_player_areas(player_name))
    player_names = set(area.get_owner_name() for area in board.areas.values())
    for pl in player_names:
        areas_on_board = areas_on_board + len(board.get_player_areas(pl))
    return player_areas/areas_on_board



def probability_of_successful_attack(board, atk_area, target_area):
    atk = board.get_area(atk_area)
    target = board.get_area(target_area)
    atk_power = atk.get_dice()
    def_power = target.get_dice()
    return attack_succcess_probability(atk_power, def_power)


def attack_succcess_probability(atk, df):
    return {
        2: {
            1: 0.83796296,
            2: 0.44367284,
            3: 0.15200617,
            4: 0.03587963,
            5: 0.00610497,
            6: 0.00076625,
            7: 0.00007095,
            8: 0.00000473,
        },
        3: {
            1: 0.97299383,
            2: 0.77854938,
            3: 0.45357510,
            4: 0.19170096,
            5: 0.06071269,
            6: 0.01487860,
            7: 0.00288998,
            8: 0.00045192,
        },
        4: {
            1: 0.99729938,
            2: 0.93923611,
            3: 0.74283050,
            4: 0.45952825,
            5: 0.22044235,
            6: 0.08342284,
            7: 0.02544975,
            8: 0.00637948,
        },
        5: {
            1: 0.99984997,
            2: 0.98794010,
            3: 0.90934714,
            4: 0.71807842,
            5: 0.46365360,
            6: 0.24244910,
            7: 0.10362599,
            8: 0.03674187,
        },
        6: {
            1: 0.99999643,
            2: 0.99821685,
            3: 0.97529981,
            4: 0.88395347,
            5: 0.69961639,
            6: 0.46673060,
            7: 0.25998382,
            8: 0.12150697,
        },
        7: {
            1: 1.00000000,
            2: 0.99980134,
            3: 0.99466336,
            4: 0.96153588,
            5: 0.86237652,
            6: 0.68516499,
            7: 0.46913917,
            8: 0.27437553,
        },
        8: {
            1: 1.00000000,
            2: 0.99998345,
            3: 0.99906917,
            4: 0.98953404,
            5: 0.94773146,
            6: 0.84387382,
            7: 0.67345564,
            8: 0.47109073,
        },
    }[atk][df]

def possible_attacks(board: Board, player_name: int) -> Iterator[Tuple[int, int]]:
    for area in board.get_player_border(player_name):
        if not area.can_attack():
            continue
        neighbours = area.get_adjacent_areas()
        for adj in neighbours:
            adjacent_area = board.get_area(adj)
            if adjacent_area.get_owner_name() != player_name:
                yield (area, adjacent_area)


def get_score_by_player(player_name, board, skip_area=None):
    """Get score of a player
    Parameters
    ----------
    player_name : int
    skip_area : int
        Name of an area to be excluded from the calculation
    Returns
    -------
    int
        score of the player
    """
    players_regions = board.get_players_regions(player_name, skip_area=skip_area)
    max_region_size = max(len(region) for region in players_regions)

    return max_region_size


def get_dice_space(player_name, board):
    player_dices = board.get_player_dice(player_name)
    player_dice_capacity =  len(board.get_player_areas(player_name)) * 8
    return player_dice_capacity - player_dices