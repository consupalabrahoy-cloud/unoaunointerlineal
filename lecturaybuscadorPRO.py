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
# REEMPLAZA las URLs con las URL raw de tus archivos CSV en GitHub
# NOTA: Se ha corregido la URL de Mateo para que sea consistente
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

def get_word_from_firestore(db, word):
    """
    Busca información sobre una palabra en la base de datos de Firestore.
    """
    if db:
        # Asume que tu colección se llama 'vocabulario_NT' y el campo de la palabra griega es 'palabra'
        # y el campo de la traducción al español es 'traduccion'
        # Ajusta los nombres de los campos si son diferentes.
        
        # Búsqueda por la palabra exacta
        # La forma de buscar la palabra exacta es con `where('palabra', '==', word)`
        docs = db.collection('vocabulario_NT').where('palabra', '==', word).stream()
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

        # Determina si la coincidencia fue en español o
