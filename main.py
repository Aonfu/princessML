import streamlit as st
import re
from urllib.parse import urlparse, parse_qs
import whisper
import yt_dlp
import os
from deep_translator import MyMemoryTranslator
import tempfile
from streamlit_player import st_player
import json
from pathlib import Path
import subprocess

# Initialisation de la session state
if 'translated_segments' not in st.session_state:
    st.session_state.translated_segments = None
if 'video_id' not in st.session_state:
    st.session_state.video_id = None
if 'current_time' not in st.session_state:
    st.session_state.current_time = 0
if 'translation_done' not in st.session_state:
    st.session_state.translation_done = False

# Configuration de la page
st.set_page_config(
    page_title="Universal YouTube Translator",
    page_icon="🌍",
    layout="wide"
)

# Fonction pour extraire l'ID de la vidéo YouTube
def extract_video_id(url):
    try:
        if 'youtu.be' in url:
            return url.split('/')[-1]
        query = parse_qs(urlparse(url).query)
        return query.get('v', [None])[0]
    except:
        return None

# Fonction pour télécharger la vidéo
def download_video(video_id):
    ydl_opts = {
        "format": "best",
        "outtmpl": f"temp_video_{video_id}.%(ext)s",
        "ffmpeg_location": "./ffmpeg.exe",
        # ⬇️ cookies extraits de Firefox
        "cookiesfrombrowser": ("firefox", "1eyrfscf.default-release") if "1eyrfscf.default-release" else ("firefox",),
        # un peu plus verbeux pour diagnostiquer
        "verbose": True,
        # (optionnel) évite de re-télécharger si déjà présent
        "overwrites": False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        return str(e)

# Fonction pour transcrire et traduire
def transcribe_and_translate(video_file, target_lang):
    try:
        # Codes de langue pour l'API de traduction
        LANG_CODES = {
            "Français": "fr-FR",
            "English": "en-GB",
            "Español": "es-ES",
            "Deutsch": "de-DE",
            "中文": "zh-CN",
            "日本語": "ja-JP"
        }
        
        # Charger le modèle Whisper
        model = whisper.load_model("base")
        
        # Transcrire l'audio et détecter la langue
        result = model.transcribe(video_file)
        detected_lang = result.get('language', 'en-GB')
        
        # Mapper les codes de langue Whisper vers les codes MyMemory
        WHISPER_TO_MYMEMORY = {
            'en': 'en-GB',
            'fr': 'fr-FR',
            'es': 'es-ES',
            'de': 'de-DE',
            'zh': 'zh-CN',
            'ja': 'ja-JP'
        }
        
        source_lang = WHISPER_TO_MYMEMORY.get(detected_lang, 'en-GB')
        
        # Initialiser le traducteur avec la langue source détectée
        translator = MyMemoryTranslator(source=source_lang, target=LANG_CODES[target_lang])
        
        # Traduire les segments
        translated_segments = []
        for segment in result["segments"]:
            try:
                # Diviser le texte en morceaux plus petits si nécessaire (500 caractères max)
                text = segment["text"]
                if len(text) > 500:
                    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
                    translated_text = ' '.join([translator.translate(chunk) for chunk in chunks])
                else:
                    translated_text = translator.translate(text)
                
                translated_segments.append({
                    'text': translated_text,
                    'start': segment['start'],
                    'end': segment['end']
                })
            except Exception as e:
                st.warning(f"Erreur lors de la traduction d'un segment : {str(e)}")
                translated_segments.append({
                    'text': segment["text"],
                    'start': segment['start'],
                    'end': segment['end']
                })
        
        return translated_segments
    except Exception as e:
        return str(e)

def create_srt_file(segments, output_srt):
    """Créer un fichier de sous-titres SRT"""
    with open(output_srt, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{segment['text']}\n\n")

def format_timestamp(seconds):
    """Convertir les secondes en format timestamp SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def create_subtitled_video(video_path, segments, output_path):
    """Créer une vidéo avec sous-titres incrustés en utilisant FFmpeg"""
    try:
        # Créer le fichier SRT temporaire
        srt_path = os.path.splitext(output_path)[0] + '.srt'
        create_srt_file(segments, srt_path)
        
        # Commande FFmpeg pour ajouter les sous-titres
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', f"subtitles={srt_path}:force_style='FontSize=24,FontName=Arial,PrimaryColour=&HFFFFFF,BackColour=&H000000,Outline=2,Shadow=1,MarginV=30'",
            '-c:a', 'copy',
            output_path,
            '-y'
        ]
        
        # Exécuter la commande FFmpeg
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Supprimer le fichier SRT temporaire
        if os.path.exists(srt_path):
            os.remove(srt_path)
            
        if process.returncode == 0:
            return True
        else:
            st.error(f"Erreur FFmpeg : {process.stderr}")
            return False
            
    except Exception as e:
        st.error(f"Erreur lors de la création de la vidéo : {str(e)}")
        return False

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
    .transcript-text {
        font-size: 16px;
        line-height: 1.8;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin: 5px 0;
    }
    .video-container {
        margin: 20px 0;
        position: relative;
    }
    .subtitle-overlay {
        position: absolute;
        bottom: 10%;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        font-size: 18px;
        text-align: center;
        z-index: 1000;
        width: 80%;
    }
    </style>
""", unsafe_allow_html=True)

# En-tête
st.markdown('<h1 class="main-title">Universal YouTube Translator 🌍</h1>', unsafe_allow_html=True)

# Onglets
tab1, tab2, tab3 = st.tabs(["Traduction", "À propos", "Contact"])

def on_time_change():
    st.session_state.current_time = st.session_state.time_slider

with tab1:
    st.markdown('<h2 class="section-title">Traduisez vos vidéos YouTube</h2>', unsafe_allow_html=True)
    
    # Interface utilisateur
    url = st.text_input("Entrez l'URL de la vidéo YouTube", placeholder="https://www.youtube.com/watch?v=...")
    langues = ["Français", "English", "Español", "Deutsch", "中文", "日本語"]
    langue_cible = st.selectbox("Choisissez la langue de traduction", langues)
    
    # Traitement de la vidéo
    if st.button("Traduire la vidéo", type="primary"):
        if url and re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+', url):
            video_id = extract_video_id(url)
            if video_id:
                st.session_state.video_id = video_id
                
                # Créer un dossier temporaire pour les fichiers
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                
                with st.spinner('Téléchargement de la vidéo...'):
                    video_file = download_video(video_id)
                    
                    if isinstance(video_file, str) and os.path.exists(video_file):
                        with st.spinner('Transcription et traduction en cours...'):
                            result = transcribe_and_translate(video_file, langue_cible)
                            
                            if isinstance(result, list):
                                st.session_state.translated_segments = result
                                st.session_state.translation_done = True
                                
                                # Créer la vidéo sous-titrée
                                with st.spinner('Création de la vidéo sous-titrée...'):
                                    output_path = f'temp/video_soustitree_{video_id}.mp4'
                                    if create_subtitled_video(video_file, result, output_path):
                                        st.success("Vidéo sous-titrée créée avec succès!")
                                        
                                        # Bouton de téléchargement
                                        with open(output_path, 'rb') as f:
                                            st.download_button(
                                                label="📥 Télécharger la vidéo sous-titrée",
                                                data=f,
                                                file_name=f"video_traduite_{langue_cible.lower()}.mp4",
                                                mime="video/mp4"
                                            )
                                        
                                        # Aperçu de la vidéo
                                        st.video(output_path)
                                    else:
                                        st.error("Erreur lors de la création de la vidéo sous-titrée.")
                                
                                # Nettoyage des fichiers temporaires
                                try:
                                    os.remove(video_file)
                                except:
                                    pass
                            else:
                                st.error(f"Erreur lors de la transcription/traduction : {result}")
                    else:
                        st.error(f"Erreur lors du téléchargement : {video_file}")
            else:
                st.error("Impossible d'extraire l'ID de la vidéo.")
        else:
            st.error("URL non valide. Veuillez entrer une URL YouTube valide.")

    # Afficher la vidéo et les sous-titres si la traduction est terminée
    if st.session_state.translation_done and st.session_state.translated_segments:
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        
        # Afficher la vidéo YouTube originale
        st_player(f"https://www.youtube.com/watch?v={st.session_state.video_id}")
        
        # Créer une zone pour les sous-titres
        subtitle_container = st.container()
        
        # Slider pour la position
        st.slider(
            "Position dans la vidéo (secondes)",
            0,
            int(st.session_state.translated_segments[-1]['end']),
            key='time_slider',
            value=st.session_state.current_time,
            on_change=on_time_change
        )
        
        # Trouver et afficher le sous-titre actuel
        current_subtitle = None
        for segment in st.session_state.translated_segments:
            if segment['start'] <= st.session_state.current_time <= segment['end']:
                current_subtitle = segment['text']
                break
        
        with subtitle_container:
            if current_subtitle:
                st.markdown(f'<div class="subtitle-overlay">{current_subtitle}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Option pour afficher la transcription complète
        show_transcript = st.checkbox("Afficher la transcription complète")
        if show_transcript:
            show_timecodes = st.checkbox("Afficher les timecodes")
            for segment in st.session_state.translated_segments:
                if show_timecodes:
                    minutes = int(segment['start'] // 60)
                    seconds = int(segment['start'] % 60)
                    st.markdown(f'<div class="transcript-text">[{minutes:02d}:{seconds:02d}] {segment["text"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="transcript-text">{segment["text"]}</div>', unsafe_allow_html=True)

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
