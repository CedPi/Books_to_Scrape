# Books to Scrap

### Formation Python OC - Projet 02.
#### Projet de scrapping du site [https://books.toscrape.com/](https://books.toscrape.com/)


## Installation

Cloner le projet
```bash
git clone https://github.com/CedPi/Books_to_Scrape.git
```

Se placer dans le répertoire
```bash
cd Books_to_Scrape
```

Créer l'environnement virtuel
```bash
python -m venv env
```

Activer l'environnement virtuel (Windows)
```bash
source env/Scripts/activate
```

Activer l'environnement virtuel (Linux)
```bash
source env/bin/activate
```

Installer les modules
```bash
$ pip install -r requirements.txt
```

## Utilisation
Lancer le script main.py
```bash
python main.py
```

## Sortie
Le script crée un répertoire "extraction" avec l'arborescence suivante
```bash
extraction/
|
|----csv/
|    |----categorie_1.csv
|    |----categorie_2.csv
|
|----images/
     |----categorie_1/
     |    |----image_a.xxx
     |    |----image_b.xxx
     |
     |----categorie_2/
          |----image_c.xxx
          |----image_d.xxx
```
