import streamlit as st
import pandas as pd
import requests
import io
import re
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
import unicodedata

# Diccionario de libros y sus URL públicas
BOOKS = {
    "Mateo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Mateo.csv",
    "Marcos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Marcos%20-%20Marcos.csv",
    "Lucas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Lucas%20-%20Lucas.csv",
    "Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Juan%20-%20Juan.csv",
    "Hechos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Hechos%20-%20Hechos.csv",
    "Romanos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Romanos%20-%20Romanos.csv",
    "1º a los Corintios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera%20de%20Corintios%20-%20Primera%20de%20Corintios.csv",
    "2º a los Corintios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda%20de%20Corintios%20-%20Segunda%20de%20Corintios.csv",
    "Gálatas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Gálatas%20-%20Gálatas.csv",
    "Efesios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Efesios%20-%20Efesios.csv",
    "Filipenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Filipenses%20-%20Filipenses.csv",
    "Colosenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Colosenses%20-%20Colosenses.csv",
    "1º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera%20a%20Tesalonicenses%20-%20Primera%20a%20Tesalonicenses.csv",
    "2º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda%20a%20Tesalonicenses%20-%20Segunda%20a%20Tesalonicenses.csv",
    "1º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera%20a%20Timoteo%20-%20Primera%20a%20Timoteo.csv",
    "2º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda%20a%20Timoteo%20-%20Segunda%20a%20Timoteo.csv",
    "Tito": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Tito%20-%20Tito.csv",
    "Filemón": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Filemón%20-%20Filemón.csv",
    "Hebreos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Hebreos%20-%20Hebreos.csv",
    "Santiago": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Santiago%20-%20Santiago.csv",
    "1º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera%20de%20Pedro%20-%20Primera%20de%20Pedro.csv",
    "2º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda%20de%20Pedro%20-%20Segunda%20de%20Pedro.csv",
    "1º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera%20de%20Juan%20-%20Primera%20de%20Juan.csv",
    "2º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda%20de%20Juan%20-%20Segunda%20de%20Juan.csv",
    "3º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/refs/heads/main/Tercera%20de%20Juan%20-%20Tercera%20de%20Juan.csv",
    "Judas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Judas%20-%20Judas.csv",
    "Apocalipsis": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Apocalipsis%20-%20Apocalipsis.csv",
}

# --- Inicialización de Firebase (con Streamlit Secrets) ---
def init_firebase():
    """Inicializa la app de Firebase si aún no ha sido inicializada."""
    if not firebase_admin._apps:
        try:
            key_base64 = st.secrets.firebase_key_base64
            key_json = base64.b64decode(key_base64).decode('utf-8')
            key_dict = json.loads(key_json)
            
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
            st.success("Conexión con Firebase establecida.")
        except Exception as e:
            st.error(f"Error al inicializar Firebase: {e}")
            st.info("Asegúrate de que la clave de Firebase esté correctamente codificada en Base64 en tu `secrets.toml`.")
            return None
    return firestore.client()

@st.cache_data(ttl=3600)
def load_all_data():
    """Carga y combina los datos de todos los libros en un solo DataFrame."""
    all_dfs = []
    for book_name, url in BOOKS.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            text_content = response.content.decode('utf-8')
            df = pd.read_csv(io.StringIO(text_content), sep=',')
            df['Libro'] = book_name
            all_dfs.append(df)
        except requests.exceptions.RequestException as e:
            st.error(f"Error al cargar datos de {book_name}: {e}")
            return None
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al procesar {book_name}: {e}")
            return None

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df['Capítulo'] = pd.to_numeric(combined_df['Capítulo'], errors='coerce').fillna(0).astype(int)
        combined_df['Versículo'] = pd.to_numeric(combined_df['Versículo'], errors='coerce').fillna(0).astype(int)
        return combined_df
    return None

def get_word_from_firestore(word):
    """
    Busca información sobre una palabra en la base de datos de Firestore.
    Se conecta directamente a la base de datos sin usar la caché.
    """
    db = firestore.client()
    if db:
        normalized_search_word = unicodedata.normalize('NFC', word.lower().strip())
        
        docs = db.collection('vocabulario_nt').where('palabra', '==', normalized_search_word).stream()
        for doc in docs:
            return doc.to_dict()

    return None

