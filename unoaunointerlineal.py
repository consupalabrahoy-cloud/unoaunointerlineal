import streamlit as st
import pandas as pd
import requests
import io
import re

@st.cache_data(ttl=3600)
def load_data_from_url(url):
    """
    Función para cargar los datos de una URL pública de Google Sheets (CSV)
    y verificar que las columnas necesarias existan.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)

            # Verificación de que las columnas existen
            required_cols = ['Libro', 'Capítulo', 'Versículo', 'Texto']
            if not all(col in df.columns for col in required_cols):
                st.error(f"Error: El archivo CSV no contiene las columnas requeridas. "
                         f"Asegúrate de que los encabezados de tu hoja de cálculo sean: {required_cols}")
                return None
            
            # Filtra las columnas requeridas y convierte los tipos
            df = df[required_cols]
            df['Capítulo'] = pd.to_numeric(df['Capítulo'], errors='coerce').fillna(0).astype(int)
            df['Versículo'] = pd.to_numeric(df['Versículo'], errors='coerce').fillna(0).astype(int)
            return df
        else:
            st.error(f"Error al cargar datos desde la URL. Código de estado: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar el archivo: {e}")
        return None

def main():
    """
    Función principal de la aplicación.
    """
    st.title("Lector Interlineal del Nuevo Testamento 📖")
    st.markdown("---")
    st.write("Selecciona un libro, capítulo y versículo para ver el texto interlineal.")

    # Diccionario de libros y sus URL públicas
    # REEMPLAZA las URLs de ejemplo con las URL reales de tus hojas de cálculo
    BOOKS = {
        "Mateo": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5t_DYgzHVvcbSXJEAcr4YrqaikQKHohfXX6uCAHctZpnTKPuTyAkdr_Os4297BIMp76T-MSw2f2Iu/pub?output=csv",
        "Marcos": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqg4e9BCqwv59ERdSyMfyTJt0Cpxz-dHfY88aOej6o46OEXadXaKuOoQtxuh9OtaRRbfdrdQokMb_e/pub?output=csv",
         "Lucas": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQlBkh2rLp5UyRNnWSlgCe10sMGngxJOdNwHkztDG49pDK03fak4IlJ3pka7CU07qIMEjX0TgiUpDO3/pub?output=csv",
         "Juan":"https://docs.google.com/spreadsheets/d/e/2PACX-1vTIKeJdAPzl_W8fPJAhe1QgmJa23ybBJzNIUtafTsd9kRjr6CnEPSVIMQzTumgOAMb0ZQ2ZlEZe6ZZJ/pub?output=csv",
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
            
            # Encuentra el punto de separación entre español y griego
            # Buscamos el primer carácter griego para dividir
            split_point = re.search(r'[α-ωΑ-Ω]', full_text)
            
            if split_point:
                spanish_text = full_text[:split_point.start()].strip()
                greek_text = full_text[split_point.start():].strip()
                st.write(spanish_text)
                st.write(greek_text)
            else:
                st.warning("No se pudo separar el texto en español y griego. Verifica el formato del archivo.")
        else:
            st.warning("No se encontró el versículo. Por favor, revisa tu selección.")

if __name__ == "__main__":
    main()
