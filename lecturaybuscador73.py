import streamlit as st
import pandas as pd
import requests
import io
import json
import google.generativeai as genai

# Diccionario de libros y sus URL públicas
BOOKS = {
    "Mateo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Mateo.csv",
    "Marcos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Marcos - Marcos.csv",
    "Lucas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Lucas - Lucas.csv",
    "Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Juan - Juan.csv",
    "Hechos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Hechos - Hechos.csv",
    "Romanos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Romanos - Romanos.csv",
    "1º a los Corintios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera de Corintios - Primera de Corintios.csv",
    "2º a los Corintios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda de Corintios - Segunda de Corintios.csv",
    "Gálatas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Gálatas - Gálatas.csv",
    "Efesios": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Efesios - Efesios.csv",
    "Filipenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Filipenses - Filipenses.csv",
    "Colosenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Colosenses - Colosenses.csv",
    "1º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera a Tesalonicenses - Primera a Tesalonicenses.csv",
    #"2º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabohoy-cloud/unoaunointerlineal/main/Segunda a Tesalonicenses - Segunda a Tesalonicenses.csv",
    "1º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera a Timoteo - Primera a Timoteo.csv",
    "2º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda a Timoteo - Segunda a Timoteo.csv",
    "Tito": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Tito - Tito.csv",
    "Filemón": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Filemón - Filemón.csv",
    "Hebreos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Hebreos - Hebreos.csv",
    "Santiago": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Santiago - Santiago.csv",
    "1º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera de Pedro - Primera de Pedro.csv",
    "2º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda de Pedro - Segunda de Pedro.csv",
    "1º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera de Juan - Primera de Juan.csv",
    "2º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda de Juan - Segunda de Juan.csv",
    "3º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/refs/heads/main/Tercera%20de%20Juan%20-%20Tercera%20de%20Juan.csv",
    "Judas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Judas - Judas.csv",
    "Apocalipsis": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Apocalipsis - Apocalipsis.csv",
}

@st.cache_data(ttl=3600)
def load_all_data():
    """Loads and combines the data from all books into a single DataFrame."""
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
    Finds a term in the DataFrames.
    """
    occurrences = []
    
    spanish_matches = df['Texto'].str.lower().str.contains(search_term.lower(), na=False, regex=False)
    greek_matches = df['Texto'].str.contains(search_term.lower(), na=False, regex=False)
    
    all_matches = df[spanish_matches | greek_matches]

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

        language = "Español"
        if search_term.lower() in greek_text.lower():
            language = "Griego"
        
        occurrences.append({
            "libro": row['Libro'],
            "capitulo": row['Capítulo'],
            "versiculo": verse_number,
            "spanish_text": spanish_text,
            "greek_text": greek_text,
            "found_word": search_term,
            "language": language
        })
    
    return occurrences

def get_gemini_analysis(word, api_key):
    """
    Analyzes a Greek word using the Gemini API.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    Actúa como un lingüista experto en el griego koiné del Nuevo Testamento. Proporciona una transliteración, una traducción literal al español y un análisis gramatical detallado de la palabra griega "{word}".
    El análisis gramatical debe incluir la raíz, la clase de palabra (verbo, sustantivo, adjetivo, etc.), el caso, el género, el número, el tiempo, la voz, el modo (si aplica) y cualquier otra información relevante para su interpretación.
    Formato de respuesta JSON:
    {{
      "transliteracion": "...",
      "traduccion_literal": "...",
      "analisis_gramatical": "..."
    }}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        if response and response.text:
            return json.loads(response.text)
    except Exception as e:
        st.error(f"Ocurrió un error con la API de Gemini: {e}")
    
    return None

