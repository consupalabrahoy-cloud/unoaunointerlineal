import streamlit as st
import pandas as pd
import requests
import io

@st.cache_data(ttl=3600)
def load_data_from_url(url):
    """
    Función para cargar los datos de un archivo CSV desde una URL pública de GitHub.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza una excepción para errores HTTP

        # Usa pandas para leer el archivo CSV directamente desde el contenido
        text_content = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(text_content), sep=',')
        
        # Convierte las columnas a tipos de datos correctos
        df['Capítulo'] = pd.to_numeric(df['Capítulo'], errors='coerce').fillna(0).astype(int)
        df['Versículo'] = pd.to_numeric(df['Versículo'], errors='coerce').fillna(0).astype(int)

        if df.empty:
            st.error("Error: El archivo de texto está vacío o tiene un formato incorrecto.")
            return None
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Error al cargar datos desde la URL: {e}")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al procesar el archivo: {e}. Por favor, verifica el formato.")
        return None

def main():
    """
    Función principal de la aplicación.
    """
    st.title("Lector Interlineal del Nuevo Testamento. Reina-Valera Antigua y Westcott-Hort")
    st.markdown("---")
    st.write("Selecciona un libro y un capítulo para ver el texto interlineal.")

    # Diccionario de libros y sus URL públicas
    # REEMPLAZA las URLs con las URL raw de tus archivos CSV en GitHub
    BOOKS = {
        "Mateo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Mateo - Mateo.csv",
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
        "2º a los Tesalonicenses": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda a Tesalonicenses - Segunda a Tesalonicenses.csv",
        "1º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera a Timoteo - Primera a Timoteo.csv",
        "2º a Timoteo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda a Timoteo - Segunda a Timoteo.csv",
        "Tito": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Tito - Tito.csv",
        "Filemón": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Filemón - Filemón.csv",
        "Hebreos": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Hebreos - Hebreos.csv",
        "Santiago": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera de Pedro - Primera de Pedro.csv",
        "1º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Santiago - Santiago.csv",
        "2º de Pedro": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda de Pedro - Segunda de Pedro.csv",
        "1º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Primera de Juan - Primera de Juan.csv",
        "2º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Segunda de Juan - Segunda de Juan.csv",
        "3º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/refs/heads/main/Tercera%20de%20Juan%20-%20Tercera%20de%20Juan.csv",
        "Judas": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Judas - Judas.csv",
        "Apocalipsis": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Apocalipsis - Apocalipsis.csv",
    }
    # Carga todos los datos de los libros
    all_books_data = {}
    for book_name, url in BOOKS.items():
        all_books_data[book_name] = load_data_from_url(url)
    
    # Maneja el caso en que la carga falle
    if not all_books_data or any(data is None for data in all_books_data.values()):
        return

    # Inicializa el estado de la sesión si no existe
    if 'selected_book' not in st.session_state:
        st.session_state.selected_book = list(BOOKS.keys())[0]
    if 'selected_chapter' not in st.session_state:
        # Obtiene el primer capítulo del primer libro por defecto
        first_book_df = all_books_data[st.session_state.selected_book]
        if not first_book_df.empty:
            first_chapter = sorted(first_book_df['Capítulo'].unique())[0]
            st.session_state.selected_chapter = first_chapter
        else:
            st.session_state.selected_chapter = 1

    # Selector de libro
    selected_book = st.selectbox("Selecciona un libro:", list(BOOKS.keys()), index=list(BOOKS.keys()).index(st.session_state.selected_book))
    if selected_book != st.session_state.selected_book:
        st.session_state.selected_book = selected_book
        # Reinicia el capítulo al cambiar de libro
        new_book_df = all_books_data[selected_book]
        if not new_book_df.empty:
            first_chapter = sorted(new_book_df['Capítulo'].unique())[0]
            st.session_state.selected_chapter = first_chapter
        else:
            st.session_state.selected_chapter = 1
        st.rerun()

    # Obtiene los capítulos del libro seleccionado
    df = all_books_data[st.session_state.selected_book]
    chapters = sorted(df['Capítulo'].unique())
    
    # Maneja la selección de capítulo desde el menú desplegable
    try:
        current_chapter_index = chapters.index(st.session_state.selected_chapter)
    except ValueError:
        # Si el capítulo guardado no existe en el nuevo libro, vuelve al primer capítulo
        current_chapter_index = 0
        st.session_state.selected_chapter = chapters[0]

    # Botones de navegación de capítulos
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Capítulo Anterior", disabled=(current_chapter_index == 0)):
            st.session_state.selected_chapter = chapters[current_chapter_index - 1]
            st.rerun()
    with col2:
        if st.button("Capítulo Siguiente", disabled=(current_chapter_index == len(chapters) - 1)):
            st.session_state.selected_chapter = chapters[current_chapter_index + 1]
            st.rerun()

    # Selector de capítulo
    selected_chapter = st.selectbox(
        "Selecciona un capítulo:",
        chapters,
        index=chapters.index(st.session_state.selected_chapter)
    )
    if selected_chapter != st.session_state.selected_chapter:
        st.session_state.selected_chapter = selected_chapter
        st.rerun()

    # Muestra los versículos del capítulo seleccionado
    if st.session_state.selected_book and st.session_state.selected_chapter:
        st.markdown("---")
        st.subheader(f"{st.session_state.selected_book} {st.session_state.selected_chapter}")

        # Filtra todas las filas del capítulo seleccionado
        chapter_verses = df[df['Capítulo'] == st.session_state.selected_chapter]

        if not chapter_verses.empty:
            for index, row in chapter_verses.iterrows():
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
                
                # Muestra cada versículo
                st.markdown(f"**Versículo {verse_number}**")
                if found_greek_start:
                    st.write(spanish_text.strip())
                    st.write(greek_text.strip())
                else:
                    st.warning("No se pudo separar el texto en español y griego. Verifica el formato del archivo.")
            
        else:
            st.warning("No se encontraron versículos en este capítulo. Por favor, revisa tu selección.")

if __name__ == "__main__":
    main()
