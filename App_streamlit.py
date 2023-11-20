
#-----------------------------------------------------#
#                      Imports                        #
#-----------------------------------------------------#

import streamlit as st                                  # Neccessaire pour utilier Streamlit
import pandas as pd                                     # Manipulation des bases de données
from PIL import Image                                   # Affichage des 2 logos
import folium                                           # Afficher le choix de carte Folium
from streamlit_folium import folium_static              # Style de carte (static)
import geopandas as gpd                                 # Traiter les données Géospatial
from babel.dates import format_date                     # Formater les dates
from streamlit_option_menu import option_menu           # Affichage du style des boutons dans la barre latéral
from folium.plugins import Draw                         # Widgets draw (dessin) sur carte en page Bus • Tram • BatCub
import random                                           # Affichage aléatoire des funfacts pendant le temps de chargement de carte 
from dotenv import load_dotenv                          # Masquer l'API utilisé
import os                                               # Appeler l'API securisé
import streamlit.components.v1 as components            # Utiliser pour le scroll up automatique (utilisé dans fonction)
# from folium.plugins import MarkerCluster              # Sera utilisé plus tard pour les stations

#-----------------------------------------------------#
#                   Page Configuration                #
#-----------------------------------------------------#

# Configuration de base de la page Streamlit
st.set_page_config(
    page_title="TBM : un diaporama du réseau",
    page_icon="🚲🚌🚃⛴️",
    layout="wide",
)

#-----------------------------------------------------#
#                   Global Variables                  #
#-----------------------------------------------------#

# Recolte de la map souhaité (pour la page Bus • Tram •BatCub)
load_dotenv()                                                                                   # Securisation de l'API
map_api_key = os.getenv("maptiler_api_key")                                                     # Appel de la cle API securisé  
new_tile = f"https://api.maptiler.com/maps/dataviz/{{z}}/{{x}}/{{y}}.png?key={map_api_key}"     # Url de ma map
#new_tile = "https://api.maptiler.com/maps/openstreetmap/{z}/{x}/{y}.jpg?key={map_api_key}"     # 2ème choix de map

# Chargement du logo
logo_path = './Images/LOGO_TBM.png'
logo = Image.open(logo_path)

#-----------------------------------------------------#
#                     Functions                       #
#-----------------------------------------------------#

