import streamlit as st
import re

# Configuration de la page
st.set_page_config(
    page_title="Universal YouTube Translator",
    page_icon="🌍",
    layout="wide"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main-title {
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 30px;
        text-align: center;
    }
    .section-title {
        font-size: 28px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .description {
        font-size: 18px;
        line-height: 1.6;
        text-align: justify;
    }
    .contact-info {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# En-tête
st.markdown('<h1 class="main-title">Universal YouTube Translator 🌍</h1>', unsafe_allow_html=True)

# Onglets
tab1, tab2, tab3 = st.tabs(["Traduction", "À propos", "Contact"])

with tab1:
    st.markdown('<h2 class="section-title">Traduisez vos vidéos YouTube</h2>', unsafe_allow_html=True)
    
    # Entrée de l'URL
    url = st.text_input("Entrez l'URL de la vidéo YouTube", placeholder="https://www.youtube.com/watch?v=...")
    
    # Sélection de la langue
    langues = ["Français", "English", "Español", "Deutsch", "中文", "日本語"]
    langue_cible = st.selectbox("Choisissez la langue de traduction", langues)
    
    # Bouton d'envoi
    if st.button("Traduire la vidéo", type="primary"):
        if url:
            if re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+', url):
                st.success("URL vidéo valide ! Traduction en cours...")
                # Ici viendra le code de traduction
            else:
                st.error("⚠️ URL non valide. Veuillez entrer une URL YouTube valide.")
        else:
            st.error("Veuillez entrer une URL")

with tab2:
    st.markdown('<h2 class="section-title">À propos du projet</h2>', unsafe_allow_html=True)
    st.markdown("""<div class="description">Nous sommes quatre étudiants en école d'ingénieur — trois de l'UTBM et un de l'UTC — actuellement en semestre à l'UTSEUS Shanghai.<br><br>
                Dans le cadre de l'UV ML01 (Machine Learning), nous avons développé Universal YouTube Translator : une application web qui permet d'obtenir le script traduit dans la langue de votre choix à partir de n'importe quelle vidéo YouTube.<br><br>
                Notre objectif : rendre les contenus YouTube accessibles à tous, quelle que soit la langue.</div>""", 
                unsafe_allow_html=True)

with tab3:
    st.markdown('<h2 class="section-title">Notre équipe</h2>', unsafe_allow_html=True)
    
    # Création de deux colonnes pour les contacts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### UTBM")
        st.write("- Gabin LAMBERT (gabin.lambert@utbm.fr)")
        st.write("- Camil MAILLARD (camil.maillard@utbm.fr)")
        st.write("- Noa FOUICH (noa.fouich@utbm.fr)")
    
    with col2:
        st.markdown("### UTC")
        st.write("- Théo PEREIRA (theo.pereira@utc.fr)")
    
    # Centrer le lien GitHub
    left, middle, right = st.columns([1, 2, 1])
    with middle:
        st.write("- GitHub : [Universal YouTube Translator](https://github.com/votre-repo)")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey;'>© 2025 Universal YouTube Translator - Projet ML01 UTSEUS</div>", 
    unsafe_allow_html=True
)