def main():
    """
    Main function of the application.
    """
    st.title("Lector y Buscador Interlineal del NT. Reina-Valera Antigua y Westcott-Hort.")
    st.markdown("---")

    combined_df = load_all_data()

    if combined_df is None:
        st.error("No se pudo cargar la base de datos completa. Por favor, verifica las URL y tu conexión a internet.")
        return

    mode = st.radio(
        "Selecciona el modo de uso:",
        ("Modo Lector", "Modo Buscador"),
        index=0
    )

    if mode == "Modo Lector":
        st.markdown("---")
        st.write("Selecciona un libro y un capítulo para leer el texto interlineal.")
        
        if 'selected_book' not in st.session_state:
            st.session_state.selected_book = list(BOOKS.keys())[0]
        if 'selected_chapter' not in st.session_state:
            first_book_df = combined_df[combined_df['Libro'] == st.session_state.selected_book]
            if not first_book_df.empty:
                first_chapter = sorted(first_book_df['Capítulo'].unique())[0]
                st.session_state.selected_chapter = first_chapter
            else:
                st.session_state.selected_chapter = 1
        if 'font_size' not in st.session_state:
            st.session_state.font_size = 18

        col1, col2, col3 = st.columns([1, 1, 2])
        with col3:
            st.session_state.font_size = st.slider(
                "Tamaño de la fuente:",
                min_value=16,
                max_value=30,
                value=st.session_state.font_size
            )
        
        selected_book = st.selectbox("Selecciona un libro:", list(BOOKS.keys()), index=list(BOOKS.keys()).index(st.session_state.selected_book))
        if selected_book != st.session_state.selected_book:
            st.session_state.selected_book = selected_book
            new_book_df = combined_df[combined_df['Libro'] == selected_book]
            if not new_book_df.empty:
                first_chapter = sorted(new_book_df['Capítulo'].unique())[0]
                st.session_state.selected_chapter = first_chapter
            else:
                st.session_state.selected_chapter = 1
            st.rerun()

        chapters = sorted(combined_df[combined_df['Libro'] == st.session_state.selected_book]['Capítulo'].unique())
        
        try:
            current_chapter_index = chapters.index(st.session_state.selected_chapter)
        except ValueError:
            current_chapter_index = 0
            st.session_state.selected_chapter = chapters[0]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Capítulo Anterior", disabled=(current_chapter_index == 0)):
                st.session_state.selected_chapter = chapters[current_chapter_index - 1]
                st.rerun()
        with col2:
            if st.button("Capítulo Siguiente", disabled=(current_chapter_index == len(chapters) - 1)):
                st.session_state.selected_chapter = chapters[current_chapter_index + 1]
                st.rerun()

        selected_chapter = st.selectbox(
            "Selecciona un capítulo:",
            chapters,
            index=chapters.index(st.session_state.selected_chapter)
        )
        if selected_chapter != st.session_state.selected_chapter:
            st.session_state.selected_chapter = selected_chapter
            st.rerun()

        st.markdown("---")
        st.subheader(f"{st.session_state.selected_book} {st.session_state.selected_chapter}")
        chapter_verses = combined_df[(combined_df['Libro'] == st.session_state.selected_book) & (combined_df['Capítulo'] == st.session_state.selected_chapter)]

        if not chapter_verses.empty:
            for _, row in chapter_verses.iterrows():
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
                
                st.markdown(f"**Versículo {verse_number}**")
                st.markdown(f"<p style='font-size:{st.session_state.font_size}px;'>{spanish_text.strip()}</p>", unsafe_allow_html=True)
                if found_greek_start:
                    st.markdown(f"<p style='font-size:{st.session_state.font_size}px;'><i>{greek_text.strip()}</i></p>", unsafe_allow_html=True)
                else:
                    st.warning("Al parecer no hay texto griego en este versículo.")
        else:
            st.warning("No se encontraron versículos en este capítulo. Por favor, revisa tu selección.")

    elif mode == "Modo Buscador":
        st.markdown("---")
        st.header("Modo Buscador")
        st.markdown("---")
        
        # New section for Gemini
        st.subheader("Análisis con Gemini")
        st.write("Copia y pega una palabra griega para obtener su transliteración, traducción y análisis morfológico.")
        
        api_key = st.text_input("Ingresa tu API Key de Google Gemini:", type="password")
        greek_word_input = st.text_input("Palabra Griega:", placeholder="Ejemplo: ἀγαθός")
        
        if st.button("Analizar Palabra Griega"):
            if not api_key:
                st.error("Por favor, ingresa tu API Key de Gemini para usar esta función.")
            elif not greek_word_input:
                st.warning("Por favor, ingresa una palabra griega para analizar.")
            else:
                with st.spinner('Analizando palabra...'):
                    analysis = get_gemini_analysis(greek_word_input, api_key)
                    if analysis:
                        st.subheader("Resultados del Análisis:")
                        st.markdown(f"**Transliteración:** `{analysis.get('transliteracion', 'N/A')}`")
                        st.markdown(f"**Traducción Literal:** `{analysis.get('traduccion_literal', 'N/A')}`")
                        st.markdown(f"**Análisis Morfológico:** `{analysis.get('analisis_gramatical', 'N/A')}`")
        
        st.markdown("---")
        st.header("La búsqueda se realizará en todos los Libros o si prefiere, utilice el filtro.")
        
        search_term = st.text_input(
            "Ingresa la secuencia de letras a buscar:",
            placeholder="Ejemplo: σπ o libertad"
        )

        with st.expander("Filtrar la búsqueda de la palabra por Libros:"):
            if 'book_selection' not in st.session_state:
                st.session_state.book_selection = {book: False for book in BOOKS.keys()}

            for book_name in BOOKS.keys():
                st.session_state.book_selection[book_name] = st.checkbox(
                    book_name, 
                    value=st.session_state.book_selection[book_name], 
                    key=f"checkbox_{book_name}"
                )

        st.markdown("---")

        if st.button("Buscar y analizar", key="search_button"):
            if not search_term:
                st.warning("Por favor, ingresa una secuencia de letras a buscar.")
            else:
                selected_books_list = [book for book, is_selected in st.session_state.book_selection.items() if is_selected]
                
                if not selected_books_list:
                    books_to_search = list(BOOKS.keys())
                else:
                    books_to_search = selected_books_list

                try:
                    filtered_df = combined_df[combined_df['Libro'].isin(books_to_search)]
                    all_occurrences = parse_and_find_occurrences(filtered_df, search_term)
                    
                    if not all_occurrences:
                        st.warning(f"No se encontraron coincidencias que contengan '{search_term}' en los libros seleccionados.")
                    else:
                        st.subheader(f" {len(all_occurrences)} resultados encontrados que contienen '{search_term}':")
                        
                        results_df = pd.DataFrame(all_occurrences)
                        
                        results_df = results_df.rename(columns={
                            'spanish_text': 'Texto en Español',
                            'greek_text': 'Texto en Griego',
                            'found_word': 'Palabra Encontrada',
                            'language': 'Idioma'
                        })

                        csv_data = results_df.to_csv(index=False).encode('utf-8')
                        
                        st.download_button(
                            label="Descargar resultados en CSV",
                            data=csv_data,
                            file_name=f"resultados_{search_term}.csv",
                            mime="text/csv",
                        )

                        for occurrence in all_occurrences:
                            st.markdown(f"**{occurrence['libro']} {occurrence['capitulo']}:{occurrence['versiculo']}**")
                            st.markdown(f"{occurrence['spanish_text']}")
                            st.markdown(f"_{occurrence['greek_text']}_")
                            st.markdown(f"**Coincidencia encontrada en {occurrence['language']}:** `{occurrence['found_word']}`")
                            st.markdown("---")

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")

if __name__ == "__main__":
    main()

