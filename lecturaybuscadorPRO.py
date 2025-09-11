import streamlit as st
import pandas as pd
import requests
import io
import re
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
    #"2º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda%20a%20Tesalonicenses%20-%20Segunda%20de%20Tesalonicenses.csv",
    #"2° a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda a Tesalonicenses - Segunda a Tesalonicenses.csv",
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

# Cargar datos
if 'df' not in st.session_state:
    st.session_state.df = load_all_data()

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
        'Grande': '22px'
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
        
        # Aplica el tamaño de fuente al texto en español y griego
        st.markdown(f'<span style="font-size:{final_font_size};">**{verse_number}** {spanish_text}</span>', unsafe_allow_html=True)
        st.markdown(f'<span style="font-family:serif;font-size:{final_font_size};font-style:italic;">{greek_text}</span>', unsafe_allow_html=True)
    
    # 2. Búsqueda y concordancia
    st.markdown('---')
    st.markdown('#### Buscar en el texto')
    
    search_term = st.text_input('Ingrese una palabra o secuencia de letras en español o griego')

    if search_term:
        # Concordancia de ocurrencias (rápida y local)
        st.markdown('##### Ocurrencias en el texto')
        occurrences_list = parse_and_find_occurrences(st.session_state.df, search_term)
        
        if occurrences_list:
            st.info(f"Se encontraron {len(occurrences_list)} ocurrencias en total.")
            for occ in occurrences_list:
                st.markdown(f"- **{occ['Libro']} {occ['Capítulo']}:{occ['Versículo']}**")
                st.markdown(f"  > {occ['Texto_Español']}")
                st.markdown(f'  > <span style="font-family:serif;font-size:{final_font_size};font-style:italic;">{occ["Texto_Griego"]}</span>', unsafe_allow_html=True)

            # Botón de descarga
            df_to_download = pd.DataFrame(occurrences_list)
            csv_data = df_to_download.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Descargar resultados en CSV",
                data=csv_data,
                file_name=f'concordancia_{search_term}.csv',
                mime='text/csv'
            )

        else:
            st.info("No se encontraron ocurrencias en el texto de los libros.")
else:
    st.error("No se pudo cargar el DataFrame. Por favor, revisa la conexión a internet y el origen de datos.")


