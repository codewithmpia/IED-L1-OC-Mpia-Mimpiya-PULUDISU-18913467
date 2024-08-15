import streamlit as st
import requests
from datetime import datetime

# Charger les premières 1 million de décimales de PI
pi_decimals = requests.get("https://raw.githubusercontent.com/aismail/first-1MM-digits-of-pi/master/pi-million.txt").text

# Consigne 1: Recherche de la date de naissance dans les décimales de PI
st.title("Recherche de Date de Naissance dans les Décimales de PI")
birth_date = st.text_input("Entrez votre date de naissance (format: JJMM)")

if birth_date:
    position = pi_decimals.find(birth_date)
    if position != -1:
        st.write(f"Votre date de naissance apparaît à la position {position} dans les décimales de PI.")
    else:
        st.write("Votre date de naissance n'apparaît pas dans les premières 1 million de décimales de PI.")

# Consigne 2: Afficher le jour de naissance correspondant
if birth_date:
    try:
        day_of_birth = datetime.strptime(birth_date, "%d%m").strftime("%A")
        st.write(f"Le jour de la semaine correspondant à votre date de naissance est : {day_of_birth}")
    except ValueError:
        st.write("Format de date invalide. Veuillez entrer la date au format JJMM.")

# Consigne 3: Calcul des sommes des décimales de PI
st.title("Calcul des Sommes des Décimales de PI")

# Filtrer les caractères non numériques
pi_digits = [digit for digit in pi_decimals if digit.isdigit()]
pi_first_20 = [int(digit) for digit in pi_digits[:20]]
pi_first_144 = [int(digit) for digit in pi_digits[:144]]
sum_first_20 = sum(pi_first_20)
sum_first_144 = sum(pi_first_144)

st.write(f"La somme des 20 premières décimales de PI est : {sum_first_20}")
st.write(f"La somme des 144 premières décimales de PI est : {sum_first_144}")

# Consigne 4: Insérer une vidéo
st.title("Vidéo : La somme de tous les nombres entiers naturels est égale à -1/12")
st.video("https://www.youtube.com/watch?v=w-I6XTVZXww")
