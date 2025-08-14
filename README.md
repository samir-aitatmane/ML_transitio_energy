Documentation : interface.py
Introduction
Le fichier interface.py est un script Python utilisant Streamlit pour créer une interface utilisateur permettant de simuler les coûts et les gains liés à des travaux de rénovation énergétique. Il intègre des calculs basés sur des données d'entrée fournies par l'utilisateur et des fichiers CSV contenant des informations sur les coûts unitaires et les caractéristiques des travaux.

Structure du Code
1. Importation des bibliothèques
Le script commence par importer les bibliothèques nécessaires :

streamlit : Pour créer l'interface utilisateur.
numpy : Pour les calculs numériques.
pickle : Pour charger le modèle de prédiction.
itertools : Pour générer des combinaisons de travaux.
matplotlib.pyplot : Pour créer des graphiques.
pandas : Pour manipuler les fichiers CSV contenant les données.
2. Interface utilisateur
L'interface utilisateur est divisée en plusieurs sections :

2.1. Paramètres du logement
L'utilisateur peut entrer les informations suivantes :

Surface habitable : Surface en m².
Année de construction : Année de construction du logement.
DPE : Classe énergétique actuelle du logement.
Région : Région géographique du logement.
2.2. Travaux effectués
L'utilisateur peut sélectionner les travaux qu'il souhaite effectuer parmi une liste :

Isolation (combles, extérieure, intérieure, plancher).
Chauffage.
Ventilation.
Eau chaude sanitaire (ECS).
Ouvertures (menuiseries).
Régulation du chauffage.
Toiture.
2.3. Isolation
L'utilisateur peut spécifier :

Type d'isolant (par exemple, laine de verre, biosourcé).
Surface isolée (en m² ou en pourcentage).
Épaisseur de l'isolant (en cm).
2.4. Mappings
Des fonctions de mapping sont définies pour convertir les données utilisateur en codes numériques compréhensibles par le modèle de prédiction.

3. Calcul du coût total
La fonction calcul_cout_total_intelligent calcule le coût total des travaux en fonction des données utilisateur et des fichiers CSV contenant les prix unitaires.

3.1. Fonctionnement
Chargement des fichiers CSV :

Les fichiers CSV contiennent les prix unitaires pour chaque type de travail (par exemple, cout_isolation.csv, cout_chauffage.csv).
Calcul des coûts par type de travail :

Pour chaque travail sélectionné, le coût est calculé en multipliant un prix unitaire par une quantité (par exemple, surface, nombre d'unités).
Ajout au coût total :

Les coûts individuels sont additionnés pour obtenir le coût total.
Retour des résultats :

La fonction retourne le coût total et un dictionnaire contenant les détails des coûts par type de travail.
4. Prédiction du gain
La section "✨ Estimer le gain" utilise un modèle de machine learning pour prédire le gain énergétique en fonction des travaux sélectionnés.

4.1. Fonctionnement
Préparation des données :

Les données utilisateur sont transformées en un tableau de caractéristiques (features) à l'aide de la fonction generer_donnees_modele.
Chargement du modèle :

Le modèle est chargé depuis un fichier modele_EF_v5.pkl.
Prédiction :

Le modèle prédit le gain énergétique en pourcentage.
Affichage des résultats :

Le gain estimé est affiché dans l'interface.
5. Calcul des combinaisons
La section "📊 Calculer les coûts et les gains individuels et les combinaisons" calcule les coûts et les gains pour :

Chaque travail individuel.
Toutes les combinaisons possibles des travaux.
5.1. Fonctionnement
Travaux individuels :

Pour chaque travail, le coût et le gain sont calculés séparément.
Combinaisons de travaux :

Toutes les combinaisons possibles des travaux sont générées à l'aide de itertools.combinations.
Le coût et le gain sont calculés pour chaque combinaison.
Affichage des résultats :

Les résultats sont affichés dans des tableaux Streamlit.
Un graphique est généré pour comparer les combinaisons en fonction du coût et du gain.
6. Exemple avec tous les inputs à 0
La section "🔧 Tester avec tous les inputs à 0" permet de tester le comportement du modèle avec des données où tous les paramètres sont initialisés à 0.

6.1. Fonctionnement
Les données utilisateur sont initialisées à 0 ou à des valeurs par défaut.
Les données sont affichées dans l'interface et imprimées dans le terminal.
Cela permet de vérifier que le modèle fonctionne correctement avec des données minimales.
7. Fonction generer_donnees_modele
Cette fonction génère les données à envoyer au modèle de prédiction. Elle :

Neutralise les paramètres des travaux non sélectionnés.
Transforme les données utilisateur en un tableau de caractéristiques (features) compréhensible par le modèle.
8. Graphique des combinaisons
Un graphique est généré pour comparer les combinaisons de travaux :

Axe X : Coût (€).
Axe Y : Gain (%).
Chaque point représente une combinaison de travaux, avec une annotation indiquant les travaux inclus.
Résumé
Le fichier interface.py est un outil complet pour simuler les coûts et les gains liés à des travaux de rénovation énergétique. Il permet :

De calculer le coût total des travaux.
De prédire le gain énergétique.
De comparer les coûts et les gains pour différentes combinaisons de travaux.
Ce script est conçu pour être interactif et intuitif, offrant une visualisation claire des résultats pour aider les utilisateurs à prendre des décisions éclairées.