def parse_and_find_occurrences(df, search_term):
    """
    Busca un término en los DataFrames.
    """
    occurrences = []
    
    # Crea una máscara booleana para encontrar las coincidencias en español y griego
    spanish_matches = df['Texto'].str.lower().str.contains(search_term.lower(), na=False, regex=False)
    greek_matches = df['Texto'].str.contains(search_term.lower(), na=False, regex=False)
    
    # Combina las coincidencias de ambos idiomas
    all_matches = df[spanish_matches | greek_matches]

    for _, row in all_matches.iterrows():
        full_text = str(row['Texto'])
        verse_number = row['Versículo']

        # Separa el texto en español y griego
        spanish_text = ""
        greek_text = ""
        found_greek_start = False
        
        for char in full_text:
            if '\u0370' <= char <= '\u03FF' or '\u1F00' <= char <= '\u1FFF':
                found_greek_start = True
            
            if not found_greek_start:
                spanish_text += char
            else:
                greek_text += char
        
        occurrences.append({
            'Libro': row['Libro'],
            'Capítulo': row['Capítulo'],
            'Versículo': row['Versículo'],
            'Texto_Español': spanish_text.strip(),
            'Texto_Griego': greek_text.strip()
        })
    
    return occurrences

# --- Contenido de la Aplicación ---
st.title('Lector Interlineal del Nuevo Testamento')
st.markdown('***')
st.markdown('¡Bienvenido! Esta es una herramienta para el estudio interlineal del Nuevo Testamento en griego.')

# Inicializar Firebase
init_firebase()

# Cargar datos
if 'df' not in st.session_state:
    st.session_state.df = load_all_data()

# Lógica principal de la UI
if st.session_state.df is not None:
    # 1. Selección y lectura del pasaje
    st.sidebar.header('Seleccionar pasaje')
    selected_book = st.sidebar.selectbox(
        'Libro',
        st.session_state.df['Libro'].unique()
    )

    df_filtered_by_book = st.session_state.df[st.session_state.df['Libro'] == selected_book]
    capitulos = sorted(df_filtered_by_book['Capítulo'].unique())
    selected_chapter = st.sidebar.selectbox(
        'Capítulo',
        capitulos
    )

    st.header(f'{selected_book} {selected_chapter}')
    df_filtered_by_chapter = df_filtered_by_book[df_filtered_by_book['Capítulo'] == selected_chapter]

    for _, row in df_filtered_by_chapter.iterrows():
        full_text = str(row['Texto'])
        verse_number = row['Versículo']

        spanish_text = ""
        greek_text = ""
        found_greek_start = False
        
        for char in full_text:
            if '\u0370' <= char <= '\u03FF' or '\u1F00' <= char <= '\u1FFF':
                found_greek_start = True
            
            if not found_greek_start:
                spanish_text += char
            else:
                greek_text += char
        
        st.markdown(f"**{verse_number}** {spanish_text}")
        st.markdown(f'<span style="font-family:serif;font-size:18px;font-style:italic;">{greek_text}</span>', unsafe_allow_html=True)
    
    # 2. Búsqueda y concordancia
    st.markdown('---')
    st.markdown('#### Buscar en el vocabulario y el texto')
    
    search_term = st.text_input('Ingrese una palabra en español o griego')

    if search_term:
        # B. Concordancia de ocurrencias (rápida y local)
        st.markdown('##### Ocurrencias en el texto')
        occurrences = parse_and_find_occurrences(st.session_state.df, search_term)
        
        if occurrences:
            st.info(f"Se encontraron {len(occurrences)} ocurrencias en total.")
            for occ in occurrences:
                st.markdown(f"- **{occ['Libro']} {occ['Capítulo']}:{occ['Versículo']}**")
                st.markdown(f"  > {occ['Texto_Español']}")
                st.markdown(f'  > <span style="font-family:serif;font-size:16px;font-style:italic;">{occ["Texto_Griego"]}</span>', unsafe_allow_html=True)
        else:
            st.info("No se encontraron ocurrencias en el texto de los libros.")

        # A. Información de la base de datos (con botón)
        st.markdown('---')
        st.markdown('##### Más información sobre la palabra seleccionada')
        
        if st.button('Obtener información del vocabulario'):
            word_info = get_word_from_firestore(search_term)
            if word_info:
                st.info(f"Información para: '{search_term}'")
                
                # Mostrar campos específicos en un orden legible
                st.markdown(f"**Palabra:** {word_info.get('palabra', 'N/A')}")
                st.markdown(f"**Traducción:** {word_info.get('traduccion', 'N/A')}")
                st.markdown(f"**Número Strong:** {word_info.get('strong', 'N/A')}")
                st.markdown(f"**Transliteración:** {word_info.get('transliteracion', 'N/A')}")
                st.markdown(f"**Pronunciación:** {word_info.get('pronunciacion', 'N/A')}")
                st.markdown(f"**Análisis morfológico:** {word_info.get('analisis_morfologico', 'N/A')}")
                st.markdown(f"**Análisis sintáctico:** {word_info.get('analisis_sintactico', 'N/A')}")
            else:
                st.warning(f"No se encontró información en el vocabulario para: '{search_term}'")
else:
    st.error("No se pudo cargar el DataFrame. Por favor, revisa la conexión a internet y el origen de datos.")
