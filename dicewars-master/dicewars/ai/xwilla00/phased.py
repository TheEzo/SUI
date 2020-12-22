import logging

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand
from .nn import NN
from .utils import *


class FinalAI:

    def __init__(self, player_name, board, players_order):
        """
        Parameters
        ----------
        game : Game
        """
        self.player_name = player_name
        self.players_order = players_order
        self.logger = logging.getLogger('AI')
        self.turn_id = 0
        self.reserve = 0
        self.nn = NN()
        self.t = 0

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn
        """

        # tady nekde volani A* nebo cehosi podobnyho
        self.turn_id = self.turn_id + 1
        self.logger.debug("Turn " + str(self.turn_id) + " begin....")

        all_evaluated_moves = []
        all_moves = list(possible_attacks(board, self.player_name))
        if len(all_moves) == 0:
            return self.end_turn_command_and_reserv_calculation(board)

        for move in all_moves:
            # ziskani vektoru pro NN
            nn_input_vec = self.get_nn_vector(board, move)

            # vyhodnoceni hodnoty
            attack_value = self.nn.eval(nn_input_vec)

            all_evaluated_moves.append((move[0], move[1], attack_value))

        # self.logger.debug(all_evaluated_moves[0][2])
        maximum = max(m[2] for m in all_evaluated_moves)
        best_move = next(m for m in all_evaluated_moves if m[2] == maximum)
        all_evaluated_moves.sort(key=lambda tup: tup[2])

        self.logger.debug(f'evaluated: {best_move[2]}')
        if best_move[2] > 0.2 and self.t < 3:
            # attack
            self.logger.debug("Attacking")
            self.t += 1
            return BattleCommand(best_move[0].get_name(), best_move[1].get_name())
        elif best_move[2] > 0.4:  # xperimentalni hranice .. uvidi se podle NN
            # attack
            self.logger.debug("Attacking")
            self.t += 1
            return BattleCommand(best_move[0].get_name(), best_move[1].get_name())
        else:
            # end of turn
            self.logger.debug("Nothing to do")
            return self.end_turn_command_and_reserv_calculation(board)

    def end_turn_command_and_reserv_calculation(self, board):
        score = get_score_by_player(self.player_name, board)
        capacity = get_dice_space(self.player_name, board)
        capacity_after_score_added = capacity - score
        # self.logger.debug("Score " + str(score))
        # self.logger.debug("Zustatek kostek " + str(capacity_after_score_added))
        if capacity_after_score_added > 0:
            self.reserve = self.reserve - capacity_after_score_added

        if capacity_after_score_added < 0:
            self.reserve = self.reserve - capacity_after_score_added

        if self.reserve < 0:
            self.reserve = 0

        if self.reserve > 64:  # e rezerva 62?
            self.reserve = 62

        return EndTurnCommand()

    # Vstupy NN
    # % velikost rezervy                                
    # pravdepodobnost dobyti                            mame
    # utok z nejvetsiho bool                            mame
    # utok na nejvetsi bool                             mame
    # % poli protivnika
    # pocet kostek protivnika/pocet kostek v cele hre   mame
    # zaplneni oblasti obrany                           mame
    # zaplneni oblasti protivnika                       mame

    def get_nn_vector(self, board, move) -> list:
        defender_name = move[1].get_owner_name()

        #pravdepodobnost dobyti
        successful_atack_p = probability_of_successful_attack(board, move[0].get_name(), move[1].get_name())
        # self.logger.debug("Attack prob: " + str(successful_atack_p))

        #utok/obrana z nejvetsiho
        attacker_max_regio_flag = is_in_largest_region(move[0], board)
        # self.logger.debug("Attacker max regio flag: " + str(attacker_max_regio_flag))

        defender_max_regio_flag = is_in_largest_region(move[1], board)
        # self.logger.debug("Defender max regio flag: " + str(defender_max_regio_flag))

        # hustota zaplneni kostkama napadeneho pole
        attacker_region_occupancy = get_regio_occupancy(move[0], board)
        # self.logger.debug("Attacker regio occupancy: " + str(attacker_region_occupancy))

        defender_region_occupancy = get_regio_occupancy(move[1], board)
        # self.logger.debug("Defender regio occupancy: " + str(defender_region_occupancy))
        #
        # pocet kostek playera ku kostkam na boardu
        attacker_dice_proportion = get_dice_proportion(self.player_name, board)
        # self.logger.debug("Attacker dice proportion: " + str(attacker_dice_proportion))

        defender_dice_proportion = get_dice_proportion(defender_name, board)
        # self.logger.debug("Defender dice proportion: " + str(defender_dice_proportion))

        # pocet poli playera ku poctu poli na boardu
        attacker_area_proportion = get_area_proportion(self.player_name, board)
        # self.logger.debug("Attacker area proportion: " + str(attacker_area_proportion))

        defender_area_proportion = get_area_proportion(defender_name, board)
        # self.logger.debug("Defender area proportion: " + str(defender_area_proportion))

        # rezerva
        reserve = self.reserve
        # self.logger.debug("Reserve: " + str(reserve))

        # skore v procentech po provedeni utoku
        enemy_score = score_after_move(defender_name, board, move[1].get_name())
        # self.logger.debug("Enemy score after attack: " + str(enemy_score))

        count_of_enemy_neighbours = count_of_adjacen(move[0].get_name(), board, self.player_name)
        # self.logger.debug("sousedi : " + str(count_of_enemy_neighbours))

        # vrat si co budes potrebovat
        return [successful_atack_p, attacker_max_regio_flag, defender_max_regio_flag, attacker_region_occupancy,
                defender_region_occupancy, attacker_dice_proportion, defender_dice_proportion, attacker_area_proportion,
                defender_area_proportion, reserve, enemy_score, count_of_enemy_neighbours]
