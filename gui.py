import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog, messagebox, filedialog
from player import Player
from match import Match
from score import Score
from tournament import Tournament
from utils import save_tournament, load_tournament, clean_str, change_log_file, TYPE_DICO_FR
from itertools import combinations
import logging
import os

logging.basicConfig(
    filename='general_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

tournament = Tournament("test")
fenetre = tk.Tk()
fenetre.title("SLG Tournament Manager")

def alert():
    messagebox.showinfo("alerte", "Fonctionnalité pas encore implémentée")

def apropos():
    message = "Application développée par Guillaume GOY.\n"
    messagebox.showinfo("A propos", message)

def confirm_and_quit():
    if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?\nAvez vous pensé à sauvegarder ?"):
        logging.info("Quitting gui.py")
        fenetre.quit()

def loading_tournament():
    global tournament
    dir = filedialog.askdirectory(title="Choisir un dossier de sauvegarde")
    dir_name = os.path.basename(dir)
    try :
        tournament = load_tournament(dir_name)
        messagebox.showinfo("Succès", "La tournoi a été chargé avec succès.")
    except :
        messagebox.showerror("Erreur", "Le tournoi n'a pas pu être chargé\nLe dossier est il bien un dossier compatible ? Est il vide ?\nLe nom est il valide ?")
        return
    change_log_file(dir_name + "/log_file.log")
    logging.info("Loading tournament into gui.py")
    logging.info(f"{tournament}")
    update_all()

def adding_player(event=None):
    popup = tk.Toplevel(fenetre)
    popup.title("Ajouter un.e joueur.euse")
    popup.geometry("400x200")
    popup.grab_set()
    popup.bind('<Return>', lambda event: valider())

    tk.Label(popup, text="Entrez le nom : ").pack(pady=(10, 0))
    entree = tk.Entry(popup, width=30)
    entree.pack(pady=5)
    entree.focus_set()

    choix_var = tk.StringVar(value="")

    tk.Label(popup, text="Choisissez une option :").pack(pady=(10, 0))
    tk.Radiobutton(popup, text="Femme", variable=choix_var, value="F").pack()
    tk.Radiobutton(popup, text="Homme", variable=choix_var, value="M").pack()

    def valider():
        global tournament
        name = entree.get()
        gender = choix_var.get()
        if name == "":
            logging.warning("Empty name")
            messagebox.showwarning("Erreur", "Vous devez choisir un nom avec au moins un caractère")
            return
        for player in tournament.players_global :
            if player.name == name :
                logging.warning("Selecting a name already used")
                messagebox.showwarning("Erreur", "ce nom est déjà utilisé, veuillez recommencer en choississant un nom différent.")
        if not gender:
            logging.warning("No gender selection")
            messagebox.showwarning("Erreur", "Vous devez selectionner un genre.")
            return
        
        player = Player(name, gender)
        tournament.add_player(player)
        update_all()
        popup.destroy()

    tk.Button(popup, text="Valider", command=valider).pack(pady=10)

def creating_tournament():
    global tournament
    tournament_name = simpledialog.askstring("Nom du tournoi", "Veuillez choisir un nom pour votre tournoi :", parent=fenetre)
    tournament_name = clean_str(tournament_name)
    messagebox.showinfo("Confirmation du nom du tounoi", f"Vous avez saisi : {tournament_name}")
    if tournament_name == "":
        messagebox.showerror("Erreur", "Le nom du tounoi ne peut pas être vide!")
        return
    try :
        tournament = Tournament(tournament_name)
        save_tournament(tournament.name, tournament)
    except :
        messagebox.showerror("Erreur", "Le nom du tournoi n'est pas valide, merci de recommencer.")
        logging.error("Error with user entry for tournament name.")
    change_log_file(tournament_name + "/log_file.log")
    logging.info("Creating a new tournament with gui.py")
    update_all()

def saving_tounament(event=None):
    global tournament
    try :
        save_tournament(tournament.name, tournament)
        logging.info(f"gui.py : SAVING tournament\n{tournament}")
    except :
        logging.warning("No tournament to save")
        messagebox.showerror("Erreur de sauvegarde", "Il n'y a rien à sauvegarder pour le moment.")

def creating_new_match(type):
    if type not in ["random", "double_H", "double_F", "mixte"]:
        messagebox.showerror("Erreur", "Le type de match selectionné n'est pas conforme")
    check = tournament.create_random_match(cat=type)
    if check == 1:
        messagebox.showerror("Erreur", f"Nous n'avons pas pu créer de match {TYPE_DICO_FR[type]}\nVeuillez vérifier que les conditions sont respectées et reessayer.")
        return
    else :
        update_all()
        match = tournament.ongoing_matches[-1]
        messagebox.showinfo("Match créé", f"!! Match créé avec succès !!\n{match.player1.name} et {match.player2.name} contre {match.player3.name} et {match.player4.name}")

def infos():
    nb_total_points = 0
    for player in tournament.players_global:
        nb_total_points += player.points_won
    messagebox.showinfo("Informations sur le tournoi",
        f"------- Tounoi {tournament.name} --------------\n" +
        f"Nombre de participants : {len(tournament.players_global)}\n" +
        f"Nombre de matchs joués : {tournament.number_of_match}\n" +
        f"Nombre de points totals gagnés : {nb_total_points//2}\n"
    )

#Bindings
fenetre.bind('<Control-s>', saving_tounament)
fenetre.bind('<Control-j>', adding_player)

menubar = tk.Menu(fenetre)

menu1 = tk.Menu(menubar, tearoff=0)
menu1.add_command(label="Créer un nouveau tournoi", command=creating_tournament)
menu1.add_command(label="Charger un tournoi", command=loading_tournament)
menu1.add_separator()
menu1.add_command(label="Sauvegarder le tournoi", command=saving_tounament)
menu1.add_separator()
menu1.add_command(label="Quitter", command=confirm_and_quit)
menubar.add_cascade(label="Fichier", menu=menu1)

menu2 = tk.Menu(menubar, tearoff=0)
menu2.add_command(label="Ajouter un.e joueur.euse", command=adding_player)
menubar.add_cascade(label="Joueur.euses", menu=menu2)

menu3 = tk.Menu(menubar, tearoff=0)
menu3.add_command(label="Commencer un nouveau match aléatoire", command=lambda: creating_new_match("random"))
menu3.add_command(label="Commencer un nouveau match mixte", command=lambda: creating_new_match("mixte"))
menu3.add_command(label="Commencer un nouveau match double Femmes", command=lambda: creating_new_match("double_F"))
menu3.add_command(label="Commencer un nouveau match double Hommes", command=lambda: creating_new_match("double_H"))
menu3.add_separator()
menu3.add_command(label="Choisir une composition", command=lambda: creating_premade_match())
menubar.add_cascade(label="Matchs", menu=menu3)

menu4 = tk.Menu(menubar, tearoff=0)
menu4.add_command(label="Informations sur le tournoi", command=infos)
menu3.add_separator()
menu4.add_command(label="A propos", command=apropos)
menubar.add_cascade(label="Aide", menu=menu4)

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    try:
        l.sort(key=lambda t: int(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

#-------------------- INFOS PLAYERS FRAME -------------------------------

frame_infos_players = tk.Frame(fenetre)
frame_infos_players.grid(row=0, column=0, padx=10, pady=10, sticky="n")

title_info_players = tk.Label(frame_infos_players, text="Liste des joueuses et joueurs du tournoi", font=("Helvetica", 12, "bold"))
title_info_players.grid(row=0, column=0, columnspan=2, sticky="n", pady=(0, 5))

#-------------------- INFOS PLAYERS -----------------------------------

tree_info_players = ttk.Treeview(frame_infos_players, columns=("Nom", "Genre", "Statut", "Matchs"), show="headings", height=20)
tree_info_players.heading("Nom", text="Nom", command=lambda: treeview_sort_column(tree_info_players, "Nom", False))
tree_info_players.heading("Genre", text="Genre", command=lambda: treeview_sort_column(tree_info_players, "Genre", False))
tree_info_players.heading("Statut", text="Statut", command=lambda: treeview_sort_column(tree_info_players, "Statut", False))
tree_info_players.heading("Matchs", text="Matchs", command=lambda: treeview_sort_column(tree_info_players, "Matchs", False))

tree_info_players.column("Nom", width=120)
tree_info_players.column("Genre", width=40)
tree_info_players.column("Statut", width=80)
tree_info_players.column("Matchs", width=60)

tree_info_players.grid(row=1, column=0)

def update_list_of_players():
    tree_info_players.delete(*tree_info_players.get_children())
    for player in tournament.players_global:
        tree_info_players.insert("", "end", iid=player.name, values=(player.name, player.gender, player.status, player.matches_played))
    treeview_sort_column(tree_info_players, "Nom", False)

scrollbar_player = ttk.Scrollbar(frame_infos_players, orient="vertical", command=tree_info_players.yview)
scrollbar_player.grid(row=1, column=1, sticky="ns")
tree_info_players.configure(yscrollcommand=scrollbar_player.set)

#----------------------- LEADERBOARDS FRAME ------------------------------------

frame_leaderboards = tk.Frame(fenetre)
frame_leaderboards.grid(row=0, column=1, padx=10, pady=10, sticky="n")

title_leaderboards = tk.Label(frame_leaderboards, text="Classements", font=("Helvetica", 12, "bold"))
title_leaderboards.grid(row=0, column=0, columnspan=6, sticky="n", pady=(0, 5))

#----------------------- LEADERBOARD 1 : WINRATE ------------------------------------

tree_leaderboard1 = ttk.Treeview(frame_leaderboards, columns=("C.", "Nom", "Taux"), show="headings", height=20)

tree_leaderboard1.heading("C.", text="C.", command=lambda: treeview_sort_column(tree_leaderboard1, "C.", False))
tree_leaderboard1.heading("Nom", text="Nom")
tree_leaderboard1.heading("Taux", text="Taux")

tree_leaderboard1.column("C.", width=40)
tree_leaderboard1.column("Nom", width=120)
tree_leaderboard1.column("Taux", width=50)

tree_leaderboard1.grid(row=1, column=0)

def update_leaderboard1():
    tree_leaderboard1.delete(*tree_leaderboard1.get_children())
    for player in tournament.players_global:
        tree_leaderboard1.insert("", "end", iid=player.name, values=(player.winrate_position, player.name, int(player.winrate)))
    treeview_sort_column(tree_leaderboard1, "C.", False)

scrollbar_leaderboard1 = ttk.Scrollbar(frame_leaderboards, orient="vertical", command=tree_leaderboard1.yview)
scrollbar_leaderboard1.grid(row=1, column=1, sticky="ns")
tree_leaderboard1.configure(yscrollcommand=scrollbar_leaderboard1.set)

#----------------------- LEADERBOARD 2 : ELO ------------------------------------

tree_leaderboard2 = ttk.Treeview(frame_leaderboards, columns=("C.", "Nom", "ELO"), show="headings", height=20)

tree_leaderboard2.heading("C.", text="C.", command=lambda: treeview_sort_column(tree_leaderboard2, "C.", False))
tree_leaderboard2.heading("Nom", text="Nom")
tree_leaderboard2.heading("ELO", text="ELO")

tree_leaderboard2.column("C.", width=40)
tree_leaderboard2.column("Nom", width=120)
tree_leaderboard2.column("ELO", width=50)

tree_leaderboard2.grid(row=1, column=2)

def update_leaderboard2():
    tree_leaderboard2.delete(*tree_leaderboard2.get_children())
    for player in tournament.players_global:
        tree_leaderboard2.insert("", "end", iid=player.name, values=(player.elo_position, player.name, int(player.elo)))
    treeview_sort_column(tree_leaderboard2, "C.", False)

scrollbar_leaderboard2 = ttk.Scrollbar(frame_leaderboards, orient="vertical", command=tree_leaderboard2.yview)
scrollbar_leaderboard2.grid(row=1, column=3, sticky="ns")
tree_leaderboard2.configure(yscrollcommand=scrollbar_leaderboard2.set)

#----------------------- LEADERBOARD 3 : POINTS PER SET ------------------------------------

tree_leaderboard3 = ttk.Treeview(frame_leaderboards, columns=("C.", "Nom", "Points"), show="headings", height=20)

tree_leaderboard3.heading("C.", text="C.", command=lambda: treeview_sort_column(tree_leaderboard3, "C.", False))
tree_leaderboard3.heading("Nom", text="Nom")
tree_leaderboard3.heading("Points", text="Points")

tree_leaderboard3.column("C.", width=40)
tree_leaderboard3.column("Nom", width=120)
tree_leaderboard3.column("Points", width=50)

tree_leaderboard3.grid(row=1, column=4)

def update_leaderboard3():
    tree_leaderboard3.delete(*tree_leaderboard3.get_children())
    for player in tournament.players_global:
        tree_leaderboard3.insert("", "end", iid=player.name, values=(player.points_position, player.name, player.points_per_set))
    treeview_sort_column(tree_leaderboard3, "C.", False)

scrollbar_leaderboard3 = ttk.Scrollbar(frame_leaderboards, orient="vertical", command=tree_leaderboard3.yview)
scrollbar_leaderboard3.grid(row=1, column=5, sticky="ns")
tree_leaderboard3.configure(yscrollcommand=scrollbar_leaderboard3.set)

#----------------------------- Refreshes ----------------------------

def update_all():
    update_players_frame()
    update_list_of_matches()

def update_players_frame():
    update_leaderboard1()
    update_leaderboard2()
    update_leaderboard3()
    update_list_of_players()

#---------------------------- INFOS PLAYERS MENU -----------------------------

menu_joueur = tk.Menu(fenetre, tearoff=0)
menu_joueur.add_command(label="Afficher informations", command=lambda: display_player_info())
menu_joueur.add_command(label="Modifier le nom", command=lambda: modify_player())
menu_joueur.add_command(label="Supprimer", command=lambda: delete_player())
menu_joueur.add_command(label="Envoyer en pause", command=lambda: breaking_player())
menu_joueur.add_command(label="Remettre en attente", command=lambda: unbreaking_player())

#---------------------------- FUNCTIONS -----------------------------

def clic_droit_joueur(event):
    item_id = tree_info_players.identify_row(event.y)
    if item_id:
        tree_info_players.selection_set(item_id)
        tree_info_players.joueur_selectionne = item_id
        menu_joueur.tk_popup(event.x_root, event.y_root)

tree_info_players.bind("<Button-3>", clic_droit_joueur)
tree_info_players.bind("<Double-Button-1>", clic_droit_joueur)

def breaking_player():
    name = tree_info_players.joueur_selectionne
    player = next((p for p in tournament.players_global if p.name == name), None)
    check = tournament.break_player(player)
    if check != 0 :
        messagebox.showwarning("Erreur", "Ce joueur ne peut pas être envoyé en pause.\n(dans un match ou déjà en pause)")
    update_all()

def unbreaking_player():
    name = tree_info_players.joueur_selectionne
    player = next((p for p in tournament.players_global if p.name == name), None)
    check = tournament.unbreak_player(player)
    if check != 0:
        messagebox.showwarning("Erreur", "Ce joueur ne peut pas être remis en attente.\n(déjà en attente ou dans un match en cours)")
    update_all()

def display_player_info():
    name = tree_info_players.joueur_selectionne
    player = next((p for p in tournament.players_global if p.name == name), None)
    messagebox.showinfo("Information joueur", f"{player}")

def delete_player():
    name = tree_info_players.joueur_selectionne
    player = next((p for p in tournament.players_global if p.name == name), None)
    if player.status == "En match" :
        messagebox.showwarning("Erreur", "Ce joueur est en match et ne peut pas être supprimé")
        return
    confirm = messagebox.askyesno("Confirmation de suppression", f"Voulez-vous vraiment supprimer le joueur {player.name} du tournoi ?\nCette action est définitive, les informations et les statistiques seront perdues.")
    if not confirm:
        return
    logging.info(f"Delete player {player.name}")
    tournament.remove_player(player)
    update_all()

def modify_player():
    popup = tk.Toplevel(fenetre)
    popup.title("Modifier les informations joueur")
    popup.grab_set()

    tk.Label(popup, text="Entrez un nom : ").pack(pady=(10, 0))
    entree = tk.Entry(popup, width=30)
    entree.pack(pady=5)

    def valider():
        global tournament
        new_name = entree.get()
        if new_name == "":
            logging.warning("Empty name")
            messagebox.showwarning("Erreur", "Vous devez choisir un nom avec au moins un caractère")
            return
        cpt = 0
        for player in tournament.players_global :
            if player.name == new_name :
                cpt += 1
        if cpt > 1:
            logging.warning("Selecting a name already used")
            messagebox.showwarning("Erreur", "ce nom est déjà utilisé, veuillez recommencer en choississant un nom différent.")
        previous_name = tree_info_players.joueur_selectionne
        player = [p for p in tournament.players_global if p.name == previous_name][0]
        player.rename(new_name)
        update_all()
        popup.destroy()

    tk.Button(popup, text="Valider", command=valider).pack(pady=10)

#-------------------- MATCHES FRAME  -------------------------------

frame_list_of_matches = tk.Frame(fenetre)
frame_list_of_matches.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="n")

title_list_of_matches = tk.Label(frame_list_of_matches, text="Liste des matchs", font=("Helvetica", 12, "bold"))
title_list_of_matches.grid(row=0, column=0, columnspan=2, sticky="n", pady=(0, 5))

#---------------------- MATCHES ------------------------------------------------

tree_list_of_matches = ttk.Treeview(frame_list_of_matches, columns=("N.", "E1", "E2", "Score", "Statut"), show="headings", height=10)
tree_list_of_matches.heading("N.", text="N.", command=lambda: treeview_sort_column(tree_list_of_matches, "N.", False))
tree_list_of_matches.heading("E1", text="Equipe 1")
tree_list_of_matches.heading("E2", text="Equipe 2")
tree_list_of_matches.heading("Score", text="Score")
tree_list_of_matches.heading("Statut", text="Statut", command=lambda: treeview_sort_column(tree_list_of_matches, "Statut", False))
tree_list_of_matches.column("N.", width=40)
tree_list_of_matches.column("E1", width=200)
tree_list_of_matches.column("E2", width=200)
tree_list_of_matches.column("Score", width=120)
tree_list_of_matches.column("Statut", width=100)
tree_list_of_matches.grid(row=1, column=0)

scrollbar_matches = ttk.Scrollbar(frame_list_of_matches, orient="vertical", command=tree_list_of_matches.yview)
scrollbar_matches.grid(row=1, column=1, sticky="ns")
tree_list_of_matches.configure(yscrollcommand=scrollbar_matches.set)

def update_list_of_matches():
    tree_list_of_matches.delete(*tree_list_of_matches.get_children())
    for match in tournament.ongoing_matches + tournament.played_matches:
        tree_list_of_matches.insert("", "end", iid=match.number, values=(match.number, match.player1.name + " et " + match.player2.name, match.player3.name + " et " + match.player4.name, match.score or "----", match.status))
    treeview_sort_column(tree_list_of_matches, "Statut", False)

#---------------------------------- FUNCTIONS ---------------------------------------------

menu_match = tk.Menu(fenetre, tearoff=0)
menu_match.add_command(label="Afficher informations", command=lambda: display_match_info())
menu_match.add_command(label="Annuler le match", command=lambda: canceling_match())
menu_match.add_command(label="Entrer les scores", command=lambda: scoring_match())

def clic_droit_match(event):
    item_id = tree_list_of_matches.identify_row(event.y)
    if item_id:
        tree_list_of_matches.selection_set(item_id)
        tree_list_of_matches.match_selectionne = item_id
        menu_match.tk_popup(event.x_root, event.y_root)

tree_list_of_matches.bind("<Button-3>", clic_droit_match)
tree_list_of_matches.bind("<Double-Button-1>", clic_droit_match)

def display_match_info():
    match_number = int(tree_list_of_matches.match_selectionne)
    actual_match = [match for match in tournament.ongoing_matches + tournament.played_matches if match.number == match_number][0]
    messagebox.showinfo(
        "Information sur le match", f"numéro du match : {actual_match.number}\n" +
        f"{actual_match.player1.name} ({actual_match.player1_elo}) et {actual_match.player2.name} ({actual_match.player2_elo})\n" + 
        "Contre\n" +
        f"{actual_match.player3.name} ({actual_match.player3_elo}) et {actual_match.player4.name} ({actual_match.player4_elo})\n" +
        f"{actual_match.score or 'Match en cours'}\n" +
        f"Prédictions ELO : {actual_match.expected_result}\n" +
        f"Resultat du match : {actual_match.result}\n" +
        f"Enjeu sur ELO : {actual_match.delta}\n" +
        f"Match {actual_match.status}"
        )

def canceling_match():
    match_number = int(tree_list_of_matches.match_selectionne)
    actual_match = [match for match in tournament.ongoing_matches + tournament.played_matches if match.number == match_number][0]
    check = tournament.cancel_match(actual_match)
    if check == 1:
        messagebox.showerror("Erreur", "On ne peut pas annuler un match déjà terminé.")
        return
    elif check == 2:
        messagebox.showerror("Erreur", "On ne peut pas annuler un match déjà annulé.")
        return
    update_all()

def scoring_match():
    match_number = int(tree_list_of_matches.match_selectionne)
    actual_match = [match for match in tournament.ongoing_matches + tournament.played_matches if match.number == match_number][0]
    if actual_match in tournament.played_matches :
        messagebox.showerror("Erreur", "On ne peut pas entrer le scores d'un match déjà terminé")
        return
    def valider():
        valeurs = []
        for i, combo in enumerate(champs):
            val = combo.get()
            if i < 4 and val == "":
                messagebox.showerror("Erreur", f"Les resultats complet des deux premiers sets sont obligatoires.")
                return
            if val != "":
                try:
                    num = int(val)
                    if not (0 <= num <= 30):
                        raise ValueError
                    valeurs.append(num)
                except ValueError:
                    messagebox.showerror("Erreur", f"Les scores doivent être des valeurs entre 0 et 30.")
                    return
        
        score = Score()
        score.enter_score(valeurs)
        global tournament
        tournament.finish_match(actual_match, score)
        update_all()
        fenetre.destroy()

    fenetre = tk.Toplevel()
    fenetre.title("Entrée de valeurs")
    fenetre.grab_set() 
    fenetre.bind('<Return>', lambda event: valider())

    tk.Label(fenetre, text=f"Veuillez entrer les resultats pour le match :\n{actual_match.player1.name} et {actual_match.player2.name} contre {actual_match.player3.name} et {actual_match.player4.name}", font=("Helvetica", 12, "bold"), pady=10).pack()

    contenu = tk.Frame(fenetre, padx=10, pady=10)
    contenu.pack()
    options = [str(i) for i in range(31)]
    champs = []

    def creer_ligne(description, index1, index2):
        ligne = tk.Frame(contenu)
        ligne.pack(pady=5)

        tk.Label(ligne, text=description, width=25, anchor="w").pack(side="left")

        combo1 = ttk.Combobox(ligne, values=options, width=5)
        combo1.pack(side="left", padx=5)
        champs.append(combo1)

        combo2 = ttk.Combobox(ligne, values=options, width=5)
        combo2.pack(side="left", padx=5)
        champs.append(combo2)

    creer_ligne("Set 1 :", 0, 1)
    creer_ligne("Set 2 :", 2, 3)
    creer_ligne("Set 3 (si joué) :", 4, 5)

    champs[0].focus_set()

    bouton_valider = tk.Button(fenetre, text="Valider", command=valider)
    bouton_valider.pack(pady=10)

def creating_premade_match():
    global tournament
    list_of_names = [player.name for player in tournament.players_active] + [player.name for player in tournament.players_inactive]
    def valider():
        selections = [combo.get() for combo in combos]

        if "" in selections:
            messagebox.showerror("Erreur", "Veuillez sélectionner les 4 joueurs.")
            return

        if len(set(selections)) != 4:
            messagebox.showerror("Erreur", "Tous les joueur.euse.s doivent être différent.es.")
            return

        list_of_players = []
        for name in selections :
            find_player = [player for player in tournament.players_active if player.name == name] + [player for player in tournament.players_inactive if player.name == name]
            player = find_player[0]
            list_of_players.append(player)
        check = tournament.create_premade_match(list_of_players)
        if check != 0 :
            messagebox.showerror("Erreur", "Le match n'a pas pu être créer, veuillez recommencer")
            return
        update_all()
        fenetre.destroy()
        messagebox.showinfo("Match créé", f"Match créé avec succès :\n{tournament.ongoing_matches[-1]}")

    result = None 

    fenetre = tk.Toplevel()
    fenetre.title("Sélection des joueurs")
    fenetre.grab_set()

    tk.Label(fenetre, text="Veuillez choisir 4 joueurs différents pour le match :", font=("Arial", 12)).pack(pady=10)

    ligne = tk.Frame(fenetre)
    ligne.pack(pady=10)

    combos = []
    for i in range(4):
        combo = ttk.Combobox(ligne, values=list_of_names, width=15, state="readonly")
        combo.pack(side="left", padx=5)
        combos.append(combo)
        if i == 0:
            tk.Label(ligne, text=" et ").pack(side="left")
        elif i == 1:
            tk.Label(ligne, text=" contre ").pack(side="left")
        elif i == 2:
            tk.Label(ligne, text=" et ").pack(side="left")

    bouton = tk.Button(fenetre, text="Valider", command=valider)
    bouton.pack(pady=10)

    fenetre.wait_window() 
    return result

#------------------------------- BUTTONS FRAME -------------------------------------

frame_buttons = tk.Frame(fenetre)
frame_buttons.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

#-------------------------------- BUTTONS ------------------------------------------

btn0 = tk.Button(frame_buttons, text="Sauvegarder !!", command=lambda: saving_tounament())
btn1 = tk.Button(frame_buttons, text="Ajouter un.e Joueur.euse", command=lambda: adding_player())
btn2 = tk.Button(frame_buttons, text="Créer un mixte aléatoire", command=lambda: creating_new_match("mixte"))
btn3 = tk.Button(frame_buttons, text="Créer un double Femme aléatoire", command=lambda: creating_new_match("double_F"))
btn4 = tk.Button(frame_buttons, text="Créer un double Homme aléatoire", command=lambda: creating_new_match("double_H"))
btn5 = tk.Button(frame_buttons, text="Créer un match aléatoire", command=lambda: creating_new_match("random"))
btn6 = tk.Button(frame_buttons, text="Choisir une composition", command=lambda: creating_premade_match())

btn0.pack(side="left", padx=5)
btn1.pack(side="left", padx=5)
btn2.pack(side="left", padx=5)
btn3.pack(side="left", padx=5)
btn4.pack(side="left", padx=5)
btn5.pack(side="left", padx=5)
btn6.pack(side="left", padx=5)

#------------------------------ FENETRE LOOP -----------------------------------

fenetre.config(menu=menubar)

fenetre.mainloop()