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

    # Widgets para la selección de Libro y Capítulo
    selected_book = st.selectbox("Selecciona un libro:", list(BOOKS.keys()))
    
    # Filtra los capítulos disponibles para el libro seleccionado
    df = all_books_data[selected_book]
    chapters = sorted(df['Capítulo'].unique())
    selected_chapter = st.selectbox("Selecciona un capítulo:", chapters)

    # Muestra los versículos del capítulo seleccionado
    if selected_book and selected_chapter:
        st.markdown("---")
        st.subheader(f"{selected_book} {selected_chapter}")

        # Filtra todas las filas del capítulo seleccionado
        chapter_verses = df[df['Capítulo'] == selected_chapter]

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
                    st.warning("No se pudo separar el texto en español y griego.")
            
        else:
            st.warning("No se encontraron versículos en este capítulo. Por favor, revisa tu selección.")

if __name__ == "__main__":
    main()
