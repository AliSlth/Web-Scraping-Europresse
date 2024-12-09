#Author : Ali Slth
import os
import argparse
import json
import re
import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import hashlib

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Scraping Articles for Training and Testing.')
    parser.add_argument('--start_urls', required=True, help='URL de connexion au site.')
    parser.add_argument('--login', required=True, help='Nom d\'utilisateur pour la connexion.')
    parser.add_argument('--mdp', required=True, help='Mot de passe pour la connexion.')
    parser.add_argument('--folder', default='data', help='Nom du dossier pour stocker les données.')
    parser.add_argument('--keywords', nargs='+', default=["Arts et culture", "Droit", "Économie", "Environnement", "Politique et gouvernement", "Santé", "Sciences et technologie", "Sports"],
                        help='Liste des mots-clés pour le scraping.')
    parser.add_argument('--nb_texts_to_scrap', type=int, default=100, help='Nombre de textes à scraper pour chaque mot-clé.')
    parser.add_argument('--min_length', type=int, default=100, help='Nombre minimum de mots dans le texte.')
    parser.add_argument('--max_length', type=int, default=500, help='Nombre maximum de mots dans le texte.')
    parser.add_argument('--latency', type=int, default=4, help='Délai pour le chargement des pages.')
    parser.add_argument('--scrolls_number', type=int, default=10, help='Nombre de défilements nécessaires pour charger le contenu.')
    return parser.parse_args()

def load_scraped_titles(folder) -> list:
    """Fonction qui charge les titres des articles déjà scrappés à partir du fichier texte
            Retour:
            Une liste de dictionnaires représentant les titres d'articles déjà scrappés
            Chaque dictionnaire peut contenir des clés telles que 'title' et 'label'
    """
    scraped_titles = []
    try:
        with open(os.path.join(folder, 'scraped_articles.txt'), 'r') as f:
            for line in f:
                scraped_titles.append(json.loads(line))
        print("Les titres des articles déjà scrapés ont été chargés.")
    except FileNotFoundError:
        print("Le fichier 'scraped_articles.txt' est introuvable. Création du fichier dans le dossier ", folder)
        with open(os.path.join(folder, 'scraped_articles.txt'), 'w', encoding='utf-8'):
            pass  # Créer un fichier vide
    return scraped_titles

def generate_hash(title, text, label):
    """Generate a hash for deduplication based on title, text, and label."""
    return hashlib.sha256(f"{title}{text}{label}".encode('utf-8')).hexdigest()

