# Web-Scraping-Europresse

Commandes de la CLI

    --start-url
        Description: URL de départ pour la connexion au site
        Exemple: --start-url https://portaildeconnexion

    --login
        Description: Nom d'utilisateur pour la connexion
        Exemple: --login utilisateur

    --password
        Description: Mot de passe pour la connexion.
        Exemple: --password motdepasse

    --keywords
        Description: Liste de mots-clés pour la recherche, séparés par des virgules
        Exemple: --keywords "Arts et culture,Droit,Économie"

    --max-texts
        Description: Nombre maximum de textes à scraper pour chaque mot-clé
        Exemple: --max-texts 100

    --min-length
        Description: Longueur minimale des textes à scraper (en mots)
        Exemple: --min-length 100

    --max-length
        Description: Longueur maximale des textes à scraper (en mots)
        Exemple: --max-length 500

    --scrolls-number
        Description: Nombre de fois à défiler vers le bas pour charger plus de contenu
        Exemple: --scrolls-number 10

    --latency
        Description: Délai (en secondes) pour laisser le temps à la page de charger
        Exemple: --latency 4

    --data-folder
        Description: Nom du dossier où les données seront stockées
        Exemple: --data-folder data

    --output-format



    --help
        Description: Affiche l'aide et les descriptions des commandes disponibles
        Exemple: --help



python scraper.py --start-url https://...\
--login utilisateur --password motdepasse \
--keywords "Arts et culture,Droit" \
--max-texts 100 --min-length 100 --max-length 500 \
--scrolls-number 10 --latency 4 --data-folder data --output-format jsonl --verb
