import logging
import random

#from .utils import *

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


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


    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn
        """
        #tady nekde volani A* nebo cehosi podobnyho


        #nekonecnej cyklus s NN
        while True:
            all_moves = list(possible_attacks(board, self.player_name))
            for move in all_moves:
                #fejkovani NN tady casem bude nejakej eval prostrednictvim NN
                self.logger.debug("There are no moves of interest")


        self.logger.debug("There are no moves of interest")
        return EndTurnCommand()



