import json
import os
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from google import genai

load_dotenv()

st.set_page_config(page_title="Analizador de comida", page_icon="🍽️", layout="centered")

st.markdown(
    """
    <style>
    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 0.75rem 2rem;
        }
        h1 {
            font-size: 1.8rem;
        }
        button, [data-testid="stFileUploader"] section {
            min-height: 3rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)
registro_path = data_dir / "registro_comidas.json"
config_path = data_dir / "config.json"
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".heic",
    ".heif",
}


def es_imagen_aceptada(nombre_archivo: str) -> bool:
    return Path(nombre_archivo).suffix.lower() in IMAGE_EXTENSIONS


def cargar_registros():
    if not registro_path.exists():
        return []
    try:
        with registro_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def guardar_registros(registros):
    with registro_path.open("w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)


def cargar_config():
    if not config_path.exists():
        return {"meta_diaria_kcal": 2000}
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except json.JSONDecodeError:
        pass
    return {"meta_diaria_kcal": 2000}


def guardar_config(config):
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def extraer_calorias(texto):
    try:
        linea = next(line for line in texto.splitlines() if "Calorias estimadas" in line)
        numero = linea.split(":", 1)[1].strip().replace("kcal", "").replace(" ", "")
        return int(float(numero))
    except (StopIteration, ValueError):
        return 0


def obtener_total_por_dia(registros, dia):
    total = 0
    for item in registros:
        if item.get("dia") == dia:
            total += item.get("calorias", 0)
    return total


def crear_registro(resultado, dia_actual):
    lineas = [line.strip() for line in resultado.splitlines() if line.strip()]
    alimento = ""
    porcion = ""
    calorias = 0

    for linea in lineas:
        if linea.startswith("Alimento:"):
            alimento = linea.replace("Alimento:", "").strip()
        elif linea.startswith("Porcion estimada:"):
            porcion = linea.replace("Porcion estimada:", "").strip()
        elif linea.startswith("Calorias estimadas:"):
            calorias = extraer_calorias(resultado)

    return {
        "dia": str(dia_actual),
        "alimento": alimento or "Desconocido",
        "porcion": porcion or "No especificada",
        "calorias": calorias,
        "resultado": resultado,
    }


@st.cache_resource
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        st.error(
            "Falta GEMINI_API_KEY. En local configúrala en .env; "
            "en Streamlit Cloud agrégala en Settings > Secrets."
        )
        st.stop()
    return genai.Client(api_key=api_key)


@st.cache_data
def analizar_imagen(ruta_imagen: str, contexto_extra: str = ""):
    client = get_client()
    model_name = "gemini-3.6-flash"

    prompt = (
        "Eres un nutricionista. Observa la imagen de comida y responde "
        "SOLO con este formato, sin texto adicional:\n"
        "Alimento: <nombre del plato o alimento>\n"
        "Porcion estimada: <cantidad aproximada>\n"
        "Calorias estimadas: <numero> kcal"
    )

    if contexto_extra.strip():
        prompt = (
            f"{prompt}\n\nContexto adicional del usuario:\n{contexto_extra.strip()}"
        )

    img = Image.open(ruta_imagen)
    with img:
        chat = client.chats.create(model=model_name)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        response = chat.send_message([prompt, img])
        return response.text


st.title("🍽️ Analizador de comida")
st.caption("Sube una foto, agrega contexto y sigue tu consumo calórico por día.")

config = cargar_config()
registros = cargar_registros()

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    dia_actual = st.date_input("Selecciona el día:", value=date.today())
with col2:
    meta_diaria = st.number_input(
        "Meta diaria (kcal)",
        min_value=0,
        value=int(config.get("meta_diaria_kcal", 2000)),
        step=50,
    )
with col3:
    total_hoy = obtener_total_por_dia(registros, str(dia_actual))
    st.info(f"Total del día: {total_hoy} kcal")

if meta_diaria != int(config.get("meta_diaria_kcal", 2000)):
    config["meta_diaria_kcal"] = int(meta_diaria)
    guardar_config(config)

uploaded_file = st.file_uploader(
    "Selecciona una imagen",
    type=None,
    help="Acepta JPG, JPEG, PNG, WEBP, BMP, TIFF, GIF y formatos comunes de móvil como HEIC/HEIF.",
)

if uploaded_file is not None:
    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in IMAGE_EXTENSIONS:
        st.error(
            "Formato no soportado. Prueba con una imagen JPG, JPEG, PNG, WEBP, BMP, TIFF, GIF o HEIC/HEIF."
        )
    else:
        temp_dir = Path("./tmp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / uploaded_file.name
        temp_path.write_bytes(uploaded_file.getvalue())

        st.image(str(temp_path), caption="Imagen subida", use_container_width=True)

        usar_contexto = st.checkbox("Agregar texto extra para ayudar a la IA", value=False)
        contexto_extra = ""
        if usar_contexto:
            contexto_extra = st.text_area(
                "Escribe materiales o detalles del plato (opcional):",
                placeholder="Ejemplo: pollo, arroz, aguacate, salsa de tomate, sin queso...",
                height=120,
            )

        if st.button("Analizar comida", type="primary", use_container_width=True):
            with st.spinner("Analizando la imagen..."):
                try:
                    resultado = analizar_imagen(str(temp_path), contexto_extra)
                    st.success("Resultado")
                    st.text(resultado)

                    guardar = st.checkbox(
                        "Guardar esta comida en el tracker del día", value=True
                    )
                    if guardar:
                        nuevo_registro = crear_registro(resultado, dia_actual)
                        registros.append(nuevo_registro)
                        guardar_registros(registros)
                        total_actual = obtener_total_por_dia(registros, str(dia_actual))
                        st.success(f"Comida guardada. Total del día: {total_actual} kcal")
                except Exception as exc:
                    st.error(f"Error: {exc}")

st.subheader("📊 Tracker semanal")

if registros:
    dias = sorted({item["dia"] for item in registros})
    datos = pd.DataFrame(
        [{"dia": dia, "kcal": obtener_total_por_dia(registros, dia)} for dia in dias]
    )
    if not datos.empty:
        st.bar_chart(datos.set_index("dia"))

    st.write("Resumen por día:")
    for dia in dias:
        total = obtener_total_por_dia(registros, dia)
        diferencia = int(config.get("meta_diaria_kcal", 2000)) - total
        st.write(f"**{dia}:** {total} kcal  |  Meta: {config.get('meta_diaria_kcal', 2000)} kcal  |  Diferencia: {diferencia} kcal")
        for item in [r for r in registros if r["dia"] == dia]:
            st.write(f"- {item['alimento']} — {item['calorias']} kcal")
else:
    st.write("Todavía no hay comidas guardadas.")

st.subheader("🗑️ Editar o eliminar comidas guardadas")
if registros:
    opciones = [
        f"{idx + 1}. {item['dia']} - {item['alimento']} ({item['calorias']} kcal)"
        for idx, item in enumerate(registros)
    ]
    seleccion = st.selectbox("Selecciona una comida para editar o borrar", opciones)
    idx_seleccionado = opciones.index(seleccion)

    item_actual = registros[idx_seleccionado]

    with st.form("editar_registro"):
        alimento_edit = st.text_input("Alimento", value=item_actual.get("alimento", ""))
        porcion_edit = st.text_input("Porción", value=item_actual.get("porcion", ""))
        calorias_edit = st.number_input("Calorías", min_value=0, value=int(item_actual.get("calorias", 0)))
        enviado = st.form_submit_button("Guardar cambios")

    if enviado:
        registros[idx_seleccionado]["alimento"] = alimento_edit
        registros[idx_seleccionado]["porcion"] = porcion_edit
        registros[idx_seleccionado]["calorias"] = int(calorias_edit)
        guardar_registros(registros)
        st.success("Comida actualizada.")
        st.rerun()

    if st.button("Eliminar comida seleccionada"):
        registros.pop(idx_seleccionado)
        guardar_registros(registros)
        st.success("Comida eliminada.")
        st.rerun()
else:
    st.write("No hay comidas para editar o borrar.")
