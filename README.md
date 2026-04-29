# 🌾 AgriData Cameroun — Application de Collecte & Analyse Agricole

Application Python/Flask de collecte et analyse descriptive des données agricoles.

## Fonctionnalités
- **Formulaire multi-sections** : Localisation, Cultures, Élevage, Météo/Sol, Intrants
- **Tableau de bord analytique** : KPIs, graphiques, statistiques descriptives
- **Export Excel** : téléchargement des données brutes
- **Stockage JSON** local (facilement remplaçable par SQLite/PostgreSQL)

## Lancement local (Windows)

```bash
cd agridata
pip install -r requirements.txt
python app.py
```
Ouvrir : http://localhost:5000

## Déploiement en ligne (gratuit)

### Option 1 — Railway.app
1. Créer un compte sur https://railway.app
2. New Project → Deploy from GitHub
3. Pousser ce dossier sur GitHub
4. Railway détecte Flask automatiquement

Ajouter un fichier `Procfile` :
```
web: python app.py
```
Et modifier `app.py` dernière ligne :
```python
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
```

### Option 2 — Render.com
1. Compte sur https://render.com
2. New Web Service → connecter GitHub
3. Start Command : `python app.py`
4. Free tier disponible

### Option 3 — PythonAnywhere
1. Compte sur https://pythonanywhere.com
2. Upload le dossier
3. Configurer WSGI pointant vers `app.py`

## Structure du projet
```
agridata/
├── app.py              # Serveur Flask + API REST
├── requirements.txt    # Dépendances Python
├── data/
│   └── collectes.json  # Données (créé automatiquement)
└── templates/
    ├── base.html       # Layout commun
    ├── index.html      # Page d'accueil
    ├── collecte.html   # Formulaire de collecte
    └── dashboard.html  # Tableau de bord analytique
```
