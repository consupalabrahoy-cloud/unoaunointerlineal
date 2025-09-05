import streamlit as st
import pandas as pd
import requests
import io

@st.cache_data(ttl=3600)
def load_data_from_url(url):
    """
    Función para cargar los datos de una URL pública de Google Sheets (CSV).
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)
            df = df[['Libro', 'Capítulo', 'Versículo', 'Texto']]
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

    # Widgets para la selección de Libro, Capítulo y Versículo
    selected_book = st.selectbox("Selecciona un libro:", list(BOOKS.keys()))
    
    # Maneja el caso en que la carga falle
    if all_books_data[selected_book] is None:
        return

    # Filtra los capítulos y versículos disponibles para el libro seleccionado
    df = all_books_data[selected_book]
    chapters = sorted(df['Capítulo'].unique())
    selected_chapter = st.selectbox("Selecciona un capítulo:", chapters)

    verses = sorted(df[df['Capítulo'] == selected_chapter]['Versículo'].unique())
    selected_verse = st.selectbox("Selecciona un versículo:", verses)

    # Muestra el texto cuando el usuario ha seleccionado todo
    if st.button("Buscar versículo"):
        if selected_book and selected_chapter and selected_verse:
            st.markdown("---")
            st.subheader(f"{selected_book} {selected_chapter}:{selected_verse}")

            # Filtra la fila correcta
            result = df[(df['Capítulo'] == selected_chapter) & (df['Versículo'] == selected_verse)]

            if not result.empty:
                text = result.iloc[0]['Texto']
                lines = text.split('\n')
                
                # Divide el texto en español y griego
                spanish_text = lines[0].strip()
                greek_text = lines[1].strip()

                st.write(spanish_text)
                st.write(greek_text)
            else:
                st.warning("No se encontró el versículo.")

if __name__ == "__main__":
    main()
