#match.py
import math
from config import ELO_K_COEF, ELO_SIGMOID_COEF
from score import Score

class Match:
    def __init__(self, list_of_players):
        # p1 and p2 VS p3 and p4
        self.player1 = list_of_players[0]
        self.player2 = list_of_players[1]
        self.player3 = list_of_players[2]
        self.player4 = list_of_players[3]
        self.player1_elo =self.player1.elo #Save elo when match starts
        self.player2_elo =self.player2.elo #Save elo when match starts
        self.player3_elo =self.player3.elo #Save elo when match starts
        self.player4_elo =self.player4.elo #Save elo when match starts
        RA = self.player1.elo + self.player2.elo
        RB = self.player3.elo + self.player4.elo
        P = math.pow(10, (RB-RA)/ELO_SIGMOID_COEF)

        self.expected_result = 1 / (1 + P) # Expected probability for p1 and p2.
        self.score = None
        self.result = None
        self.delta = 0
        self.status = "En cours"
        self.number = None
        self.type = self.determine_match_type()

    def __str__(self):
        return f"{self.number} :: {self.player1.name} et {self.player2.name} VS {self.player3.name} et {self.player4.name} ({self.score})"
    
    def determine_match_type(self):
        if self.player1.gender == self.player2.gender == self.player3.gender == self.player4.gender == "M":
            self.type = "dH"
        elif self.player1.gender == self.player2.gender == self.player3.gender == self.player4.gender == "F":
            self.type = "dF"
        elif (self.player1.gender == self.player3.gender) and (self.player2.gender == self.player4.gender) or (self.player1.gender == self.player4.gender) and (self.player2.gender == self.player3.gender) :
            self.type = "mixte"
        else:
            self.type = "rand"

    def set_score(self, score : Score):
        self.score = score
        total_team1 = score.set1_team1 + score.set2_team1 + (score.set3_team1 or 0)
        total_team2 = score.set1_team2 + score.set2_team2 + (score.set3_team2 or 0)
        
        nb_set_won_team1 = (score.set1_team1 > score.set1_team2) + (score.set2_team1 > score.set2_team2) + ((score.set3_team1 or 0) > (score.set3_team2 or 0))
        nb_set_won_team2 = (score.set1_team1 < score.set1_team2) + (score.set2_team1 < score.set2_team2) + ((score.set3_team1 or 0) < (score.set3_team2 or 0))
        nb_sets_played = nb_set_won_team1 + nb_set_won_team2

        self.result = nb_set_won_team1 / (nb_set_won_team1 + nb_set_won_team2)
        self.delta = abs(ELO_K_COEF*(self.result - self.expected_result))

        if nb_set_won_team1 > nb_set_won_team2 :
            self.player1.win_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player2.win_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player3.lose_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)
            self.player4.lose_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)
        else :
            self.player1.lose_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player2.lose_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player3.win_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)
            self.player4.win_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)

        self.player1.update_all()
        self.player2.update_all()
        self.player3.update_all()
        self.player4.update_all()
        self.status = "Terminé"

    def reset_score(self):
        score = self.score
        total_team1 = score.set1_team1 + score.set2_team1 + (score.set3_team1 or 0)
        total_team2 = score.set1_team2 + score.set2_team2 + (score.set3_team2 or 0)

        nb_set_won_team1 = (score.set1_team1 > score.set1_team2) + (score.set2_team1 > score.set2_team2) + ((score.set3_team1 or 0) > (score.set3_team2 or 0))
        nb_set_won_team2 = (score.set1_team1 < score.set1_team2) + (score.set2_team1 < score.set2_team2) + ((score.set3_team1 or 0) < (score.set3_team2 or 0))
        nb_sets_played = nb_set_won_team1 + nb_set_won_team2

        self.result = nb_set_won_team1 / (nb_set_won_team1 + nb_set_won_team2)
        self.delta = math.abs(ELO_K_COEF*(self.result - self.expected_result))

        if nb_set_won_team1 > nb_set_won_team2 :
            self.player1.unwin_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player2.unwin_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player3.unlose_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)
            self.player4.unlose_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)
        else :
            self.player1.unlose_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player2.unlose_match(sets_won = nb_set_won_team1, sets_played= nb_sets_played, points = total_team1, delta_elo=self.delta)
            self.player3.unwin_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)
            self.player4.unwin_match(sets_won = nb_set_won_team2, sets_played= nb_sets_played, points = total_team2, delta_elo=self.delta)

        self.player1.update_all()
        self.player2.update_all()
        self.player3.update_all()
        self.player4.update_all()
        self.status = "Match annulé"
