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

# URL del archivo JSON del diccionario
DICTIONARY_URL = "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/vocabulario_nt.json"


# CSS personalizado para estilizar los botones de descarga
st.markdown("""
<style>
    /* Estiliza los botones de descarga usando su data-testid */
    [data-testid="stDownloadButton"] > button {
        background-color: transparent; /* Fondo transparente */
        color: #0CA7CF;
        border: 1px solid #0CA7CF; /* Borde más fino */
        border-radius: 8px;
        padding: 10px 20px;
        margin-top: 20px; /* Separación del texto superior */
    }

    /* Estilo de los botones de descarga al pasar el ratón */
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #E6EAF0;
        border-color: #0A8AB3;
        color: #0A8AB3;
    }
    
    /* Estilo para el botón de limpiar caché */
    .stButton > button {
        background-color: #f0f2f6;
        color: #262730;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background-color: #e6eaf0;
        border-color: #d0d0d0;
    }
</style>
""", unsafe_allow_html=True)


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
        # Reemplazar valores nulos con cadenas vacías para evitar errores de búsqueda
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
    # Descompone el string en su forma normalizada
    normalized = unicodedata.normalize('NFD', word)
    
    # Filtra los caracteres que no son letras, números o espacios (incluyendo diacríticos)
    stripped = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    # Convierte a minúsculas
    return stripped.lower()

def parse_and_find_occurrences(df, search_term):
    """
    Busca un término en los DataFrames, normalizando el texto de búsqueda y el
    texto de la Biblia para ignorar mayúsculas y acentos.
    """
    occurrences = []
    normalized_search_term = normalize_greek(search_term)

    # Crea una máscara booleana para encontrar las coincidencias en español y griego
    df['normalized_text'] = df['Texto'].apply(normalize_greek)
    
    all_matches = df[df['normalized_text'].str.contains(normalized_search_term, na=False, regex=False)]
    
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

def search_word_in_dict(word, dictionary_data):
    """
    Busca una palabra en el diccionario y devuelve su información,
    ignorando mayúsculas, minúsculas y acentos.
    """
    # Normaliza la palabra de búsqueda para la comparación
    normalized_search_term = normalize_greek(word)
    
    for entry in dictionary_data:
        # Extrae la palabra del diccionario y elimina espacios en blanco
        entry_word = entry.get("palabra", "").strip()
        # Normaliza la palabra del diccionario para la comparación
        normalized_entry_word = normalize_greek(entry_word)
        
        if normalized_entry_word == normalized_search_term:
            return entry
            
    return None

# --- Contenido de la Aplicación ---
st.title('Lector Interlineal español-griego del Nuevo Testamento.')
st.markdown('***')
st.markdown('Reina-Valera Antigua y Westcott-Hort.')

# Botón para limpiar el caché
if st.button('Actualizar datos'):
    st.cache_data.clear()
    st.experimental_rerun()

# Cargar datos
if 'df' not in st.session_state:
    st.session_state.df = load_all_data()
    st.session_state.dict_data = load_dictionary_data()

