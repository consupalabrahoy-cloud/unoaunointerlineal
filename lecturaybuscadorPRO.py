import streamlit as st
import pandas as pd
import requests
import io
import re
import unicodedata
import json

# URL de los archivos CSV individuales en GitHub para el texto de la Biblia
BOOKS_URLS = {
    "Mateo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Mateo.csv",
    "Marcos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Marcos.csv",
    "Lucas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Lucas.csv",
    "Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Juan.csv",
    "Hechos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Hechos.csv",
    "Romanos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Romanos.csv",
    "1º a los Corintios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/PrimeraCorintios.csv",
    "2º a los Corintios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/SegundaCorintios.csv",
    "Gálatas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Gálatas.csv",
    "Efesios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Efesios.csv",
    "Filipenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Filipenses.csv",
    "Colosenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Colosenses.csv",
    "1º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/PrimeraTesalonicenses.csv",
    "2º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/SegundaTesalonicenses.csv",
    "1º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/PrimeraTimoteo.csv",
    "2º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/SegundaTimoteo.csv",
    "Tito": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Tito.csv",
    "Filemón": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Filemón.csv",
    "Hebreos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Hebreos.csv",
    "Santiago": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Santiago.csv",
    "1º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/PrimeraPedro.csv",
    "2º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/SegundaPedro.csv",
    "1º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/PrimeraJuan.csv",
    "2º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/SegundaJuan.csv",
    "3º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/TerceraJuan.csv",
    "Judas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Judas.csv",
    "Apocalipsis": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Apocalipsis.csv",
}

# URL del archivo JSON del diccionario en GitHub
DICTIONARY_URL = "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/vocabulario_nt.json"

# --- Funciones de Carga de Datos ---
@st.cache_data(ttl=3600)
def load_all_data():
    """Carga y combina los datos de todos los libros en un solo DataFrame."""
    all_dfs = []
    for book_name, url in BOOKS_URLS.items():
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
        combined_df = combined_df.fillna('')
        return combined_df
    return None

@st.cache_data(ttl=3600)
def load_dictionary_data():
    """Carga los datos del diccionario desde el archivo JSON."""
    try:
        response = requests.get(DICTIONARY_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al cargar datos del diccionario: {e}")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al procesar el diccionario: {e}")
        return None

# --- Funciones de Procesamiento y Búsqueda ---
def normalize_greek(word):
    """
    Normaliza una palabra griega eliminando acentos y convirtiendo a minúsculas.
    """
    normalized = unicodedata.normalize('NFD', word)
    stripped = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return stripped.lower()

def parse_and_find_occurrences(df, search_term):
    """
    Busca un término en los DataFrames, normalizando el texto de búsqueda y el
    texto de la Biblia para ignorar mayúsculas y acentos.
    """
    occurrences = []
    normalized_search_term = normalize_greek(search_term)
    
    # Crea una columna normalizada para una búsqueda más eficiente
    df['normalized_text'] = df['Texto'].apply(normalize_greek)
    
    all_matches = df[df['normalized_text'].str.contains(normalized_search_term, na=False, regex=False)]
    
    for _, row in all_matches.iterrows():
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

        occurrences.append({
            'Libro': row['Libro'],
            'Capítulo': row['Capítulo'],
            'Versículo': row['Versículo'],
            'Texto_Español': spanish_text.strip(),
            'Texto_Griego': greek_text.strip()
        })

    return occurrences

def search_word_in_dict(word, dictionary_data):
    """
    Busca una palabra en el diccionario y devuelve su información,
    ignorando mayúsculas, minúsculas y acentos.
    """
    normalized_search_term = normalize_greek(word)
    
    # Crea un diccionario para una búsqueda más rápida O(1)
    if not hasattr(st.session_state, 'dictionary_map'):
        st.session_state.dictionary_map = {normalize_greek(entry.get("palabra", "")): entry for entry in dictionary_data}

    return st.session_state.dictionary_map.get(normalized_search_term)

# --- Streamlit Interface ---
st.title("Lector Interlineal del Nuevo Testamento 📖")
st.write("Selecciona un libro, un capítulo y un versículo para leer el texto interlineal. Puedes hacer clic en una palabra griega para ver su definición, transliteración y análisis morfológico.")

# --- Cargar datos ---
combined_df = load_all_data()
dictionary_data = load_dictionary_data()

if combined_df is None or dictionary_data is None:
    st.warning("No se pudieron cargar los datos. Por favor, revisa tu conexión o intenta de nuevo más tarde.")
    st.stop()
    
# Botón para forzar la actualización de los datos
if st.button("Actualizar la Base de Datos"):
    st.cache_data.clear()
    combined_df = load_all_data()
    dictionary_data = load_dictionary_data()
    st.success("¡Base de datos actualizada con éxito!")

# --- Controles de selección ---
book_options = combined_df['Libro'].unique()
selected_book = st.selectbox("Selecciona un libro:", book_options)

chapters_in_book = combined_df[combined_df['Libro'] == selected_book]['Capítulo'].unique()
selected_chapter = st.selectbox("Selecciona un capítulo:", sorted(chapters_in_book))

verses_in_chapter = combined_df[(combined_df['Libro'] == selected_book) & (combined_df['Capítulo'] == selected_chapter)]['Versículo'].unique()
selected_verse = st.selectbox("Selecciona un versículo:", sorted(verses_in_chapter))

# --- Búsqueda de palabras ---
st.markdown("---")
st.subheader("Buscar una Palabra")
search_term = st.text_input("Ingresa una palabra para buscar (ej. `Dios`, `amor` o `ἀγάπη`):")

if st.button("Buscar"):
    if search_term:
        st.info("Buscando en toda la base de datos...")
        occurrences = parse_and_find_occurrences(combined_df, search_term)
        
        if occurrences:
            st.subheader(f"Resultados de búsqueda para '{search_term}':")
            for occ in occurrences:
                st.write(f"**{occ['Libro']} {occ['Capítulo']}:{occ['Versículo']}**")
                st.write(f"Español: {occ['Texto_Español']}")
                st.write(f"Griego: {occ['Texto_Griego']}")
        else:
            st.warning("No se encontraron coincidencias. Intenta con otra palabra.")
    else:
        st.warning("Por favor, ingresa una palabra en el campo de búsqueda.")


# --- Mostrar texto interlineal ---
st.markdown("---")
st.subheader(f"Texto Interlineal: {selected_book} {selected_chapter}:{selected_verse}")
verse_data = combined_df[(combined_df['Libro'] == selected_book) & (combined_df['Capítulo'] == selected_chapter) & (combined_df['Versículo'] == selected_verse)]

if not verse_data.empty:
    for index, row in verse_data.iterrows():
        st.markdown(f"**{row['Posicion_En_Versiculo']}**")
        st.write(row['RV1960'])
        st.write(row['Original'])
        st.write(row['Transliteracion'])
        st.write(row['Significado'])
        
        # Opciones para el diccionario
        with st.expander(f"Ver información de '{row['Original']}'"):
            word_info = search_word_in_dict(row['Original'], dictionary_data)
            if word_info:
                st.subheader(f"Información de la palabra: {word_info.get('palabra', 'N/A')}")
                st.markdown(f"**Transliteración:** {word_info.get('transliteracion', 'N/A')}")
                st.markdown(f"**Traducción literal:** {word_info.get('traduccion_literal', 'N/A')}")
                st.markdown(f"**Análisis Gramatical:** {word_info.get('analisis_gramatical', 'N/A')}")
            else:
                st.info("En este momento no hay información gramatical para esta palabra.")
else:
    st.warning("Versículo no encontrado. Por favor, selecciona otro.")
