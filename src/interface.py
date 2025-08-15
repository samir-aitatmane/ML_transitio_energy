import streamlit as st
import numpy as np
import pickle
import itertools
##import matplotlib.pyplot as plt
import pandas as pd

# === INTERFACE STREAMLIT ===

st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(120deg, #e0eafc 0%, #cfdef3 100%);}
    .big-font {font-size:22px !important; color:#1a237e;}
    .section-title {font-size:18px !important; color:#1565c0; margin-top: 30px;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="big-font">🏡 Simulation rénovation énergétique</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Paramètres du logement</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    surface = st.number_input("Surface habitable (m²)", min_value=10, max_value=500, value=70)
    annee = st.number_input("Année de construction", min_value=1900, max_value=2025, value=1990)
    dpe = st.selectbox("DPE", ["Pas de DPE", "A", "B", "C", "D", "E", "F", "G"])
    region = st.selectbox("Région", [
        "Île-de-France", "Hauts-de-France", "Grand Est", "Normandie", "Bretagne",
        "Pays de la Loire", "Centre-Val de Loire", "Bourgogne-Franche-Comté",
        "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine", "Occitanie", "PACA et Corse"
    ])
with col2:
    travaux = st.multiselect(
        "Travaux effectués",
        [
            "Isolation combles", "Isolation extérieure", "Isolation plancher",
            "Chauffage", "Ventilation", "Eau chaude", "Ouvertures",
            "Régulation chauffage", "Toiture", "Rénovation sans isolation toiture",
            "Isolation intérieure"
        ]
    )
    chauffage_actuel = st.selectbox("Type de chauffage actuel", ["Gaz", "Fioul", "Électrique", "Bois", "Mixte", "Autre"])
    age_chauffage = st.selectbox("Âge du chauffage actuel", ["<10 ans", "10–15 ans", "15–20 ans", ">20 ans", "Rénové", "Inconnu"])
    ventilation = st.selectbox("Système de ventilation prévu", ["Aucune", "Simple flux"])
    ecs_type = st.selectbox("Type d'ECS (Eau Chaude Sanitaire)", ["Ballon ECS vertical", "Chauffe-eau thermodynamique", "Aucun"])

# Ajout spec0_chauffage
spec0_chauffage_label = st.selectbox(
    "Nouveau système de chauffage",
    ["Pas de changement", "Chaudière condensation", "PAC", "Radiateurs électriques"]
)
spec0_mapping = {
    "Pas de changement": -999,
    "Chaudière condensation": 1,
    "PAC": 2,
    "Radiateurs électriques": 3
}
spec0_chauffage = spec0_mapping[spec0_chauffage_label]
# Ajout spec3_chauffage
spec3_chauffage_label = st.selectbox(
    "Système installé après rénovation",
    ["Aucun", "PAC air/eau", "PAC air/air", "Chaudière condensation", "Radiateurs électriques"]
)
spec3_mapping = {
    "Aucun": -999,
    "PAC air/eau": 22,
    "PAC air/air": 21,
    "Chaudière condensation": 12,
    "Radiateurs électriques": 3
}
spec3_chauffage = spec3_mapping[spec3_chauffage_label]

st.markdown('<div class="section-title">Isolation</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    iti_type = st.selectbox("Type d’isolant ITI", ["Non renseigné", "Laine de verre", "Isolant biosourcé", "Isolant synthétique", "Isolant mince"])
    iti_surface = st.selectbox("Part de murs isolés (ITI)", ["0–25 %", "25–50 %", "50–100 %"])
    iti_epaisseur = st.slider("Épaisseur ITI (cm)", min_value=0, max_value=50, value=20)
    iti_surface_m2 = st.number_input("Surface de mur à isoler ITI (m²)", min_value=0, max_value=500, value=0)
    toiture_type = st.selectbox("Type d’isolant toiture", ["Non renseigné", "Laine de verre", "Isolant biosourcé", "Isolant synthétique", "Isolant mince"])
    toiture_surface = st.selectbox("Part de surface isolée toiture", ["0–25 %", "25–50 %", "50–100 %"])
    toiture_epaisseur = st.slider("Épaisseur toiture (cm)", min_value=0, max_value=50, value=20)
    toiture_surface_m2 = st.number_input("Surface de toiture à isoler (m²)", min_value=0, max_value=500, value=0)
with col4:
    plancher_type = st.selectbox("Type d’isolant plancher", ["Non renseigné", "Laine de verre", "Isolant biosourcé", "Isolant synthétique", "Isolant mince"])
    plancher_surface = st.selectbox("Part de surface isolée plancher", ["0–25 %", "25–50 %", "50–100 %"])
    plancher_epaisseur = st.slider("Épaisseur plancher (cm)", min_value=0, max_value=50, value=20)
    plancher_surface_m2 = st.number_input("Surface de plancher à isoler (m²)", min_value=0, max_value=500, value=0)
    ite_type = st.selectbox("Type d’isolant extérieur", ["Non renseigné", "Laine de verre", "Isolant biosourcé", "Isolant synthétique", "Isolant mince"])
    ite_surface = st.selectbox("Part de surface isolée extérieure", ["0–25 %", "25–50 %", "50–100 %"])
    ite_epaisseur = st.slider("Épaisseur ITE (cm)", min_value=0, max_value=50, value=20)
    ite_surface_m2 = st.number_input("Surface de mur à isoler ITE (m²)", min_value=0, max_value=500, value=0)
    ouvertures_ratio = st.selectbox("Proportion des ouvertures rénovées", ["Aucune", "0–25%", "25–50%", "50–75%", "75–100%"])

# === MAPPINGS ===
def annee_to_anciennete(annee):
    if annee < 1948: return 1
    elif annee <= 1974: return 2
    elif annee <= 1981: return 3
    elif annee <= 1989: return 4
    elif annee <= 2000: return 5
    elif annee <= 2012: return 6
    else: return 7

def dpe_to_code(dpe):
    return {"Pas de DPE": 0, "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}.get(dpe, 5)

def chauffage_actuel_code(ch):
    return {"Gaz": 1, "Fioul": 2, "Électrique": 3, "Bois": 4, "Mixte": 5, "Autre": 6}[ch]

def age_chauffage_code(age):
    mapping = {
        "<10 ans": 1,
        "10–15 ans": 2,
        "15–20 ans": 3,
        ">20 ans": 4,
        "Rénové": 5,
        "Inconnu": 6
    }
    # Retourner une valeur neutre si l'âge est -999
    return mapping.get(age, -999)

def isolant_code(t):
    return {"Non renseigné": -999, "Laine de verre": 1, "Isolant biosourcé": 2, "Isolant synthétique": 3, "Isolant mince": 4}[t]

def surface_code(s):
    return {"0–25 %": 1, "25–50 %": 2, "50–100 %": 3}[s]

def ouvertures_code(o):
    return {"Aucune": 0, "0–25%": 0.25, "25–50%": 0.5, "50–75%": 0.75, "75–100%": 1}[o]

def region_to_binaire(r):
    regions = {
        "Île-de-France": "var_region_IDF", "Hauts-de-France": "var_region_Hauts_de_France",
        "Grand Est": "var_region_Grand_Est", "Normandie": "var_region_Normandie",
        "Bretagne": "var_region_Bretagne", "Pays de la Loire": "var_region_Pays_de_la_Loire",
        "Centre-Val de Loire": "var_region_Centre_Val", "Bourgogne-Franche-Comté": "var_region_Bourgogne_Franche_Compte",
        "Auvergne-Rhône-Alpes": "var_region_ARA", "Nouvelle-Aquitaine": "var_region_Nouvelle_Aquitaine",
        "Occitanie": "var_region_Occitanie", "PACA et Corse": "var_region_PACA_et_Corse"
    }
    binaires = {k: 0 for k in regions.values()}
    binaires[regions[r]] = 1
    return binaires

def travaux_to_actions(travaux_list):
    actions = {
        "action_chauffage": 0, "action_ventilation": 0, "action_ECS": 0, "action_isolation_combles": 0,
        "action_isolation_ext": 0, "action_isolation_plancher": 0, "action_regulation_chauffage": 0,
        "action_ouvertures": 0, "action_isolation_toiture": 0, "action_renovation_sans_isolation_toiture": 0,
        "action_isolation_int": 0
    }
    mapping = {
        "Isolation combles": "action_isolation_combles",
        "Isolation extérieure": "action_isolation_ext",
        "Isolation plancher": "action_isolation_plancher",
        "Chauffage": "action_chauffage",
        "Ventilation": "action_ventilation",
        "Eau chaude": "action_ECS",
        "Ouvertures": "action_ouvertures",
        "Régulation chauffage": "action_regulation_chauffage",
        "Toiture": "action_isolation_toiture",
        "Rénovation sans isolation toiture": "action_renovation_sans_isolation_toiture",
        "Isolation intérieure": "action_isolation_int"
    }
    for t in travaux_list:
        if t in mapping:
            actions[mapping[t]] = 1
    return actions

# === MAPPING POUR LE CHAUFFAGE ===
chauffage_mapping = {
    "Gaz": "Chaudière gaz condensation",
    "Fioul": "Chaudière biomasse",
    "Électrique": "Radiateurs électriques",
    "Bois": "Chaudière biomasse",
    "Mixte": "PAC air/eau",
    "Autre": "PAC air/air"
}

# === FONCTION DE CALCUL DU COÛT TOTAL ===
def calcul_cout_total_intelligent(surface, travaux,
                                  iti_surface_m2, iti_epaisseur,
                                  toiture_surface_m2, toiture_epaisseur,
                                  plancher_surface_m2, plancher_epaisseur,
                                  ite_surface_m2, ite_epaisseur,
                                  chauffage_nouveau, ecs_type, ventilation_type, ouvertures_ratio,
                                  csv_isolation="cout_isolation.csv",
                                  csv_chauffage="cout_chauffage.csv",
                                  csv_ecs="cout_ecs.csv",
                                  csv_ventilation="cout_ventilation.csv",
                                  csv_menuiseries="cout_menuiseries.csv"):
    """
    Calcule le coût total des travaux en utilisant uniquement les données pertinentes pour chaque poste.
    """
    total = 0
    details = {}

    # Exemple d'utilisation du mapping
    chauffage_nouveau_mapped = chauffage_mapping.get(chauffage_nouveau, chauffage_nouveau)

    # Chargement des données d'isolation
    df_iso = pd.read_csv(csv_isolation)

    # 1. Isolation combles
    if "Isolation combles" in travaux and toiture_surface_m2 > 0:
        prix_unit = df_iso.loc[
            (df_iso['type_isolation'].str.lower() == "combles") &
            (df_iso['epaisseur_min'] <= toiture_epaisseur) &
            (df_iso['epaisseur_max'] >= toiture_epaisseur),
            'prix_m2'
        ].values[0]
        cout = prix_unit * toiture_surface_m2
        details["Isolation combles"] = cout
        total += cout

    # 2. Isolation intérieure (ITI)
    if "Isolation intérieure" in travaux and iti_surface_m2 > 0:
        prix_unit = df_iso.loc[
            (df_iso['type_isolation'].str.lower() == "iti") &
            (df_iso['epaisseur_min'] <= iti_epaisseur) &
            (df_iso['epaisseur_max'] >= iti_epaisseur),
            'prix_m2'
        ].values[0]
        cout = prix_unit * iti_surface_m2
        details["Isolation ITI"] = cout
        total += cout

    # 3. Isolation extérieure (ITE)
    if "Isolation extérieure" in travaux and ite_surface_m2 > 0:
        prix_unit = df_iso.loc[
            (df_iso['type_isolation'].str.lower() == "ite") &
            (df_iso['epaisseur_min'] <= ite_epaisseur) &
            (df_iso['epaisseur_max'] >= ite_epaisseur),
            'prix_m2'
        ].values[0]
        cout = prix_unit * ite_surface_m2
        details["Isolation ITE"] = cout
        total += cout

    # 4. Isolation plancher
    if "Isolation plancher" in travaux and plancher_surface_m2 > 0:
        prix_unit = df_iso.loc[
            (df_iso['type_isolation'].str.lower() == "plancher sol") &
            (df_iso['epaisseur_min'] <= plancher_epaisseur) &
            (df_iso['epaisseur_max'] >= plancher_epaisseur),
            'prix_m2'
        ].values[0]
        cout = prix_unit * plancher_surface_m2
        details["Isolation plancher"] = cout
        total += cout

    # 5. Chauffage (nouveau système)
    if "Chauffage" in travaux and chauffage_nouveau != "Aucun":
        df_chauf = pd.read_csv(csv_chauffage)
        # Mapper le type de chauffage sélectionné à la valeur du fichier CSV
        chauffage_nouveau_mapped = chauffage_mapping.get(chauffage_nouveau, chauffage_nouveau)
        
        if chauffage_nouveau_mapped == "Radiateurs électriques":
            # Cas spécifique pour les radiateurs électriques
            cout = 567.60 * (surface / 10)
            details["Chauffage (Radiateurs électriques)"] = cout  # Ajouter aux détails
            total += cout  # Ajouter au total

        else:
            # Filtrer les données en fonction du type de chauffage et de la surface
            filtre = (df_chauf['type_chauffage'] == chauffage_nouveau_mapped) & \
                     (df_chauf['surface_min'] <= surface) & \
                     (df_chauf['surface_max'] >= surface)
            if not filtre.any():
                st.warning(f"⚠️ Aucun prix trouvé pour le type de chauffage : {chauffage_nouveau_mapped} avec surface {surface} m²")
            else:
                cout = df_chauf.loc[filtre, 'prix'].values[0]
                details["Chauffage"] = cout
                total += cout

    # 6. Eau Chaude Sanitaire (ECS)
    if "Eau chaude" in travaux and ecs_type != "Aucun":
        df_ecs = pd.read_csv(csv_ecs)
        capacite = 100 if surface < 100 else 200
        cout = df_ecs.loc[
            (df_ecs['type_ecs'] == ecs_type) & (df_ecs['capacite'] == capacite),
            'prix'
        ].values[0]
        details["ECS"] = cout
        total += cout

    # 7. Ventilation
    if "Ventilation" in travaux and ventilation_type != "Aucune":
        df_vent = pd.read_csv(csv_ventilation)
        cout = df_vent.loc[df_vent['type_ventilation'] == ventilation_type, 'prix'].values[0]
        details["Ventilation"] = cout
        total += cout

    # 8. Menuiseries
    if "Ouvertures" in travaux and ouvertures_ratio > 0:
        df_menu = pd.read_csv(csv_menuiseries)
        prix_unit = df_menu.loc[df_menu['type_menuiserie'] == 'Fenêtre', 'prix_unitaire'].values[0]
        surface_fenetres = surface * ouvertures_ratio
        nb_fenetres = surface_fenetres / 15
        cout = prix_unit * nb_fenetres
        details["Menuiseries"] = cout
        total += cout

    return total, details

# === PRÉDICTION DU GAIN ===

if st.button("✨ Estimer le gain"):
    # Préparation des paramètres pour la prédiction
    valeurs_principales = [
        surface,
        annee_to_anciennete(annee),
        dpe_to_code(dpe),
        *[travaux_to_actions(travaux)[k] for k in [
            "action_chauffage", "action_ventilation", "action_ECS", "action_isolation_combles",
            "action_isolation_ext", "action_isolation_plancher", "action_regulation_chauffage",
            "action_ouvertures", "action_isolation_toiture", "action_renovation_sans_isolation_toiture",
            "action_isolation_int"
        ]],
        spec0_chauffage,
        chauffage_actuel_code(chauffage_actuel),
        age_chauffage_code(age_chauffage),
        spec3_chauffage,
        1 if ventilation == "Simple flux" else -999,
        isolant_code(iti_type), surface_code(iti_surface), iti_epaisseur,
        isolant_code(toiture_type), surface_code(toiture_surface), toiture_epaisseur,
        isolant_code(plancher_type), surface_code(plancher_surface), plancher_epaisseur,
        isolant_code(ite_type), surface_code(ite_surface), ite_epaisseur,
        ouvertures_code(ouvertures_ratio),
        *[region_to_binaire(region)[k] for k in [
            "var_region_IDF", "var_region_Hauts_de_France", "var_region_Grand_Est", "var_region_Normandie",
            "var_region_Bretagne", "var_region_Pays_de_la_Loire", "var_region_Centre_Val",
            "var_region_Bourgogne_Franche_Compte", "var_region_ARA", "var_region_Nouvelle_Aquitaine",
            "var_region_Occitanie", "var_region_PACA_et_Corse"
        ]]
    ]

    # Afficher les données envoyées au modèle dans l'interface
    st.markdown("### Données envoyées au modèle")
    st.write(valeurs_principales)

    # Imprimer les données dans le terminal
    print("Données envoyées au modèle :", valeurs_principales)

    # Chargement du modèle et prédiction
    try:
        with open("modele_EF_v5.pkl", "rb") as f:
            modele = pickle.load(f)
        X = np.array(valeurs_principales, dtype=float).reshape(1, -1)
        prediction = modele.predict(X)
        gain_percent = abs(prediction[0] * 100)
        st.success(f"🌱 Gain estimé : {gain_percent:.2f} %")
    except Exception as e:
        st.error("Erreur lors de la prédiction du gain.")
        st.error(f"Détails de l'erreur : {e}")

# === CALCUL DU COÛT TOTAL ===

if st.button("💶 Calculer le coût total"):
    # Calcul du coût total
    total, details = calcul_cout_total_intelligent(
        surface=surface,
        travaux=travaux,
        iti_surface_m2=iti_surface_m2,
        iti_epaisseur=iti_epaisseur,
        toiture_surface_m2=toiture_surface_m2,
        toiture_epaisseur=toiture_epaisseur,
        plancher_surface_m2=plancher_surface_m2,
        plancher_epaisseur=plancher_epaisseur,
        ite_surface_m2=ite_surface_m2,
        ite_epaisseur=ite_epaisseur,
        chauffage_nouveau=chauffage_actuel,
        ecs_type=ecs_type,
        ventilation_type=ventilation,
        ouvertures_ratio=ouvertures_code(ouvertures_ratio)
    )

    # Afficher le coût total
    st.success(f"💶 Coût total estimé : {total:.2f} €")

    # Afficher les détails des calculs
    st.markdown("### Détails des coûts")
    for poste, cout in details.items():
        st.write(f"- {poste} : {cout:.2f} €")
# === FONCTION POUR GÉNÉRER LES DONNÉES DU MODÈLE ===
def generer_donnees_modele(surface, annee, dpe, travaux, chauffage_actuel, age_chauffage, ventilation, ecs_type,
                           spec0_chauffage, spec3_chauffage, iti_type, iti_surface, iti_epaisseur,
                           toiture_type, toiture_surface, toiture_epaisseur,
                           plancher_type, plancher_surface, plancher_epaisseur,
                           ite_type, ite_surface, ite_epaisseur, ouvertures_ratio, region):
    """
    Génère les données à envoyer au modèle pour le calcul du gain.
    Neutralise les paramètres des travaux absents pour garantir la cohérence des données.
    """
    actions = travaux_to_actions(travaux)

    # Neutraliser les paramètres des travaux absents
    if not actions["action_isolation_int"]:
        iti_type, iti_surface, iti_epaisseur = "Non renseigné", "0–25 %", 0
    if not actions["action_isolation_toiture"] and not actions["action_isolation_combles"]:
        toiture_type, toiture_surface, toiture_epaisseur = "Non renseigné", "0–25 %", 0
    if not actions["action_isolation_plancher"]:
        plancher_type, plancher_surface, plancher_epaisseur = "Non renseigné", "0–25 %", 0
    if not actions["action_isolation_ext"]:
        ite_type, ite_surface, ite_epaisseur = "Non renseigné", "0–25 %", 0
    if not actions["action_chauffage"]:
        spec0_chauffage, spec3_chauffage = -999, -999
        age_chauffage = -999  # Neutraliser l'âge du chauffage si "Chauffage" n'est pas sélectionné
    if not actions["action_ECS"]:
        ecs_type = "Aucun"
    if not actions["action_ventilation"]:
        ventilation = "Aucune"
    if not actions["action_ouvertures"]:
        ouvertures_ratio = "Aucune"

    return [
        surface,
        annee_to_anciennete(annee),
        dpe_to_code(dpe),
        *[actions[k] for k in [
            "action_chauffage", "action_ventilation", "action_ECS", "action_isolation_combles",
            "action_isolation_ext", "action_isolation_plancher", "action_regulation_chauffage",
            "action_ouvertures", "action_isolation_toiture", "action_renovation_sans_isolation_toiture",
            "action_isolation_int"
        ]],
        spec0_chauffage,
        chauffage_actuel_code(chauffage_actuel),
        age_chauffage_code(age_chauffage),  # L'âge du chauffage est neutralisé si nécessaire
        spec3_chauffage,
        1 if ventilation == "Simple flux" else -999,
        isolant_code(iti_type), surface_code(iti_surface), iti_epaisseur,
        isolant_code(toiture_type), surface_code(toiture_surface), toiture_epaisseur,
        isolant_code(plancher_type), surface_code(plancher_surface), plancher_epaisseur,
        isolant_code(ite_type), surface_code(ite_surface), ite_epaisseur,
        ouvertures_code(ouvertures_ratio),
        *[region_to_binaire(region)[k] for k in [
            "var_region_IDF", "var_region_Hauts_de_France", "var_region_Grand_Est", "var_region_Normandie",
            "var_region_Bretagne", "var_region_Pays_de_la_Loire", "var_region_Centre_Val",
            "var_region_Bourgogne_Franche_Compte", "var_region_ARA", "var_region_Nouvelle_Aquitaine",
            "var_region_Occitanie", "var_region_PACA_et_Corse"
        ]]
    ]
# === CALCUL DES COÛTS ET GAINS INDIVIDUELS ET DES COMBINAISONS ===

if st.button("📊 Calculer les coûts et les gains individuels et les combinaisons"):
    resultats_individuels = []
    resultats_combinations = []
    details_complet = []

    # 1. Calcul des coûts et gains pour chaque travail individuel
    for travail in travaux:
        total, details = calcul_cout_total_intelligent(
            surface=surface,
            travaux=[travail],  # Un seul travail à la fois
            iti_surface_m2=iti_surface_m2,
            iti_epaisseur=iti_epaisseur,
            toiture_surface_m2=toiture_surface_m2,
            toiture_epaisseur=toiture_epaisseur,
            plancher_surface_m2=plancher_surface_m2,
            plancher_epaisseur=plancher_epaisseur,
            ite_surface_m2=ite_surface_m2,
            ite_epaisseur=ite_epaisseur,
            chauffage_nouveau=chauffage_actuel,
            ecs_type=ecs_type,
            ventilation_type=ventilation,
            ouvertures_ratio=ouvertures_code(ouvertures_ratio)
        )

        # Générer les données pour le modèle
        valeurs_principales = generer_donnees_modele(
            surface, annee, dpe, [travail], chauffage_actuel, age_chauffage, ventilation, ecs_type,
            spec0_chauffage, spec3_chauffage, iti_type, iti_surface, iti_epaisseur,
            toiture_type, toiture_surface, toiture_epaisseur,
            plancher_type, plancher_surface, plancher_epaisseur,
            ite_type, ite_surface, ite_epaisseur, ouvertures_ratio, region
        )

        # Prédiction du gain pour le travail individuel
        try:
            with open("modele_EF_v5.pkl", "rb") as f:
                modele = pickle.load(f)
            X = np.array(valeurs_principales, dtype=float).reshape(1, -1)
            prediction = modele.predict(X)
            gain_percent = abs(prediction[0] * 100)
        except Exception as e:
            gain_percent = None

        resultats_individuels.append({"Travail": travail, "Coût (€)": total, "Gain (%)": gain_percent})
        details_complet.append({"Travail": travail, "Détails": details})

    # 2. Calcul des coûts et gains pour toutes les combinaisons possibles
    for r in range(1, len(travaux) + 1):
        for combo in itertools.combinations(travaux, r):
            total, details = calcul_cout_total_intelligent(
                surface=surface,
                travaux=combo,
                iti_surface_m2=iti_surface_m2,
                iti_epaisseur=iti_epaisseur,
                toiture_surface_m2=toiture_surface_m2,
                toiture_epaisseur=toiture_epaisseur,
                plancher_surface_m2=plancher_surface_m2,
                plancher_epaisseur=plancher_epaisseur,
                ite_surface_m2=ite_surface_m2,
                ite_epaisseur=ite_epaisseur,
                chauffage_nouveau=chauffage_actuel,
                ecs_type=ecs_type,
                ventilation_type=ventilation,
                ouvertures_ratio=ouvertures_code(ouvertures_ratio)
            )

            # Générer les données pour le modèle
            valeurs_principales = generer_donnees_modele(
                surface, annee, dpe, combo, chauffage_actuel, age_chauffage, ventilation, ecs_type,
                spec0_chauffage, spec3_chauffage, iti_type, iti_surface, iti_epaisseur,
                toiture_type, toiture_surface, toiture_epaisseur,
                plancher_type, plancher_surface, plancher_epaisseur,
                ite_type, ite_surface, ite_epaisseur, ouvertures_ratio, region
            )

            # Prédiction du gain pour la combinaison
            try:
                with open("modele_EF_v5.pkl", "rb") as f:
                    modele = pickle.load(f)
                X = np.array(valeurs_principales, dtype=float).reshape(1, -1)
                prediction = modele.predict(X)
                gain_percent = abs(prediction[0] * 100)
            except Exception as e:
                gain_percent = None

            resultats_combinations.append({"Travaux": " + ".join(combo), "Coût (€)": total, "Gain (%)": gain_percent})

    # Afficher les résultats individuels
    st.markdown("### Résultats individuels")
    df_individuels = pd.DataFrame(resultats_individuels)
    st.dataframe(df_individuels)

    # Afficher les résultats des combinaisons
    st.markdown("### Résultats des combinaisons")
    df_combinations = pd.DataFrame(resultats_combinations)
    st.dataframe(df_combinations)

    # Graphique des combinaisons
    st.markdown("### Graphique des combinaisons")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Ajouter les points au graphique
    ax.scatter(df_combinations["Coût (€)"], df_combinations["Gain (%)"], color="blue", label="Combinaisons")



    # Ajouter des annotations pour chaque point
    for i, row in df_combinations.iterrows():
        ax.annotate(
            row["Travaux"],  # Texte de l'annotation (nom des travaux)
            (row["Coût (€)"], row["Gain (%)"]),  # Position du point
            textcoords="offset points",  # Décalage du texte par rapport au point
            xytext=(5, 5),  # Décalage en pixels (x, y)
            ha="left",  # Alignement horizontal
            fontsize=8,  # Taille de la police
            color="black"  # Couleur du texte
        )

    # Configurer les axes et le titre
    ax.set_xlabel("Coût (€)")
    ax.set_ylabel("Gain (%)")
    ax.set_title("Comparaison des combinaisons de travaux")
    st.pyplot(fig)

if st.button("🔧 Tester avec tous les inputs à 0"):
    # Exemple avec tous les inputs à 0
    surface = 0
    annee = 0
    dpe = "Pas de DPE"
    travaux = []
    chauffage_actuel = "Gaz"
    age_chauffage = "<10 ans"
    ventilation = "Aucune"
    ecs_type = "Aucun"
    spec0_chauffage = -999
    spec3_chauffage = -999
    iti_surface_m2 = 0
    iti_epaisseur = 0
    toiture_surface_m2 = 0
    toiture_epaisseur = 0
    plancher_surface_m2 = 0
    plancher_epaisseur = 0
    ite_surface_m2 = 0
    ite_epaisseur = 0
    ouvertures_ratio = 0

    valeurs_principales = [
        surface,
        annee_to_anciennete(annee),
        dpe_to_code(dpe),
        *[travaux_to_actions(travaux)[k] for k in [
            "action_chauffage", "action_ventilation", "action_ECS", "action_isolation_combles",
            "action_isolation_ext", "action_isolation_plancher", "action_regulation_chauffage",
            "action_ouvertures", "action_isolation_toiture", "action_renovation_sans_isolation_toiture",
            "action_isolation_int"
        ]],
        spec0_chauffage,
        chauffage_actuel_code(chauffage_actuel),
        age_chauffage_code(age_chauffage),
        spec3_chauffage,
        1 if ventilation == "Simple flux" else -999,
        isolant_code("Non renseigné"), surface_code("0–25 %"), 0,
        isolant_code("Non renseigné"), surface_code("0–25 %"), 0,
        isolant_code("Non renseigné"), surface_code("0–25 %"), 0,
        isolant_code("Non renseigné"), surface_code("0–25 %"), 0,
        0,
        *[region_to_binaire("Île-de-France")[k] for k in [
            "var_region_IDF", "var_region_Hauts_de_France", "var_region_Grand_Est", "var_region_Normandie",
            "var_region_Bretagne", "var_region_Pays_de_la_Loire", "var_region_Centre_Val",
            "var_region_Bourgogne_Franche_Compte", "var_region_ARA", "var_region_Nouvelle_Aquitaine",
            "var_region_Occitanie", "var_region_PACA_et_Corse"
        ]]
    ]

    # Imprimer les données dans le terminal
    print("Exemple avec tous les inputs à 0 :", valeurs_principales)