def crawl_data(args) -> list:
    """
    Fonction qui permet de scraper des articles sur une plateforme donnée en utilisant Selenium.
    Cette fonction se connecte à un site web, effectue des recherches en utilisant des mots-clés,
    et scrape les textes des articles correspondants.Les textes et les titres des articles sont ensuite enregistrés
    au format JSON Lines dans le dossier spécifié

    Entrée:
    params (dict): Dictionnaire contenant des paramètres nécessaires pour le scraping, tels que:
          - start_urls: URL de connexion
          - login: Nom d'utilisateur pour la connexion
          - mdp: Mot de passe pour la connexion
          - keywords: Liste des mots-clés pour la recherche
          - step: Taille du pas de défilement pour le scrolling
          - latency: Délai pour laisser le temps à la page de charger
          - scrolls_number Nombre de défilements nécessaires pour charger le contenu
          - nb_texts_to_scrap: Nombre de textes à scraper pour chaque mot-clé
          - folder: Nom du dossier où les données sont stockées
          - max_length : Nombre maximum de mots contenus dans le texte
          - min_length : Nombre minimum de mots contenus dans le texte
    Sortie:
        - Retourne la liste des textes scrappés, organisé sous forme de dictionnaire
        Chaque dictionnaire contient des clés comme texte, label, url, title, et id
    """

    data_list = []
    articles_list = []
    
    folder_name = args.folder
    keywords = args.keywords
    nb_texts_to_scrap = args.nb_texts_to_scrap
    min_length = args.min_length
    max_length = args.max_length
    latency = args.latency
    scrolls_number = args.scrolls_number

    # Crée le dossier "data" s'il n'existe pas encore
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)  # Créer le dossier si nécessaire
    except PermissionError:
        print("Permission refusée : impossible de créer le dossier 'data'.")

    # Charger les titres scrappés
    scraped_titles = load_scraped_titles(folder_name)

    # Initialiser le navigateur Firefox
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)

    try:
        # Ouverture de l'url
        driver.get(args.start_urls)
        time.sleep(2)

        # Champs utilisateur et mot de passe
        driver.find_element(By.ID, "user").send_keys(args.login)
        driver.find_element(By.ID, "pass").send_keys(args.mdp)
        driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2)

        # Vérifier si on est toujours sur la page de connexion  (ex. si le mdp fonctionne pas)
        if driver.current_url == args.start_urls:
            print("Échec de connexion: login ou mot de passe incorrect")
            return None

        print("Connexion établie.")
        time.sleep(latency)

        #Scraper
        for keyword in keywords:
            time.sleep(latency)
            print(f"Recherche pour le mot-clé: {keyword}")

            # Options de recherche
            select_date = Select(driver.find_element(By.ID, "DateFilter_DateRange"))
            select_date.select_by_value("9")  # "Toutes les archives"
            select_source = Select(driver.find_element(By.ID, "CriteriaSet"))
            select_source.select_by_value("210340")  # France
            time.sleep(latency)

            # Entrer les mots-clés dans la barre de recherche
            keywords_input = driver.find_element(By.ID, "Keywords")
            keywords_input.clear()
            keywords_input.send_keys("SECT=", keyword)
            driver.find_element(By.ID, "btnSearch").click()
            time.sleep(latency)

            # Scroller pour charger les liens
            for _ in range(scrolls_number):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(latency)

            links = driver.find_elements(By.CSS_SELECTOR, 'ul#container.documentList.items a.docList-links')
            print(f"Nombre de liens récupérés : {len(links)}")

            with tqdm(total=nb_texts_to_scrap, desc=f"Scraping '{keyword}'") as pbar:
                for link in links:
                    title = link.text
                    # Vérifier si l'item existe
                    exists = any(item['title'] == title and item['label'] == keyword for item in scraped_titles)
                    if exists:
                        print(f"'{title}' avec le label '{keyword}' a déjà été scrappé.")
                        continue

                    link.click()  # Clic sur le lien
                    time.sleep(2)

                    # Extraction du texte de l'article
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    doc_text_div = soup.find('div', id='docText')
                    if doc_text_div:
                        paragraphs = doc_text_div.find_all('p')
                        extracted_text = '\n'.join([p.get_text().strip() for p in paragraphs])
                        cleaned_text = re.sub(r'\s*\n\s*', ' ', extracted_text).strip()

                        # Vérification de la longueur du texte
                        if min_length < len(cleaned_text.split()) < max_length:
                            # Génération d'un hash
                            article_hash = generate_hash(title, cleaned_text, keyword)
                            if not any(item.get('hash') == article_hash for item in data_list):
                                data_dict = {
                                    "texte": cleaned_text,
                                    "label": keyword,
                                    "url": driver.current_url,
                                    "title": title,
                                    "hash": article_hash 
                                }
                                data_list.append(data_dict)
                                articles_list.append({"title": title, "label": keyword})

                                pbar.update(1)
                            else:
                                print(f"Article déjà présent dans les données: {title}")
                        else:
                            print(f"Texte qui ne correspond pas à la longueur souhaitée : {driver.current_url}")

                    time.sleep(1)
                    driver.back()
                    time.sleep(2)

        # Sauvegarder les articles
        with open(os.path.join(folder_name, 'data_train.jsonl'), 'a', encoding='utf-8') as jsonl_file:
            for data in data_list:
                json.dump(data, jsonl_file, ensure_ascii=False)
                jsonl_file.write('\n')

        with open(os.path.join(folder_name, 'scraped_articles.txt'), 'a', encoding='utf-8') as f:
            for article in articles_list:
                f.write(json.dumps(article, ensure_ascii=False) + '\n')

    finally:
        driver.quit()

if __name__ == "__main__":
    args = parse_arguments()
    crawl_data(args)
