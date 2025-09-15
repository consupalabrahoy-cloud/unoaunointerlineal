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
</style>
""", unsafe_allow_html=True)


# --- Funciones de Carga de Datos ---
def _split_text(full_text):
    """
    Función auxiliar para dividir el texto en español y griego.
    Utiliza una expresión regular para encontrar el punto de división.
    """
    # Expresión regular para encontrar un espacio seguido de un carácter griego
    match = re.search(r'\s(?=[α-ωΑ-Ω])', full_text)
    if match:
        split_index = match.start()
        spanish_text = full_text[:split_index].strip()
        greek_text = full_text[split_index:].strip()
        return spanish_text, greek_text
    return full_text, ""

@st.cache_data(ttl=3600)
def load_all_data():
    """Carga y combina los datos de todos los libros en un solo DataFrame."""
    all_dfs = []
    for book_name, url in BOOKS_URLS.items():
        try:
            df = pd.read_csv(url, sep=',')
            df['Libro'] = book_name
            all_dfs.append(df)
        except Exception as e:
            st.error(f"Error al cargar datos de {book_name}: {e}")
            return None

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df['Capítulo'] = pd.to_numeric(combined_df['Capítulo'], errors='coerce').fillna(0).astype(int)
        combined_df['Versículo'] = pd.to_numeric(combined_df['Versículo'], errors='coerce').fillna(0).astype(int)
        combined_df = combined_df.fillna('')
        
        # Aplicar la lógica de separación de texto
        combined_df[['texto_espanol', 'texto_griego']] = combined_df['Texto'].apply(
            lambda x: pd.Series(_split_text(x))
        )
        return combined_df
    return None

@st.cache_data(ttl=3600)
def load_dictionary_data():
    """Carga los datos del diccionario y los prepara para una búsqueda rápida."""
    try:
        response = requests.get(DICTIONARY_URL, timeout=10)
        response.raise_for_status()
        dictionary_list = response.json()
        
        # Crear un mapa para una búsqueda instantánea
        dictionary_map = {}
        for entry in dictionary_list:
            word = entry.get("palabra", "")
            if word:
                normalized_word = normalize_greek(word)
                dictionary_map[normalized_word] = entry
        
        return dictionary_map
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
    df['normalized_espanol'] = df['texto_espanol'].apply(normalize_greek)
    df['normalized_griego'] = df['texto_griego'].apply(normalize_greek)
    
    all_matches = df[df['normalized_espanol'].str.contains(normalized_search_term, na=False, regex=False) |
                     df['normalized_griego'].str.contains(normalized_search_term, na=False, regex=False)]
    
    for _, row in all_matches.iterrows():
        occurrences.append({
            'Libro': row['Libro'],
            'Capítulo': row['Capítulo'],
            'Versículo': row['Versículo'],
            'Texto_Español': row['texto_espanol'].strip(),
            'Texto_Griego': row['texto_griego'].strip()
        })
    return occurrences

def search_word_in_dict(word, dictionary_data):
    """
    Busca una palabra en el diccionario y devuelve su información.
    Utiliza el mapa de búsqueda instantánea.
    """
    normalized_search_term = normalize_greek(word)
    return dictionary_data.get(normalized_search_term)


# --- Contenido de la Aplicación ---
st.title('Lector Interlineal español-griego del Nuevo Testamento.')
st.markdown('***')
st.markdown('Reina-Valera Antigua y Westcott-Hort.')

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
        df_filtered_by_chapter = df_filtered_by_book[st.session_state.df['Libro'] == selected_chapter]

        for _, row in df_filtered_by_chapter.iterrows():
            st.markdown(f'<span style="font-size:{final_font_size};">**{row["Versículo"]}** {row["texto_espanol"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span style="font-family:serif;font-size:{final_font_size};font-style:italic;">{row["texto_griego"]}</span>', unsafe_allow_html=True)

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
                    st.markdown('**Análisis Morfológico:**')
                    
                    if isinstance(analisis, dict):
                        formatted_analisis = ""
                        for key, value in analisis.items():
                            formatted_analisis += f"- **{key.capitalize()}:** {value}\n"
                        st.markdown(formatted_analisis)
                    elif isinstance(analisis, str):
                        st.markdown(analisis)
                    else:
                        st.markdown('No disponible')

                else:
                    st.warning("No hay información gramatical para esa palabra en este momento.")
            else:
                st.error("No se pudo cargar el diccionario.")

else:
    st.error("No se pudo cargar el DataFrame. Por favor, revisa la conexión a internet y el origen de datos.")
