import streamlit as st
import pandas as pd
import requests
import io
import re

@st.cache_data(ttl=3600)
def load_data_from_url(url):
    """
    Función para cargar los datos de una URL pública de GitHub.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza una excepción para errores HTTP
        
        # Lee el contenido del archivo como texto
        text_content = response.text
        
        # Procesa el texto para crear un DataFrame
        lines = text_content.strip().split('\n')
        data = []
        for line in lines:
            parts = line.split(',', 3)
            if len(parts) == 4:
                # La columna 'Texto' contiene tanto español como griego
                data.append(parts)
        
        df = pd.DataFrame(data, columns=['Libro', 'Capítulo', 'Versículo', 'Texto'])
        
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
        st.error(f"Ocurrió un error inesperado al procesar el archivo: {e}")
        return None

def main():
    """
    Función principal de la aplicación.
    """
    st.title("Lector Interlineal del Nuevo Testamento 📖")
    st.markdown("---")
    st.write("Selecciona un libro, capítulo y versículo para ver el texto interlineal.")

    # Diccionario de libros y sus URL públicas
    # REEMPLAZA las URLs de ejemplo con las URL raw de tus archivos de texto en GitHub
    BOOKS = {
        "Mateo": "https://raw.githubusercontent.com/consupalabrahoy-cloud/unoaunointerlineal/refs/main/Mateo.txt",
        # Agrega el resto de los libros y sus URLs aquí
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

