import logging

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand
from .nn import NN
from .utils import *
import time

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
        self.adjacent_areas_max = max_count_of_adjacen(board)
        self.attacked = None

        self.won = 0

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn
        """
        start_turn = time.time()
       
        #if self.attacked is not None:
            #new_owner = board.areas[str(self.attacked)].get_owner_name()

            # if new_owner == self.player_name:
            #    self.logger.debug("Attack successful")
            #    self.won += 0.04
            #else:
            #    self.logger.debug("Attack not successful")
            #    self.won -= 0.06
            #
            #    if self.won < 0:
            #        self.won = 0
                    
            #self.attacked = None

        try:
            # tady nekde volani A* nebo cehosi podobnyho
            self.turn_id = self.turn_id + 1
            self.logger.debug("Turn " + str(self.turn_id) + " begin....")

            all_evaluated_moves = []
            all_moves = list(possible_attacks(board, self.player_name))
            
            if len(all_moves) == 0:
                return self.end_turn_command_and_reserv_calculation(board)

            if time_left < 0.3 or time_left / 0.05 < len(all_moves):
                return self.end_turn_command_and_reserv_calculation(board)

            moves_time_start = time.time()

            all_moves.sort(key=lambda tup: (tup[0].get_dice() * tup[0].get_dice()) - tup[1].get_dice(), reverse=True)
            
            if self.t > 5:
                return self.end_turn_command_and_reserv_calculation(board)
                for move in all_moves:
                    nn_input_vec = self.get_nn_vector(board, move)
                    attack_value = self.nn.eval(nn_input_vec)[0][0]

                    self.logger.debug(f"nn_input_vec: {nn_input_vec}")
                    self.logger.debug(f"attack_value: {attack_value}")

                    if attack_value > 0.65: # 0.65
                        self.logger.debug(f"Attacking: {self.t}, {attack_value}")
                        self.attacked = move[1].get_name()
                        return BattleCommand(move[0].get_name(), move[1].get_name())

                return self.end_turn_command_and_reserv_calculation(board)   
            else:
                for move in all_moves:
                    nn_input_vec = self.get_nn_vector(board, move)
                    attack_value = self.nn.eval(nn_input_vec)[0][0]

                    self.logger.debug(f"nn_input_vec: {nn_input_vec}")
                    self.logger.debug(f"attack_value: {attack_value}")

                    if attack_value > 0.75:
                        self.logger.debug(f"Attacking: {self.t}, {attack_value}")
                        self.attacked = move[1].get_name()
                        return BattleCommand(move[0].get_name(), move[1].get_name())

                    all_evaluated_moves.append((move[0], move[1], attack_value))
            
            moves_time_end = time.time()
            self.logger.debug(f"moves_time: {moves_time_end - moves_time_start}")

            maximum = max(m[2] for m in all_evaluated_moves)
            best_move = next(m for m in all_evaluated_moves if m[2] == maximum)
            all_evaluated_moves.sort(key=lambda tup: tup[2])

            self.logger.debug(f'evaluated: {best_move[2]}')
            
            if (self.t > 1 and best_move[2] > (0.56 - self.won)) or (best_move[2] > (0.53 - self.won)):
                self.logger.debug(f"Attacking: {self.t}, {best_move[2]}")
                self.attacked = best_move[1].get_name()
                self.t += 1
                return BattleCommand(best_move[0].get_name(), best_move[1].get_name())
            
            self.logger.debug("Nothing to do")
            return self.end_turn_command_and_reserv_calculation(board)
            
        finally:
            end_turn = time.time()
            self.logger.debug(f"end turn: {end_turn - start_turn}")

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

        self.t = 0

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
        # return [successful_atack_p, attacker_max_regio_flag, defender_max_regio_flag, attacker_region_occupancy,
        #        defender_region_occupancy, attacker_dice_proportion, defender_dice_proportion, attacker_area_proportion,
        #        defender_area_proportion, reserve, enemy_score, count_of_enemy_neighbours / self.adjacent_areas_max]

        return [successful_atack_p, attacker_max_regio_flag, defender_max_regio_flag, attacker_region_occupancy,
                defender_region_occupancy, attacker_dice_proportion, defender_dice_proportion, attacker_area_proportion,
                defender_area_proportion, enemy_score, count_of_enemy_neighbours / self.adjacent_areas_max]