# Fonction pour charger les fun facts à partir du fichier .txt (Temps d'attente / U.X)
def load_facts(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            facts = file.read().splitlines()
        return facts
    except FileNotFoundError:
        st.error("Fait amusant non disponible...")
        return []

# Chargement des données Bus, Tram et BatCub depuis le fichier GeoJSON
@st.cache_data(show_spinner=False)
def load_data_and_create_geodataframe():
    """Load data and create a GeoDataFrame"""
    gdf = gpd.read_file('./Data/gdfbustrambat.json')
    return gdf


# Chargement des données VCube et formatage date / heure
@st.cache_data(show_spinner=False)
def load_v3_data():
    """Load V3 data"""
    # Loading data from CSV, converting 'mdate' to datetime and formatting the date and time
    data = pd.read_csv("./Data/stations_VCube.csv")
    data['mdate'] = pd.to_datetime(data['mdate'])
    data['time'] = data['mdate'].dt.strftime('%H:%M')
    data['formatted_date'] = data['mdate'].apply(lambda x: format_date(x, 'EEEE d MMMM y', locale='fr'))
    return data

# Création de la carte pour la 2ème presentation
def create_v3_map(filtered_data, selected_tile):
    """Create V3 map"""
    # Creating a folium map with specified location, zoom and tile style
    m = folium.Map(
        location=[44.8378, -0.5792],
        zoom_start=13,
        tiles=selected_tile,
        attr='Map data © OpenStreetMap contributors'
    )
    # Iteration à travers les données filtré et ajout des marqueur de cercle sur la carte
    for index, row in filtered_data.iterrows():

        # Extraction des informations pertinente
        nom = row['nom']  # Nom de station
        nbvelos = row['nbvelos']  # Nombre de VCub disponible
        latitude = row['latitude']  # Latitude de la station
        longitude = row['longitude']  # Longitude dela station
        etat = row['etat']  # Status de la station 
        nbelec = row['nbelec']  # Nombre de VCub electrique
        nbclassiq = row['nbclassiq']  # Nombre de VCub classique
        nbplaces = row['nbplaces']  # Nombre de place disponible

        # Determiner la couleur basé en fonction du status de la station
        if etat == 'CONNECTEE':
            color = '#E37222'
        elif etat == 'MAINTENANCE':
            color = '#0A8A9F'
        elif etat == 'DECONNECTEE':
            color = 'red'

        # Determiner la grosseur du rayon de cercle basé sur le nombre de VCub disponible
        radius = nbvelos * 1.5

        # Affichage de la carte jour / nuit en fonction de l'heure choisis
        fill = True if selected_tile in ['Stamen Toner', 'OpenStreetMap'] else False
        fill_color = color if fill else None

        # Creatiion du text des Popups
        popup_text = f"""
        <div style="font-size:12px">
        <h4 style="color:{color};margin-bottom:0">{nom}</h4>
        <p style="margin-bottom:0"><b>État:</b> {etat}</p>
        <p style="margin-bottom:0"><b>Places disponible:</b> {nbplaces}</p>
        <p style="margin-bottom:0"><b>Vélos disponible:</b> {nbvelos}</p>
        <p style="margin-bottom:0"><b>Vélos électriques:</b> {nbelec}</p>
        <p style="margin-bottom:0"><b>Vélos classiques:</b> {nbclassiq}</p>
        </div>
        """
        popup = folium.Popup(popup_text, max_width=250)  # Creating a popup with the text

        # Creation des marqueurs et ajout à la carte
        marker = folium.CircleMarker(
            location=[latitude, longitude], 
            color=color, 
            fill=fill, 
            fill_color=fill_color,
            radius=radius,
            weight=1,
            popup=popup  # Adding the popup to the marker
        )
        marker.add_to(m)  # Adding the marker to the map

    return m  # Returning the map object

# Fonctions pour la description de la page 3
def render_page_3_description():
    return """
        <div style="text-align: justify; background-color: #f5f5f5; padding: 20px; border-radius: 10px; border: 2px solid #000;">
            <h2 style="text-align: center;">Bus • Tram • BatCub</h2>
            <p>Dans la continuité des 14 jours de données que nous avons explorés, découvrez maintenant les lignes de Bus, Tram et BatCub de la métropole bordelaise. 
                Chaque véhicule est associé à une couleur distincte pour les identifier facilement sur la carte. 
                En changeant de couche, vous avez la possibilité de sélectionner quel type de véhicule vous souhaitez afficher. 
                De plus, vous pouvez desactiver / activer la visualisation des lignes en retard, qui apparaissent en rouge pour une identification rapide.</p>
        </div>
    """
# Pour créer les lignes et leur couleur en fonction du vehicule
def add_geojson_to_layer(row, layer, line_color, line_weight):
    geojson_obj = folium.GeoJson(
        row['geometry'], 
        style_function=lambda x, color=line_color: {'color': color, 'weight': line_weight},
        popup=folium.Popup(create_popup_text(row))
    )
    geojson_obj.add_to(layer)

# Pour la page Bus Tram BatCub
def create_popup_text(row, line_emoji, line_color):
    retard_moyen_minutes = row['retard'] / 60
    return f"""
    <div style="font-size:12px; padding:10px; background-color: #F8F9F9; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.25); min-width: 300px;">
        <h4 style="color:{line_color};margin-bottom:10px">{row['ligne_com']}</h4>
        <p style="margin-bottom:5px"><b>Terminus:</b> {row['libelle']}</p>
        <p style="margin-bottom:5px"><b>Vehicule:</b> {line_emoji} {row['vehicule']}</p>
        <p style="margin-bottom:5px"><b>Retard Moyen:</b> {retard_moyen_minutes:.2f} minutes</p>
        <p style="margin-bottom:5px"><b>Vitesse Moyenne (km/h):</b> {row['vitesse']}</p>
        <p style="margin-bottom:5px"><b>Nombre de véhicule/ligne:</b> {row['nb_vehicule']}</p>
    </div>
    """
# Titre de presentation Rapport d'analyse VCub
def render_powerbi_info():
    return """
    <div style="margin-top: 20px; text-align: center; background-color: #f5f5f5; padding: 20px; border-radius: 10px; border: 2px solid #000;">
        <h2>Rapport d'analyse VCub</h2>
        <p>Pour visualiser ce rapport, veuillez vous connecter à un compte Power BI</p>
    </div>
    """
# Affichage du rapport VCub
def render_powerbi_report_vcub():
    return """
    <div style="width: 1000px; height: 650px; overflow: hidden; position: relative;">
        <iframe 
            title="V3" 
            width="980" 
            height="600" 
            src="https://app.powerbi.com/reportEmbed?reportId=a5a6fa02-137c-48ca-9754-8467b7366089&autoAuth=true&ctid=5892e2db-e39d-4cc1-a179-dc66550efc30" 
            frameborder="0" 
            allowfullscreen
            style="position: absolute;">
        </iframe>
    </div>
    """

# Titre de presentation Rapport d'analyse Bus • Tram • BatCub
def render_powerbi_info_2():
    return """
    <div style="margin-top: 20px; text-align: center; background-color: #f5f5f5; padding: 20px; border-radius: 10px; border: 2px solid #000;">
        <h2>Rapport d'analyse Bus • Tram • BatCub</h2>
        <p>Pour visualiser ce rapport, veuillez vous connecter à un compte Power BI</p>
    </div>
    """

# Affichage du raport Bus • Tram • BatCub
def render_powerbi_iframe():
    return """
    <div style="width: 1000px; height: 1200px; overflow: hidden; position: relative;">
        <iframe 
            title="TRAM • BUS • BATEAU" 
            width="945" 
            height="2000" 
            src="https://app.powerbi.com/reportEmbed?reportId=7f601950-66d2-4060-840b-21740784a6dc&autoAuth=true&ctid=5892e2db-e39d-4cc1-a179-dc66550efc30" 
            frameborder="0" 
            allowfullscreen
            style="position: absolute;">
        </iframe>
    </div>
    """

# Fonction pour remonter en haut de page (Applicable sur une seul page malheureusement)
def scroll_to_top():
    components.html(
        """
        <script>
        const anchor = document.createElement('a');
        anchor.setAttribute('href', '#');
        anchor.click();
        </script>
        """,
        height=0
    )
#-----------------------------------------------------#
#                       Sidebar                       #
#-----------------------------------------------------#

# Création de la barre latérale avec options de navigation
with st.sidebar:
    st.image(logo, use_column_width=True)
    selected = option_menu(None, ['HOME', 'VCub', 'Bus • Tram • BatCub'],
                           icons=['house', 'bicycle', 'geo-alt'], 
                           menu_icon="cast", default_index=0)
   
#-----------------------------------------------------#
#                    Pages HOME                       #
#-----------------------------------------------------#

# Page d'accueil
if selected == 'HOME':
    # Chargement du logo
    image = Image.open('./Images/Logo_live_sync.png')

    # Créer 3 colonnes invisible pour centrer le logo en utilisant celle du milieu
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.image(image, use_column_width=True)

#-----------------------------------------------------#
#                    Pages VCub                       #
#-----------------------------------------------------#

# Page VCub
elif selected == 'VCub':

    # Présentation de la visualisation des besoins en vélos VCub (justifié)
    st.markdown("""
    <div style="text-align: justify; background-color: #f5f5f5; padding: 20px; border-radius: 10px; border: 2px solid #000;">
        <h2 style="text-align: center;">Visualisation en temps réel des besoins en vélos VCub</h2>
        <p>Cette carte offre une visualisation en temps réel des besoins en vélos classiques et électriques VCub. Les données sont collectées en temps réel à différents intervalles en fonction des jeux de données disponibles, puis affichées en temps réel sur la carte.</p>
        <p>La taille du cercle représente la disponibilité des vélos : plus le cercle est grand, plus il y a de vélos disponibles, et plus il est petit, moins il y a de vélos disponibles. La couleur du cercle indique également l'état de la station.</p>
        <p>Pour une expérience plus immersive, placez le curseur à 4 minutes lors de la fête nationale du 14 juillet, entre 20 heures et 3 heures du matin, sur la place du Miroir d'Eau, lieu habituel pour admirer le feu d'artifice, où les stations connaissent un mouvement considérable.</p>
        <p>La collecte de données a été volontairement interrompue après 14 jours en raison de limitations matérielles.</p>
    </div>
    <div style="margin-bottom: 20px;"></div>
""", unsafe_allow_html=True)

    # Ouverture du fichier video
    video_file = open('./Video/VCub_video.mp4', 'rb')

    # Reglage du codec
    video_bytes = video_file.read()

    # Affichage de la vidéo
    st.video(video_bytes)


    # Ligne horizontale pour marquer la transition
    st.markdown("---")

    # Ajout d'un espace 
    st.markdown("""<div style="margin-bottom: 20px;"></div>""", unsafe_allow_html=True)

    # Présentation de la deuxième démonstration
    st.markdown("""
    <div style="text-align: justify; background-color: #f5f5f5; padding: 20px; border-radius: 10px; border: 2px solid #000;">
        <h2 style="text-align: center;">Exploration des données VCub</h2>
        <p>Dans cette démonstration, vous avez la possibilité de choisir parmi les 14 jours de données sur l'utilisation des vélos classiques et électriques VCub dans la métropole bordelaise.</p>
        <p>Sélectionnez une date et une heure pour afficher la disponibilité des vélos sur la carte interactive.</p>
        <p>En cliquant sur une station (extrémité du cercle), vous pouvez obtenir des détails sur le nombre de vélos disponibles, ainsi que le nombre de places que peut accueillir la station.</p>
        <p>Explorez les variations de la demande VCub au fil du temps !</p>
    </div>
""", unsafe_allow_html=True)
    
    # Ajout d'un espace 
    st.markdown("""<div style="margin-bottom: 20px;"></div>""", unsafe_allow_html=True)

    # Témoin de chargement
    with st.spinner('Chargement de la carte ...'):

        # Chargement des données VCub
        data = load_v3_data()
        # Ajout d'un espace 
        st.markdown("""<div style="margin-bottom: 20px;"></div>""", unsafe_allow_html=True)

        # Formatage des dates présentes
        date_format_mapping = pd.Series(data.formatted_date.values,index=data.mdate.dt.date).to_dict()

        # Rangement dans l'ordre des dates formaté unique 
        unique_dates = sorted(date_format_mapping.items())[1:]

        # Liste déroulante pour des dates formaté
        selected_date = st.selectbox('Selectionnez une date :', 
                                     unique_dates, format_func=lambda x: x[1] if x != 'Selectionnez une date..' else x)

        # Rangement dans l'ordre des heures 
        unique_times = sorted(data['time'].unique())

        # Liste déroulante des heures uniques
        selected_time = st.selectbox('Selectionnez une heure :', options=unique_times)

        # Ajout d'un espace
        st.markdown("""<div style="margin-bottom: 20px;"></div>""", unsafe_allow_html=True)

        # Application de la carte jour ou nuit en fonction du lévé et coucher du soleil (Période réel)
        if '06:20' <= selected_time < '21:40':
            selected_tile = new_tile
        else:
            selected_tile = 'CartoDB dark_matter'

        # Filtrage des données en fonction de la date et de l'heure sélectionnées et création d'une carte
        filtered_data = (
            data[(data['mdate'].dt.date == selected_date[0]) & (data['time'] == selected_time)] 
            if selected_date != 'Selectionnez une date..' else pd.DataFrame()
        )

        # Création de la carte interactive VCub
        m = create_v3_map(filtered_data, selected_tile)

        # Affichage de la carte interactive VCub
        folium_static(m, width=945, height=450)

        # Ligne de séparation de sujet
        st.markdown("---")

    #------------- Tableau de bord Power BI --------------#

        st.markdown(render_powerbi_info(), unsafe_allow_html=True)               # Texte d'information pour visualiser le rapport 
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # Ajout d'un espace
        st.markdown(render_powerbi_report_vcub(), unsafe_allow_html=True)        # Affichage du rapport d'analyse VCub
    
#-----------------------------------------------------#
#              Pages Bus • Tram • VCub                #
#-----------------------------------------------------#

# Début de la page "Bus • Tram • BatCub"
elif selected == 'Bus • Tram • BatCub':
    scroll_to_top()

    st.markdown(render_page_3_description(), unsafe_allow_html=True)

    # Espace pour la mise en page
    st.markdown("""<div style="height: 20px;"></div>""", unsafe_allow_html=True)

    # Charger les faits
    facts = load_facts("./facts.txt")

    # Conteneur temporaire pour le fait
    fact_container = st.empty()
    
    # Sélectionner un fait aléatoire
    random_fact = random.choice(facts) if facts else ''
    fact_container.markdown(f"""
        <div style="background-color:#f0f2f6; padding:10px; border-radius:10px;">
            <h4 style="color:#0078D4;"><i class="fas fa-lightbulb"></i>💡 Le saviez-vous ?</h4>
            <p>{random_fact}</p>
        </div>
        """, unsafe_allow_html=True)

    # Espace pour la mise en page
    st.markdown("""<div style="height: 20px;"></div>""", unsafe_allow_html=True)

    # Suite de la page "Bus • Tram • BatCub"
    with st.spinner('Chargement de la carte ...'):
        gdf = load_data_and_create_geodataframe()

        # Initialisation et ajout de la carte
        m = folium.Map((44.84101, -0.64265), tiles=None, zoom_start=12)
        folium.TileLayer(new_tile, attr='© MapTiler © OpenStreetMap contributors', name='Dataviz Map').add_to(m)
        
        # Initialisation des couches
        tram_layer = folium.FeatureGroup(name='🚊 Tram')
        bus_layer = folium.FeatureGroup(name='🚍 Bus')
        bateau_layer = folium.FeatureGroup(name='🚢 BatCub')
        delay_layer = folium.FeatureGroup(name='Lignes en retards')

        # Dictionnaire pour les couleurs des trajets effectués des véhicules
        vehicle_color_map = {
            'BUS': '#01b1eb',
            'TRAM': '#831f82',
            'BATEAU': '#2b9cbf'
        }

        # Mapping des types de véhicules à leurs couches respectives
        layer_dict = {
            'TRAM': tram_layer,
            'BUS': bus_layer,
            'BATEAU': bateau_layer
        }        

        # Dictionnaire pour les emojis des véhicules
        emoji_dict = {'Tram': '🚊', 'Bus': '🚍', 'BatCub': '🚢'}

        # Définition de l'épaisseur de ligne
        line_weight = 2  # Ajustez cette valeur pour l'épaisseur souhaitée

        # Seuil de retard (en secondes)
        retard_seuil = 100

        # Ajout des données GeoDataFrame à la carte dans leurs couches respectives
        for index, row in gdf.iterrows():
            line_color = vehicle_color_map.get(row['vehicule'], '#8dc63f')
            line_emoji = emoji_dict.get(row['vehicule'], '')
            popup_text = create_popup_text(row, line_emoji, line_color)

            # Création de l'objet GeoJSON pour chaque ligne
            geojson_obj = folium.GeoJson(
                row['geometry'], 
                style_function=lambda x, color=line_color: {'color': color, 'weight': line_weight},
                popup=folium.Popup(popup_text)
            )

            # Ajout à la couche correspondante
            if row['vehicule'] == 'BUS':
                geojson_obj.add_to(bus_layer)
            elif row['vehicule'] == 'TRAM':
                geojson_obj.add_to(tram_layer)
            elif row['vehicule'] == 'BATEAU':
                geojson_obj.add_to(bateau_layer)

            # Ajout à la couche des retards si le retard dépasse le seuil
            if row['retard'] > retard_seuil:
                geojson_obj_delay = folium.GeoJson(
                    row['geometry'], 
                    style_function=lambda x, color='red': {'color': color, 'weight': line_weight},
                    popup=folium.Popup(popup_text)
                )
                geojson_obj_delay.add_to(delay_layer)

        # Widgets pour dessiner sur la carte
        draw = Draw(
            export=True,
            filename='data.geojson',
            position='topleft',
            draw_options={
                'polyline': True,
                'polygon': True,
                'circle': True,
                'rectangle': True,
                'marker': True,
            },
            edit_options={'edit': True}
        )
        draw.add_to(m)

        # Ajouter les couches à la carte
        tram_layer.add_to(m)
        bus_layer.add_to(m)
        bateau_layer.add_to(m)
        delay_layer.add_to(m)
        folium.LayerControl().add_to(m)

        # Afficher la carte dans Streamlit
        folium_static(m, width=945, height=450)
        
        # Ajout d'un espace pour la mise en page
        st.markdown("""<div style="margin-bottom: 10px;"></div>""", unsafe_allow_html=True)

        # Ligne horizontale pour marquer la transition
        st.markdown("---")

        # Ajout d'un espace pour la mise en page
        st.markdown("""<div style="margin-bottom: 10px;"></div>""", unsafe_allow_html=True)

    # Effacer le fait après le chargement
    fact_container.empty()

    #------------- Tableau de bord Power BI --------------#

    st.markdown(render_powerbi_info_2(), unsafe_allow_html=True)               # Texte d'information pour visualiser le rapport              
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)   # Ajout d'un espace
    st.markdown(render_powerbi_iframe(), unsafe_allow_html=True)               # Affichage du rapport d'analyse VCub

