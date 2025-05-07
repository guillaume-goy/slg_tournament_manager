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