# 📊 SEO Analyzer Dashboard

Dashboard interactif pour visualiser et analyser les résultats d'analyse SEO. Construit avec Streamlit pour une interface moderne et réactive.

## ✨ Fonctionnalités

### 🎯 Page Principale (Vue d'ensemble)
- **Scores globaux** avec gauges interactives  
- **Graphique radar** des performances par catégorie
- **Métriques en temps réel** avec indicateurs visuels
- **Forces et faiblesses** identifiées automatiquement
- **Analyses IA avancées** (LLM/GEO)

### 🔍 Analyse Détaillée
- **Vue complète** d'un rapport spécifique
- **Métriques par catégorie** avec visualisations
- **Core Web Vitals** détaillées (Desktop/Mobile)
- **Analyses améliorées** (naturalité, SSR, fraîcheur)
- **Données JSON brutes** accessibles

### 📊 Comparaisons et Tendances
- **Comparaison multi-sites** avec heatmaps
- **Évolution temporelle** d'un domaine
- **Analyse détaillée comparative**
- **Tableaux interactifs** avec mise en forme

## 🚀 Lancement Rapide

### Méthode 1: Script de lancement
```bash
# Depuis la racine du projet
uv run python run_dashboard.py
```

### Méthode 2: Streamlit direct
```bash
# Depuis la racine du projet  
uv run streamlit run dashboard/app.py --server.port=8501
```

Le dashboard sera accessible à l'adresse: **http://localhost:8501**

## 📁 Structure

```
dashboard/
├── app.py                      # Application principale
├── components/
│   └── charts.py              # Composants de visualisation
├── utils/
│   └── data_loader.py         # Chargement et traitement des données
├── pages/
│   ├── 1_🔍_Analyse_Détaillée.py
│   └── 2_📊_Comparaisons.py
└── README.md                  # Ce fichier
```

## 🎨 Interface Utilisateur

### Navigation
- **Sidebar** : Configuration et sélection des rapports
- **Onglets** : Organisation du contenu par thème
- **Pages** : Navigation multi-pages via la sidebar Streamlit

### Visualisations
- **Gauges** : Scores individuels (0-100)
- **Graphiques radar** : Vue d'ensemble multi-catégories  
- **Graphiques en barres** : Comparaisons entre sites
- **Graphiques temporels** : Évolution dans le temps
- **Heatmaps** : Matrices de performance
- **Waterfall** : Métriques de performance détaillées

### Données Affichées
- **Score Global SEO** : Moyenne pondérée de toutes les catégories
- **Scores par Catégorie** : Contenu, Structure, Maillage, Performance, AIO, IA
- **Métriques Techniques** : Core Web Vitals, compatibilité SSR, données structurées
- **Analyses IA** : E-A-T, intention de recherche, authenticité du contenu
- **Recommandations** : Suggestions d'amélioration priorisées

## 🔧 Configuration

### Variables d'Environnement
Le dashboard utilise les mêmes variables d'environnement que l'analyseur principal (fichier `.env`).

### Données Sources
- **Rapports Raw** : `reports/raw/report_*.json`
- **Rapports Scores** : `reports/scores/scores_*.json`

### Cache
Streamlit met en cache les données chargées pour des performances optimales. Le cache se rafraîchit automatiquement si les fichiers changent.

## 🎯 Cas d'Usage

### 1. Monitoring SEO
- Suivi des performances d'un site dans le temps
- Identification des régressions et améliorations  
- Alertes sur les scores critiques

### 2. Audit Comparatif  
- Benchmarking concurrentiel
- Identification des meilleures pratiques
- Priorisation des optimisations

### 3. Reporting Client
- Tableaux de bord visuels pour les clients
- Export de visualisations
- Démonstration des résultats d'optimisation

## 🔄 Architecture pour API Future

Le dashboard est conçu pour faciliter la transition vers une architecture API/Frontend :

### Couche de Données (`utils/data_loader.py`)
- Interface abstraite pour l'accès aux données
- Facilement remplaçable par des appels API REST
- Gestion du cache et des erreurs

### Composants de Visualisation (`components/charts.py`)  
- Logique métier séparée de l'interface
- Composants réutilisables
- Compatible avec des frameworks comme React/Vue

### Structure Modulaire
- Séparation claire des responsabilités
- Code découplé et testable
- Configuration centralisée

## 🚀 Déploiement

### Local (Développement)
```bash
uv run python run_dashboard.py
```

### Production avec Docker
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Cloud (Streamlit Cloud, Heroku, etc.)
Le dashboard peut être déployé sur la plupart des plateformes cloud supportant Python/Streamlit.

## 📈 Métriques de Performance

Le dashboard charge et affiche plusieurs types de métriques :

### Scores SEO (0-100)
- **Contenu & Sémantique** : Richesse, style, sources, fraîcheur
- **Structure Technique** : H1-H6, métadonnées, images, données structurées  
- **Maillage Interne** : Liens, ancres, distribution
- **Performance** : Core Web Vitals (LCP, INP, CLS)
- **Optimisation AIO** : Questions/réponses, données quantifiables
- **Analyse IA** : E-A-T, intention, couverture thématique

### Métriques Avancées
- **Densité informationnelle** : Richesse du contenu
- **Authenticité** : Détection de contenu IA-généré
- **Compatibilité SSR** : Accessibilité pour les crawlers
- **Fraîcheur temporelle** : Présence d'années dans les métadonnées

## 🎨 Personnalisation

### Thème et Style
Le CSS personnalisé est défini dans `app.py` et peut être modifié pour :
- Changer les couleurs de marque
- Ajuster la mise en page
- Personnaliser les badges et métriques

### Nouvelles Visualisations  
Ajouter de nouveaux graphiques dans `components/charts.py` :
```python
def create_custom_chart(data):
    fig = go.Figure(...)
    return fig
```

### Pages Supplémentaires
Créer de nouvelles pages dans `pages/` :
```python
# pages/3_📈_Page_Custom.py
import streamlit as st
st.title("Ma Page Personnalisée")
```

## 🐛 Dépannage

### Erreurs Courantes

**"Aucun rapport disponible"**
- Vérifiez que `reports/raw/` contient des fichiers `report_*.json`
- Lancez d'abord `uv run python -m src.page_analyzer`

**"Impossible de charger les données"**
- Vérifiez les permissions de lecture sur les dossiers `reports/`
- Vérifiez que les fichiers JSON ne sont pas corrompus

**Erreurs de dépendances**
- Installez les dépendances : `uv sync`
- Vérifiez la version Python : `python --version` (>= 3.11)

### Logs et Debug
Activer le mode debug de Streamlit :
```bash
streamlit run dashboard/app.py --logger.level=debug
```

## 🔮 Évolutions Prévues

### Version API + Frontend
- **Backend FastAPI** : API REST pour les données
- **Frontend React** : Interface utilisateur moderne
- **Base de données** : Stockage persistant des rapports
- **Authentification** : Gestion des utilisateurs et permissions

### Nouvelles Fonctionnalités
- **Alertes automatisées** : Notifications sur les seuils
- **Rapports programmés** : Analyses récurrentes
- **Intégrations** : Slack, Teams, email
- **Export avancé** : PDF, Excel, API

---

🎯 **Objectif** : Fournir une interface intuitive et puissante pour exploiter pleinement les analyses SEO générées par l'outil.