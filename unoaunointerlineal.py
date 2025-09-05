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
    st.write("Selecciona un libro, capítulo y versículo para ver el texto interlineal.")

    # Diccionario de libros y sus URL públicas
    # REEMPLAZA las URLs de ejemplo con las URL raw de tus archivos CSV en GitHub
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
        "3º de Juan": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/main/Tercera de Juan - Tercera de Juan.csv",
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

    # Widgets para la selección de Libro, Capítulo y Versículo
    selected_book = st.selectbox("Selecciona un libro:", list(BOOKS.keys()))
    
    # Filtra los capítulos y versículos disponibles para el libro seleccionado
    df = all_books_data[selected_book]
    chapters = sorted(df['Capítulo'].unique())
    selected_chapter = st.selectbox("Selecciona un capítulo:", chapters)

    verses = sorted(df[df['Capítulo'] == selected_chapter]['Versículo'].unique())
    selected_verse = st.selectbox("Selecciona un versículo:", verses)

    # Muestra el texto cuando el usuario ha seleccionado todo
    if selected_book and selected_chapter and selected_verse:
        st.markdown("---")
        st.subheader(f"{selected_book} {selected_chapter}:{selected_verse}")

        # Filtra la fila correcta
        result = df[(df['Capítulo'] == selected_chapter) & (df['Versículo'] == selected_verse)]

        if not result.empty:
            full_text = str(result.iloc[0]['Texto'])

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
            
            if found_greek_start:
                st.write(spanish_text.strip())
                st.write(greek_text.strip())
            else:
                st.warning("No se pudo separar el texto en español y griego. Verifica el formato del archivo.")
        else:
            st.warning("No se encontró el versículo. Por favor, revisa tu selección.")

if __name__ == "__main__":
    main()



