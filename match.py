#match.py
import math
from config import ELO_K_COEF, ELO_SIGMOID_COEF

class Score:
    def __init__(self):
        self.set1_team1 = 0
        self.set1_team2 = 0
        self.set2_team1 = 0
        self.set2_team2 = 0
        self.set3_team1 = None
        self.set3_team2 = None

    def __str__(self):
        if self.set3_team1 is None :
            return f"({self.set1_team1}-{self.set1_team2})({self.set2_team1}-{self.set2_team2})"
        else :
            return f"({self.set1_team1}-{self.set1_team2})({self.set2_team1}-{self.set2_team2})({self.set3_team1}-{self.set3_team2})"

    def enter_score(self, list_of_scores) :
        if len(list_of_scores) == 4 :
            self.set1_team1 = list_of_scores[0]
            self.set1_team2 = list_of_scores[1]
            self.set2_team1 = list_of_scores[2]
            self.set2_team2 = list_of_scores[3]
        elif len(list_of_scores) == 6 :
            self.set1_team1 = list_of_scores[0]
            self.set1_team2 = list_of_scores[1]
            self.set2_team1 = list_of_scores[2]
            self.set2_team2 = list_of_scores[3]
            self.set3_team1 = list_of_scores[4]
            self.set3_team2 = list_of_scores[5]
        else :
            print("log : Le format des scores n'est pas le bon")
            return None

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

    def __str__(self):
        return f"{self.number} :: {self.player1.name} et {self.player2.name} VS {self.player3.name} et {self.player4.name} ({self.score})"

    def set_score(self, score):
        self.score = score
        total_team1 = score.set1_team1 + score.set2_team1 + (score.set3_team1 or 0)
        total_team2 = score.set1_team2 + score.set2_team2 + (score.set3_team2 or 0)

        nb_set_won_team1 = (score.set1_team1 > score.set1_team2) + (score.set2_team1 > score.set2_team2) + ((score.set3_team1 or 0) > (score.set3_team2 or 0))
        nb_set_won_team2 = (score.set1_team1 < score.set1_team2) + (score.set2_team1 < score.set2_team2) + ((score.set3_team1 or 0) < (score.set3_team2 or 0))

        self.result = nb_set_won_team1 / 3
        self.delta = abs(ELO_K_COEF*(self.result - self.expected_result))

        if nb_set_won_team1 > nb_set_won_team2 :
            self.player1.win_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player2.win_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player3.lose_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)
            self.player4.lose_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)
        else :
            self.player1.lose_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player2.lose_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player3.win_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)
            self.player4.win_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)

        self.player1.update_winrate()
        self.player2.update_winrate()
        self.player3.update_winrate()
        self.player4.update_winrate()
        self.status = "Terminé"

    def reset_score(self):
        score = self.score
        total_team1 = score.set1_team1 + score.set2_team1 + (score.set3_team1 or 0)
        total_team2 = score.set1_team2 + score.set2_team2 + (score.set3_team2 or 0)

        nb_set_won_team1 = (score.set1_team1 > score.set1_team2) + (score.set2_team1 > score.set2_team2) + ((score.set3_team1 or 0) > (score.set3_team2 or 0))
        nb_set_won_team2 = (score.set1_team1 < score.set1_team2) + (score.set2_team1 < score.set2_team2) + ((score.set3_team1 or 0) < (score.set3_team2 or 0))

        self.result = nb_set_won_team1 / 3
        self.delta = math.abs(ELO_K_COEF*(self.result - self.expected_result))

        if nb_set_won_team1 > nb_set_won_team2 :
            self.player1.unwin_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player2.unwin_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player3.unlose_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)
            self.player4.unlose_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)
        else :
            self.player1.unlose_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player2.unlose_match(sets_won = nb_set_won_team1, points = total_team1, delta_elo=self.delta)
            self.player3.unwin_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)
            self.player4.unwin_match(sets_won = nb_set_won_team2, points = total_team2, delta_elo=self.delta)

        self.player1.update_winrate()
        self.player2.update_winrate()
        self.player3.update_winrate()
        self.player4.update_winrate()
        self.status = "Match annulé"
