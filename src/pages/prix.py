import streamlit as st
import pandas as pd

st.title("🛠 Modification des prix de base")

# Chargement des datasets
df_iso = pd.read_csv("cout_isolation.csv")
df_chauff = pd.read_csv("cout_chauffage.csv")
df_ecs = pd.read_csv("cout_ecs.csv")
df_vent = pd.read_csv("cout_ventilation.csv")
df_menu = pd.read_csv("cout_menuiseries.csv")

st.header("Isolation")
for i, row in df_iso.iterrows():
    new_prix = st.number_input(
        f"{row['type_isolation']} {row['epaisseur_min']}–{row['epaisseur_max']} cm (€/m²)",
        value=float(row['prix_m2']),
        key=f"iso_{i}"
    )
    df_iso.at[i, 'prix_m2'] = new_prix

st.header("Chauffage")
for i, row in df_chauff.iterrows():
    new_prix = st.number_input(
        f"{row['type_chauffage']} {row['modele']} ({row['surface_min']}-{row['surface_max']} m²)",
        value=float(row['prix']),
        key=f"chauff_{i}"
    )
    df_chauff.at[i, 'prix'] = new_prix

st.header("ECS")
for i, row in df_ecs.iterrows():
    new_prix = st.number_input(
        f"{row['type_ecs']} {row['capacite']}L",
        value=float(row['prix']),
        key=f"ecs_{i}"
    )
    df_ecs.at[i, 'prix'] = new_prix

st.header("Ventilation")
for i, row in df_vent.iterrows():
    new_prix = st.number_input(
        f"{row['type_ventilation']}",
        value=float(row['prix']),
        key=f"vent_{i}"
    )
    df_vent.at[i, 'prix'] = new_prix

st.header("Menuiseries")
for i, row in df_menu.iterrows():
    new_prix_unitaire = st.number_input(
        f"{row['type_menuiserie']} prix unitaire",
        value=float(row['prix_unitaire']),
        key=f"menu_u_{i}"
    )
    new_prix_pose = st.number_input(
        f"{row['type_menuiserie']} prix pose",
        value=float(row['prix_pose']),
        key=f"menu_p_{i}"
    )
    df_menu.at[i, 'prix_unitaire'] = new_prix_unitaire
    df_menu.at[i, 'prix_pose'] = new_prix_pose

if st.button("💾 Sauvegarder les nouveaux prix"):
    df_iso.to_csv("cout_isolation.csv", index=False)
    df_chauff.to_csv("cout_chauffage.csv", index=False)
    df_ecs.to_csv("cout_ecs.csv", index=False)
    df_vent.to_csv("cout_ventilation.csv", index=False)
    df_menu.to_csv("cout_menuiseries.csv", index=False)
    st.success("Les nouveaux prix ont été sauvegardés !")
