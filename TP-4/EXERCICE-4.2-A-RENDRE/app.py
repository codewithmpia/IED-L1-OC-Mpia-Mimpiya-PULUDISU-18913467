import streamlit as st
from PIL import Image
import piexif
import folium
from streamlit_folium import st_folium

# Charger l'image
uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Image téléchargée', use_column_width=True)

    # Vérifier si les métadonnées EXIF existent
    exif_dict = {}
    if "exif" in image.info:
        # Lire les métadonnées EXIF existantes
        exif_dict = piexif.load(image.info["exif"])
    else:
        st.warning("L'image ne contient pas de métadonnées EXIF. Ajout de métadonnées par défaut.")

    # Formulaire pour éditer les métadonnées EXIF
    st.write("Modifier les métadonnées EXIF")
    new_exif_data = {}
    for tag, value in exif_dict.get("0th", {}).items():
        tag_name = piexif.TAGS['0th'][tag]['name']
        # Convertir en chaîne pour éviter les erreurs
        new_value = st.text_input(f"{tag_name}:", str(value))
        try:
            # Convertir en entier pour les données EXIF numériques
            new_exif_data[tag] = int(new_value)  
        except ValueError:
            # Garder comme chaîne si non convertible en entier
            new_exif_data[tag] = new_value  

    # Formulaire pour les coordonnées GPS
    st.write("Modifier les coordonnées GPS")
    latitude = st.text_input("Latitude (format DD MM SS)", "48 50 29")
    longitude = st.text_input("Longitude (format DD MM SS)", "2 24 47")

    # Mettre à jour les métadonnées EXIF
    if st.button("Mettre à jour les métadonnées"):
        try:
            exif_dict["0th"].update(new_exif_data)
            if latitude and longitude:
                lat_deg, lat_min, lat_sec = map(int, latitude.split())
                lon_deg, lon_min, lon_sec = map(int, longitude.split())

                gps_ifd = {
                    piexif.GPSIFD.GPSLatitudeRef: "N" if lat_deg >= 0 else "S",
                    piexif.GPSIFD.GPSLatitude: ((abs(lat_deg), 1), (lat_min, 1), (lat_sec, 1)),
                    piexif.GPSIFD.GPSLongitudeRef: "E" if lon_deg >= 0 else "W",
                    piexif.GPSIFD.GPSLongitude: ((abs(lon_deg), 1), (lon_min, 1), (lon_sec, 1)),
                }
                exif_dict["GPS"] = gps_ifd

            exif_bytes = piexif.dump(exif_dict)
            image.save("edited_image.jpg", "jpeg", exif=exif_bytes)
            st.success("Les métadonnées ont été mises à jour avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour des métadonnées: {e}")

    # Afficher les coordonnées GPS sur une carte
    if "GPS" in exif_dict:
        gps_info = exif_dict["GPS"]
        if piexif.GPSIFD.GPSLatitude in gps_info and piexif.GPSIFD.GPSLongitude in gps_info:
            lat = gps_info[piexif.GPSIFD.GPSLatitude]
            lon = gps_info[piexif.GPSIFD.GPSLongitude]
            lat_ref = gps_info[piexif.GPSIFD.GPSLatitudeRef]
            lon_ref = gps_info[piexif.GPSIFD.GPSLongitudeRef]

            lat = lat[0][0] + lat[1][0] / 60 + lat[2][0] / 3600
            lon = lon[0][0] + lon[1][0] / 60 + lon[2][0] / 3600

            if lat_ref != "N":
                lat = -lat
            if lon_ref != "E":
                lon = -lon

            st.write(f"Latitude: {lat}, Longitude: {lon}")

            # Afficher la carte avec Folium
            map = folium.Map(location=[lat, lon], zoom_start=12)
            folium.Marker([lat, lon]).add_to(map)
            st_folium(map, width=700, height=500)
        else:
            st.warning("Les coordonnées GPS ne sont pas présentes dans les métadonnées.")
    else:
        st.warning("Les coordonnées GPS ne sont pas présentes dans les métadonnées.")

    # Afficher les POI(s) des voyages
    st.write("Afficher les POI(s) des voyages")
    pois = [
        {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "Tokyo", "lat": 35.6895, "lon": 139.6917},
        {"name": "Charenton-le-Pont", "lat": 48.8297, "lon": 2.4167},
        {"name": "Kinshasa", "lat": -4.4419, "lon": 15.2663},
        {"name": "Bruxelles", "lat": 50.8503, "lon": 4.3517},
    ]

    map_pois = folium.Map(location=[48.8566, 2.3522], zoom_start=2)
    for poi in pois:
        folium.Marker([poi['lat'], poi['lon']], popup=poi['name']).add_to(map_pois)
    st_folium(map_pois, width=700, height=500)
