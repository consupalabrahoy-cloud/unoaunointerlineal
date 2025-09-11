import streamlit as st
import pandas as pd
import requests
import io
import re

# Diccionario de libros y sus URL públicas
# REEMPLAZA las URLs con las URL raw de tus archivos CSV en GitHub
# NOTA: Se ha corregido la URL de Mateo para que sea consistente
BOOKS = {
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
    "Santiago": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/PrimeraPedro.csv",
    "1º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Santiago.csv",
    "2º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/SegundaPedro.csv",
    "1º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/PrimeraJuan.csv",
    "2º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/SegundaJuan.csv",
    "3º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/refs/heads/main/TerceraJuan.csv",
    "Judas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Judas.csv",
    "Apocalipsis": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Apocalipsis.csv",
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

        # Determina si la coincidencia fue en español o griego
        language = "Español"
        if search_term.lower() in greek_text.lower():
            language = "Griego"
        
        occurrences.append({
            "libro": row['Libro'],
            "capitulo": row['Capítulo'],
            "versiculo": verse_number,
            "spanish_text": spanish_text.strip(),
            "greek_text": greek_text.strip(),
            "found_word": search_term,
            "language": language
        })
    
    return occurrences

def main():
    """
    Función principal de la aplicación.
    """
    st.title("Lector y Buscador Interlineal del NT. Reina-Valera Antigua y Westcott-Hort.")
    st.markdown("---")

    combined_df = load_all_data()

    if combined_df is None:
        st.error("No se pudo cargar la base de datos completa. Por favor, verifica las URL y tu conexión a internet.")
        return

    # Modo de selección
    mode = st.radio(
        "Selecciona el modo de uso:",
        ("Modo Lector", "Modo Buscador"),
        index=0
    )

    if mode == "Modo Lector":
        st.markdown("---")
        st.write("Selecciona un libro y un capítulo para leer el texto interlineal.")
        
        # Inicializa el estado de la sesión de manera segura
        if 'selected_book' not in st.session_state:
            st.session_state.selected_book = list(BOOKS.keys())[0]
        if 'font_size' not in st.session_state:
            st.session_state.font_size = 18

        # Controles de navegación y fuente
        col1, col2, col3 = st.columns([1, 1, 2])
        with col3:
            st.session_state.font_size = st.slider(
                "Tamaño de la fuente:",
                min_value=16,
                max_value=30,
                value=st.session_state.font_size
            )
        
        # Selectbox para el libro
        selected_book = st.selectbox(
            "Selecciona un libro:", 
            list(BOOKS.keys()), 
            index=list(BOOKS.keys()).index(st.session_state.selected_book)
        )
        
        # Lógica para cambiar de libro y actualizar el capítulo
        if selected_book != st.session_state.selected_book:
            st.session_state.selected_book = selected_book
            # No es necesario un st.rerun() aquí, Streamlit lo hará por sí solo.

        # Obtener la lista de capítulos para el libro seleccionado
        book_chapters = sorted(combined_df[combined_df['Libro'] == st.session_state.selected_book]['Capítulo'].unique())
        
        # Asegurar que el capítulo seleccionado sea válido para el nuevo libro
        if 'selected_chapter' not in st.session_state or st.session_state.selected_chapter not in book_chapters:
            st.session_state.selected_chapter = book_chapters[0]
        
        # Botones de navegación de capítulos
        current_chapter_index = book_chapters.index(st.session_state.selected_chapter)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Capítulo Anterior", disabled=(current_chapter_index == 0)):
                st.session_state.selected_chapter = book_chapters[current_chapter_index - 1]
                st.rerun()
        with col2:
            if st.button("Capítulo Siguiente", disabled=(current_chapter_index == len(book_chapters) - 1)):
                st.session_state.selected_chapter = book_chapters[current_chapter_index + 1]
                st.rerun()

        # Selectbox para el capítulo
        selected_chapter = st.selectbox(
            "Selecciona un capítulo:",
            book_chapters,
            index=book_chapters.index(st.session_state.selected_chapter)
        )
        if selected_chapter != st.session_state.selected_chapter:
            st.session_state.selected_chapter = selected_chapter
            # No es necesario un st.rerun() aquí.

        # Muestra los versículos
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
                # Se muestra el texto en español siempre
                st.markdown(f"<p style='font-size:{st.session_state.font_size}px;'>{spanish_text.strip()}</p>", unsafe_allow_html=True)

                if found_greek_start:
                    st.markdown(f"<p style='font-size:{st.session_state.font_size}px;'><i>{greek_text.strip()}</i></p>", unsafe_allow_html=True)
                else:
                    st.warning("Al parecer no hay texto griego en este versículo.")
        else:
            st.warning("No se encontraron versículos en este capítulo. Por favor, revisa tu selección.")

    elif mode == "Modo Buscador":
        st.markdown("---")
        st.header("La búsqueda se realizará en todos los Libros o si prefiere, utilice el filtro.")
        
        search_term = st.text_input(
            "Ingresa la secuencia de letras a buscar:",
            placeholder="Ejemplo: σπ o libertad"
        )

        # Usar un expander para ocultar el filtro
        with st.expander("Filtrar la búsqueda de la palabra por Libros:"):
            # Inicializar el estado de los libros si no existe
            if 'book_selection' not in st.session_state:
                st.session_state.book_selection = {book: False for book in BOOKS.keys()}

            # Crear las casillas de selección
            for book_name in BOOKS.keys():
                st.session_state.book_selection[book_name] = st.checkbox(
                    book_name,
                    value=st.session_state.book_selection[book_name],
                    key=f"checkbox_{book_name}"
                )

        st.markdown("---")

        if st.button("Buscar y analizar"):
            if not search_term:
                st.warning("Por favor, ingresa una secuencia de letras a buscar.")
            else:
                # Determinar qué libros buscar
                selected_books_list = [book for book, is_selected in st.session_state.book_selection.items() if is_selected]
                
                # Si no se seleccionó ningún libro, buscar en todos por defecto
                if not selected_books_list:
                    books_to_search = list(BOOKS.keys())
                else:
                    books_to_search = selected_books_list

                try:
                    # Filtra el DataFrame completo según los libros seleccionados
                    filtered_df = combined_df[combined_df['Libro'].isin(books_to_search)]
                    all_occurrences = parse_and_find_occurrences(filtered_df, search_term)
                    
                    if not all_occurrences:
                        st.warning(f"No se encontraron coincidencias que contengan '{search_term}' en los libros seleccionados.")
                    else:
                        st.subheader(f" {len(all_occurrences)} resultados encontrados que contienen '{search_term}':")
                        
                        # Crear un DataFrame para la descarga
                        results_df = pd.DataFrame(all_occurrences)
                        
                        # Renombrar las columnas para que estén en español
                        results_df = results_df.rename(columns={
                            'spanish_text': 'Texto en Español',
                            'greek_text': 'Texto en Griego',
                            'found_word': 'Palabra Encontrada',
                            'language': 'Idioma'
                        })

                        # Convertir el DataFrame a CSV para el botón de descarga
                        csv_data = results_df.to_csv(index=False).encode('utf-8')
                        
                        # Mostrar el botón de descarga
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

