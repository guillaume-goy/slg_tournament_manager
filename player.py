#player.py
from config import ELO_START

class Player:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender #Genre ("F" ou "M")
        self.status = "En attente" # "En attente" "En match" "En pause"

        self.sets_played = 0 #Nombres de sets joués
        self.matches_played = 0 #Nombres de matchs joués

        self.points_won = 0 #Nombre de points gagnés
        self.sets_won = 0 #Nombre de sets gagnés
        self.matches_won = 0 #Nombre de matchs gagnés
        self.points_per_set = 0 #Nombres de points gagnés par set en moyenne

        self.winrate = 0
        self.elo = ELO_START #Points elo du joueur (WIP)
        self.elo_position = None
        self.winrate_position = None
        self.points_position = None

        self.partners_history = set()  #Partenaires avec lesquels on a déjà joué.

    def __str__(self):
        return (
            f"Nom du joueur : {self.name}\n" +
            f"Genre du joeur : {self.gender}\n" +
            f"Match joués : {self.matches_played}\n" +
            f"Match gagnés : {self.matches_won}\n" +
            f"Sets gagnés : {self.sets_won}\n" +
            f"Points gagnés : {self.points_won}\n" +
            f"Elo du joueur : {self.elo}\n" +
            f"Historique des partenaire : {[partner.name for partner in self.partners_history]}\n"
        )
    
    def rename(self, name):
        self.name = name

    def win_match(self, sets_won=2, sets_played=2, points=0, delta_elo=0):
        self.matches_won += 1
        self.matches_played += 1
        self.sets_won += sets_won
        self.sets_played += sets_played
        self.points_won += points
        self.elo += delta_elo

    def lose_match(self, sets_won=0, sets_played=2, points=0, delta_elo=0):
        self.matches_played += 1
        self.sets_won += sets_won
        self.sets_played += sets_played
        self.points_won += points
        self.elo -= delta_elo

    def unwin_match(self, sets_won=2, sets_played=2, points=0, delta_elo=0):
        self.matches_won -= 1
        self.matches_played -= 1
        self.sets_won -= sets_won
        self.sets_played -= sets_played
        self.points_won -= points
        self.elo -= delta_elo

    def unlose_match(self, sets_won=0, sets_played=2, points=0, delta_elo=0):
        self.matches_played -= 1
        self.sets_won -= sets_won
        self.sets_played -= sets_played
        self.points_won -= points
        self.elo += delta_elo

    def update_history(self, other):
        self.partners_history.add(other)
        other.partners_history.add(self)

    def remove_from_history(self, other):
        self.partners_history.discard(other)
        other.partners_history.discard(self)
        
    def update_winrate(self):
        if self.matches_played == 0:
            return 0
        self.winrate =  100 * self.matches_won / self.matches_played

    def update_points_per_set(self):
        if self.sets_played == 0:
            self.points_per_set = 0
        else :
            self.points_per_set = int(10*self.points_won / self.sets_played)/10

    def update_all(self):
        self.update_points_per_set()
        self.update_winrate()

    def reset_stats(self):
        self.points_won = 0 #Nombre de points gagnés
        self.sets_won = 0 #Nombre de sets gagnés
        self.matches_won = 0 #Nombre de matchs gagnés
        self.matches_played = 0 #Nombres de matchs joués
        self.elo = ELO_START #Points elo du joueur (WIP)
        self.partners_history = set()  #Partenaires avec lesquels on a déjà joué.