# Lógica principal de la UI
if st.session_state.df is not None:
    # 1. Selección y lectura del pasaje
    st.sidebar.header('Seleccionar pasaje')

    # Selector para el tamaño de la fuente
    font_size_option = st.sidebar.selectbox(
        'Tamaño de la fuente',
        ['Normal', 'Grande', 'Pequeña']
    )

    font_size_map = {
        'Pequeña': '16px',
        'Normal': '18px',
        'Grande': '23px'
    }

    final_font_size = font_size_map[font_size_option]

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

    # Contenedor expandible para el texto del capítulo
    with st.expander(f'{selected_book} {selected_chapter}', expanded=True):
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

            # Aplica el tamaño de fuente al texto en español y griego
            st.markdown(f'<span style="font-size:{final_font_size};">**{verse_number}** {spanish_text}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="font-family:serif;font-size:{final_font_size};font-style:italic;">{greek_text}</span>', unsafe_allow_html=True)

    # La búsqueda por defecto es en todos los Libros.
    st.markdown('---')
    st.markdown('#### Búsqueda y concordancia (por defecto se hará en todos los Libros).')

    # Se ingresa la palabra a buscar
    search_term = st.text_input('Ingrese una palabra o secuencia de letras en español o griego')
    st.write("") # Línea para espacio en blanco

    # Se muestra la etiqueta de color para el filtro
    st.markdown(f'<span style="color:#0CA7CF;font-weight: bold;">Prefiero filtrar la búsqueda por libros:</span>', unsafe_allow_html=True)

    # Selector de libros para la búsqueda, con etiqueta vacía
    all_books = st.session_state.df['Libro'].unique()
    selected_search_books = st.multiselect(
        "",  # Etiqueta vacía para no duplicar el texto
        options=all_books,
        default=[],
        placeholder="Seleccionar libros..."
    )

    if search_term:
        # Crea pestañas para la concordancia y el diccionario
        tab1, tab2 = st.tabs(["Concordancia", "Diccionario"])

        with tab1:
            st.markdown('##### Ocurrencias en el texto')
            # Si no se selecciona ningún libro, se busca en todos por defecto
            if not selected_search_books:
                df_for_search = st.session_state.df
            else:
                # Si se seleccionan libros, se filtra el DataFrame
                df_for_search = st.session_state.df[st.session_state.df['Libro'].isin(selected_search_books)]

            occurrences_list = parse_and_find_occurrences(df_for_search, search_term)

            if occurrences_list:
                st.info(f"Se encontraron {len(occurrences_list)} ocurrencias en total.")
                for occ in occurrences_list:
                    st.markdown(f"- **{occ['Libro']} {occ['Capítulo']}:{occ['Versículo']}**")
                    st.markdown(f' > <span style="font-size:{final_font_size};">{occ["Texto_Español"]}</span>', unsafe_allow_html=True)
                    st.markdown(f' > <span style="font-family:serif;font-size:{final_font_size};font-style:italic;">{occ["Texto_Griego"]}</span>', unsafe_allow_html=True)

                txt_content = ""
                for occ in occurrences_list:
                    txt_content += f"{occ['Libro']} {occ['Capítulo']}:{occ['Versículo']}\n"
                    txt_content += f"  {occ['Texto_Español']}\n"
                    txt_content += f"  {occ['Texto_Griego']}\n\n"

                st.download_button(
                    label="Descargar resultados en TXT",
                    data=txt_content.encode('utf-8'),
                    file_name=f'concordancia_{search_term}.txt',
                    mime='text/plain'
                )

                json_data = json.dumps(occurrences_list, indent=2).encode('utf-8')
                st.download_button(
                    label="Descargar resultados en JSON",
                    data=json_data,
                    file_name=f'concordancia_{search_term}.json',
                    mime='application/json'
                )

                df_to_download = pd.DataFrame(occurrences_list)
                csv_data = df_to_download.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar resultados en CSV",
                    data=csv_data,
                    file_name=f'concordancia_{search_term}.csv',
                    mime='text/csv'
                )
            else:
                st.info("No se encontraron ocurrencias en el texto de los libros seleccionados.")

        with tab2:
            st.markdown('##### Información del diccionario')
            if st.session_state.dict_data:
                dict_entry = search_word_in_dict(search_term, st.session_state.dict_data)
                if dict_entry:
                    st.markdown(f'**Palabra:** {dict_entry.get("palabra", "No disponible")}')
                    st.markdown(f'**Transliteración:** {dict_entry.get("transliteracion", "No disponible")}')
                    st.markdown(f'**Traducción literal:** {dict_entry.get("traduccion_literal", "No disponible")}')
                    
                    analisis = dict_entry.get("analisis_gramatical", {})
                    if isinstance(analisis, dict):
                        st.markdown('**Análisis Morfológico:**')
                        st.json(analisis)
                    elif isinstance(analisis, str):
                        st.markdown('**Análisis Morfológico:**')
                        st.markdown(analisis)
                    else:
                        st.markdown('**Análisis Morfológico:** No disponible')

                else:
                    st.warning(f"La palabra '{search_term}' no se encontró en el diccionario.")
            else:
                st.error("No se pudo cargar el diccionario.")

else:
    st.error("No se pudo cargar el DataFrame. Por favor, revisa la conexión a internet y el origen de datos.")
