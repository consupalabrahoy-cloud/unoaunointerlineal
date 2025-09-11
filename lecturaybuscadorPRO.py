import streamlit as st
import pandas as pd
import requests
import io
import re
import json
import base64

# Importa el SDK de Firebase Admin
import firebase_admin
from firebase_admin import credentials, firestore

# Diccionario de libros y sus URL públicas
BOOKS = {
    "Mateo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Mateo.csv",
    "Marcos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Marcos - Marcos.csv",
    "Lucas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Lucas - Lucas.csv",
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
            # Lee la cadena Base64 del archivo de secretos
            key_base64 = st.secrets.firebase_key_base64
            # Decodifica la cadena a un JSON legible
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
            df['Libro'] = book_name  # Agrega la columna del libro para identificarlo
            all_dfs.append(df)
        except requests.exceptions.RequestException as e:
            st.error(f"Error al cargar datos de {book_name}: {e}")
            return None
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al procesar {book_name}: {e}")
            return None

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        # Convierte las columnas a tipos de datos correctos
        combined_df['Capítulo'] = pd.to_numeric(combined_df['Capítulo'], errors='coerce').fillna(0).astype(int)
        combined_df['Versículo'] = pd.to_numeric(combined_df['Versículo'], errors='coerce').fillna(0).astype(int)
        return combined_df
    return None

db = init_firebase()

# --- Contenido de la Aplicación ---
st.title('Interlineal Bíblico')
st.markdown('***')
st.markdown('¡Bienvenido! Esta es una herramienta para el estudio interlineal del Nuevo Testamento en griego.')

# Carga de datos
if 'df' not in st.session_state:
    st.session_state.df = load_all_data()

if st.session_state.df is not None:
    # Selección de libro, capítulo y versículo
    selected_book = st.selectbox(
        'Seleccione un libro',
        st.session_state.df['Libro'].unique()
    )

    df_filtered_by_book = st.session_state.df[st.session_state.df['Libro'] == selected_book]
    capitulos = sorted(df_filtered_by_book['Capítulo'].unique())
    selected_chapter = st.selectbox(
        'Seleccione un capítulo',
        capitulos
    )

    df_filtered_by_chapter = df_filtered_by_book[df_filtered_by_book['Capítulo'] == selected_chapter]
    versiculos = sorted(df_filtered_by_chapter['Versículo'].unique())
    selected_verse = st.selectbox(
        'Seleccione un versículo',
        versiculos
    )

    # Mostrar el texto del versículo seleccionado
    df_selected_verse = df_filtered_by_chapter[df_filtered_by_chapter['Versículo'] == selected_verse]

    if not df_selected_verse.empty:
        full_text = df_selected_verse['Texto'].iloc[0]
        st.markdown(f"### {selected_book} {selected_chapter}:{selected_verse}")
        
        # Separar el texto en español y griego
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
        
        st.markdown("#### Texto en Español")
        st.write(spanish_text)
        
        st.markdown("#### Texto en Griego")
        st.markdown(f'<p style="font-family:serif;font-size:20px;font-style:italic;">{greek_text}</p>', unsafe_allow_html=True)

    # Búsqueda de palabras
    st.markdown('***')
    st.markdown('#### Búsqueda de Palabras')
    search_term = st.text_input('Ingrese una palabra en español o griego para buscar en el vocabulario')

    if search_term:
        word_info = get_word_from_firestore(db, search_term)
        
        if word_info:
            st.success("Palabra encontrada en la base de datos de vocabulario.")
            st.write(word_info)
        else:
            st.warning("No se encontró información sobre esa palabra en la base de datos de vocabulario.")
            
        occurrences = parse_and_find_occurrences(st.session_state.df, search_term)
        
        if occurrences:
            st.markdown(f'#### Ocurrencias de "{search_term}"')
            for occ in occurrences:
                st.write(f"- {occ['Libro']} {occ['Capítulo']}:{occ['Versículo']}")
        else:
            st.info("No se encontraron ocurrencias en el texto de los libros.")
else:
    st.error("No se pudo cargar el DataFrame. Por favor, revisa la conexión a internet y el origen de datos.")
