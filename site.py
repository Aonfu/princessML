import streamlit as st
import re

#titre de la page
st.title("URL de la vidéo à traduir ☺")

#entrée de l'url
url=st.text_input("URL")

#verification: l'url contient t'elle qqch?
if st.button("envoyer"):
    if url:
        # Vérifie si c'est une URL YouTube ou Vimeo
        if re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be|vimeo\.com)\/.+', url):
            st.success("URL vidéo valide ! Voici le lien : " + url)
            
        else:
            st.error("⚠️ URL non valide. Ce n'est pas une vidéo")
    else:
        st.error("il n'y a pas d'URL")
