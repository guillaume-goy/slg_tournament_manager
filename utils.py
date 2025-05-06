#utils.py
import os
import pickle
import logging
from tournament import Tournament
import re
import unicodedata

def save_tournament(name : str, tournament : Tournament):
    logging.info(f"Saving tournament with name: {name}")
    try :
        os.makedirs(f"{name}", exist_ok=True)
        file_path = os.path.join(f"{name}", "tournament_data.pkl")
        with open(file_path, "wb") as f:
            pickle.dump(tournament, f)
    except Exception as e:
        logging.error(f"Unable to save tournament {name}: {e}")

def load_tournament(name : str):
    logging.info(f"loading tournament with name: {name}")
    file_path = os.path.join(f"{name}", "tournament_data.pkl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier non trouvé : {file_path}")
    with open(file_path, 'rb') as f:
        #tournament = Tournament(name)
        tournament = pickle.load(f)
    return tournament

def clean_str(texte):
    texte = unicodedata.normalize('NFD', texte).encode('ascii', 'ignore').decode('utf-8')
    texte = texte.replace(' ', '_')
    texte = re.sub(r'[^\w]', '', texte)
    return texte

def change_log_file(new_filename):
    logger = logging.getLogger()

    # Supprimer les anciens FileHandlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()

    # Ajouter un nouveau FileHandler
    file_handler = logging.FileHandler(new_filename)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)