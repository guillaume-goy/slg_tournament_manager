#tournament.py
import random
import math
import numpy as np
import logging
from collections import Counter

from player import Player
from match import Match
from config import ELO_START, REJECTION_NUMBER

class Tournament :
    def __init__(self, name):
        logging.info(f"Create a new tournament with name {name}")
        self.name = name
        self.players_global = []
        self.players_active = []
        self.players_active_M = []
        self.players_active_F = []
        self.players_inactive = [] #Players who take break / stop the tournament
        self.players_in_match = [] #Players who are involve in an ongoing match
        self.number_of_match = 0

        self.played_matches = []
        self.ongoing_matches = []
        self.winrates = {} # pourcentage de matches gagnés
        self.leaderboard = {} # moyenne nombres de points par match

    def __str__(self):
        return (f"General information about: {self.name}" + "\n" +
                f"Registered players: {[player.name for player in self.players_global]}" + "\n" +
                f"Break players: {[player.name for player in self.players_inactive]}" + "\n" +
                f"Playing players: {[player.name for player in self.players_in_match]}" + "\n" +
                f"Waiting players: {[player.name for player in self.players_active]}" + "\n" +
                f"Waiting players M: {[player.name for player in self.players_active_M]}" + "\n" +
                f"Waiting players F: {[player.name for player in self.players_active_F]}" + "\n" +
                f"Ongoing matches: {[str(match) for match in self.ongoing_matches]}" + "\n" +
                f"Matches Finifhed: {[str(match) for match in self.played_matches]}"
        )
    
    def refresh_winrates(self):
        for player in self.players_global:
            player.update_winrate()

    def refresh_leaderboard(self):
        for player in self.players_global:
            self.leaderboard[player.name] = player.elo

    def all_refreshes(self):
        self.refresh_leaderboard()
        self.refresh_winrates()
        self.update_elo_position()
        self.update_winrate_position()
        self.update_points_position()
        logging.info("refresh leaderboards")

    def add_player(self, player):
        self.players_global.append(player)
        self.players_active.append(player)
        if player.gender == "M" : 
            self.players_active_M.append(player)
        else:
            self.players_active_F.append(player)
        logging.info(f"add player to tournament : {player.name} ({player.gender})")
        #self.all_refreshes()

    def remove_player(self, player):
        self.players_global.remove(player)
        if player in self.players_active :
            self.players_active.remove(player)
            if player.gender == "M" : 
                self.players_active_M.remove(player)
            else:
                self.players_active_F.remove(player)
        if player in self.players_inactive :
            self.players_inactive.remove(player)
        logging.info(f"remove player from tournament : {player.name} ({player.gender})")
        self.all_refreshes()

    def break_player(self, player):
        if player in self.players_in_match :
            logging.warning("break player tries to break a player involved in a match")
            return 1
        elif player in self.players_inactive :
            logging.warning("try to break a player already in break")
            return 2
        elif player.gender == "M" : 
            self.players_active_M.remove(player)
        else:
            self.players_active_F.remove(player)
        self.players_active.remove(player)
        self.players_inactive.append(player)
        player.status = "En pause"
        logging.info(f"player {player.name} takes a break")
        return 0

    def unbreak_player(self, player):
        if player in self.players_in_match :
            logging.warning("unbreak player tries to unbreak a player involved in a match")
            return 1
        elif player in self.players_active :
            logging.warning("try to unbreak a player already in active list")
            return 2
        if player in self.players_inactive :
            self.players_inactive.remove(player)
            self.players_active.append(player)
            if player.gender == "M" : 
                self.players_active_M.append(player)
            else:
                self.players_active_F.append(player)
            player.status = "En attente"
            logging.info(f"player {player.name} comes back from break")
            return 0
        else :
            logging.error("unbreak_player tries to unbreak a player not in the break list")
            return 3

    def match_player(self, player):
        if player.gender == "M" : 
            self.players_active_M.remove(player)
        else:
            self.players_active_F.remove(player)
        self.players_active.remove(player)
        self.players_in_match.append(player)
        player.status = "En match"
        logging.info(f"{player.name} starts a match")

    def unmatch_player(self, player):
        if player in self.players_in_match :
            self.players_in_match.remove(player)
            self.players_active.append(player)
            if player.gender == "M" : 
                self.players_active_M.append(player)
            else:
                self.players_active_F.append(player)
            player.status = "En attente"
            logging.info(f"{player.name} ends a match")
        else :
            logging.error(f"unmatch_player tries to unmatch {player.name} who is not in an ongoing match")

    def random_sampling(self, list_of_players, k=1):
        if len(list_of_players) < k:
            return None
        weights = []
        #compute probabilities*
        for player in list_of_players:
            weights.append(1/math.pow(2,player.matches_played))
        total = sum(weights)
        normalised_weights = [w / total for w in weights]
        list_of_selected_players = np.random.choice(list_of_players, size=k, replace=False, p=normalised_weights)
        return list(list_of_selected_players) 

    def create_random_match(self, cat="random"):
        list_of_players = []
        rejection_cpt = REJECTION_NUMBER
        cond = True
        if cat == "mixte":
            while (rejection_cpt>0 and cond):
                rejection_cpt -= 1
                try :
                    [player1_M, player2_M] = self.random_sampling(self.players_active_M, 2)
                    choice_list_for_player1_M = [player for player in self.players_active_F if player not in player1_M.partners_history]
                    [player1_F] = self.random_sampling(choice_list_for_player1_M)
                    choice_list_for_player1_M = [player for player in self.players_active_F if player not in player1_M.partners_history and player != player1_F]
                    [player2_F] = self.random_sampling(choice_list_for_player1_M)
                except :
                    logging.warning(f"create_random_match : Unable to find a combination to start a {cat} game --> We try again (remaining attempts: {rejection_cpt})")
                    [player1_F, player1_M, player2_F, player2_M] = [None, None, None, None]
                if all(x is not None for x in [player1_F, player1_M, player2_F, player2_M]):
                    cond = False
                    list_of_players = [player1_F, player1_M, player2_F, player2_M]

        elif cat == "double_H":
            while (rejection_cpt>0 and cond):
                rejection_cpt -= 1
                try :
                    [player1, player2, player3, player4] = self.random_sampling(self.players_active_M, 4)
                except :
                    logging.warning(f"create_random_match : Unable to find a combination to start a {cat} game --> We try again (remaining attempts: {rejection_cpt})")
                    [player1, player2, player3, player4] = [None, None, None, None]
                if all(x is not None for x in [player1, player2, player3, player4]):
                    cond = False
                    list_of_players = [player1, player2, player3, player4]

        elif cat == "double_F":
            while (rejection_cpt>0 and cond):
                rejection_cpt -= 1
                try :
                    [player1, player2, player3, player4] = self.random_sampling(self.players_active_F, 4)
                except :
                    logging.warning(f"create_random_match : Unable to find a combination to start a {cat} game --> We try again (remaining attempts: {rejection_cpt})")
                    [player1, player2, player3, player4] = [None, None, None, None]
                if all(x is not None for x in [player1, player2, player3, player4]):
                    cond = False
                    list_of_players = [player1, player2, player3, player4]

        elif cat == "random":
            while (rejection_cpt>0 and cond):
                rejection_cpt -= 1
                try :
                    [player1, player2, player3, player4] = self.random_sampling(self.players_active, 4)
                except :
                    logging.warning(f"create_random_match : Unable to find a combination to start a {cat} game --> We try again (remaining attempts: {rejection_cpt})")
                    [player1, player2, player3, player4] = [None, None, None, None]
                if all(x is not None for x in [player1, player2, player3, player4]):
                    cond = False
                    list_of_players = [player1, player2, player3, player4]
        if list_of_players != []:
            new_match = Match(list_of_players)
            self.number_of_match += 1
            new_match.number = self.number_of_match
            logging.info(f"create_random_match : Successfully created a {cat} game: {new_match}")

            #Considérer les joueurs comme en match
            self.match_player(list_of_players[0])
            self.match_player(list_of_players[1])
            self.match_player(list_of_players[2])
            self.match_player(list_of_players[3])

            #Mettre à jour les historiques
            list_of_players[0].update_history(list_of_players[1])
            list_of_players[2].update_history(list_of_players[3])

            self.ongoing_matches.append(new_match)
            return 1
        else :
            logging.info(f"create_random_match : failed to create a {cat} game.")
            return 0
     
    def create_premade_match(self, players_list):
        for player in players_list :
            if player in self.players_inactive:
                self.unbreak_player(player)
            if player not in self.players_active:
                logging.error(f"create_premade_match tries to create a premade match with unavailable players.")
                return 1
            
        new_match = Match(players_list)
        self.number_of_match += 1
        new_match.number = self.number_of_match
        logging.info(f"create_premade_match : Successfully created a premade game: {new_match}")
        
        #Considérer les joueurs comme en match
        self.match_player(players_list[0])
        self.match_player(players_list[1])
        self.match_player(players_list[2])
        self.match_player(players_list[3])

        #Mettre à jour les historiques
        players_list[0].update_history(players_list[1])
        players_list[2].update_history(players_list[3])
        self.ongoing_matches.append(new_match)
        return 0
    
    def cancel_match(self, match):
        #Annule un match
        if match.status == "Terminé":
            logging.error("trying to cancel a finished match")
            return 1
        elif match.status == "Match annulé":
            logging.error("trying to cancel a canceled match")
            return 2
        else:
            self.unmatch_player(match.player1)
            self.unmatch_player(match.player2)
            self.unmatch_player(match.player3)
            self.unmatch_player(match.player4)

        #remove from history
        match.player1.remove_from_history(match.player2)
        match.player3.remove_from_history(match.player4)

        #refresh leaderboards
        match.status = "Match annulé"
        logging.info(f"Cancelled a match :\n{match}")
        self.all_refreshes()

    def finish_match(self, match, score):
        logging.info(f"Ending a match: {match}")
        match.set_score(score)

        # Rendre à nouveau les joueurs disponibles
        self.unmatch_player(match.player1)
        self.unmatch_player(match.player2)
        self.unmatch_player(match.player3)
        self.unmatch_player(match.player4)

        #Passer le match dans la liste des matches terminés
        self.ongoing_matches.remove(match)
        self.played_matches.append(match)

        #refresh leaderboards
        self.all_refreshes()

    def update_elo_position(self):
        sorted_players = sorted(self.players_global, key=lambda j: j.elo, reverse=True)
        
        # Mise à jour des rangs
        for i, player in enumerate(sorted_players, start=1):
            player.elo_position = i
        logging.info("updated players elo position")
    
    def update_winrate_position(self):
        sorted_players = sorted(self.players_global, key=lambda j: j.winrate, reverse=True)
        
        # Mise à jour des rangs
        for i, player in enumerate(sorted_players, start=1):
            player.winrate_position = i
        logging.info("updated players elo position")

    def update_points_position(self):
        sorted_players = sorted(self.players_global, key=lambda j: j.points_won, reverse=True)
        
        # Mise à jour des rangs
        for i, player in enumerate(sorted_players, start=1):
            player.points_position = i
        logging.info("updated players points position")

    def verif(self):
        #verif elo
        total_elo = 0
        for player in self.players_global:
            total_elo += player.elo
        assert (ELO_START - total_elo / len(self.players_global)) < 1, "The ELO system is not accurate."

        #verif player lists :
        assert (Counter(self.players_inactive + self.players_active + self.players_in_match) == Counter(self.players_global)), "Player lists are not matching."
