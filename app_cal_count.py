import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

load_dotenv()

IA_PROVIDER = os.getenv("IA_PROVIDER", "gemini").lower()

if IA_PROVIDER == "gemini":
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env. Agrega tu clave gratuita de Google AI Studio.")
    client = genai.Client(api_key=api_key)
    MODEL_NAME = "gemini-3.6-flash"
else:
    raise RuntimeError("Este proyecto está configurado por defecto para la IA gratuita de Gemini. Usa IA_PROVIDER=gemini en .env.")


def buscar_imagen(base_dir: Path, nombre_o_ruta: str):
    ruta = Path(nombre_o_ruta).expanduser()
    if ruta.is_absolute():
        return ruta

    # Primero intenta exacto en la carpeta del proyecto
    candidata = (base_dir / ruta).resolve()
    if candidata.exists():
        return candidata

    # Luego busca imagen por nombre en la carpeta del proyecto
    patrones = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
    for patron in patrones:
        coincidencias = list(base_dir.glob(patron))
        if coincidencias:
            # Si no ingresó nombre, toma la primera imagen disponible
            if not nombre_o_ruta.strip():
                return coincidencias[0]

    return candidata


def analizar_comida(ruta_imagen):
    base_dir = Path(__file__).resolve().parent
    ruta = buscar_imagen(base_dir, ruta_imagen)

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró la imagen: {ruta}. Colócala en la carpeta del proyecto o usa una ruta completa."
        )

    if ruta.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError(f"El archivo no es una imagen válida: {ruta}")

    prompt = (
        "Eres un nutricionista. Observa la imagen de comida y responde "
        "SOLO con este formato, sin texto adicional:\n"
        "Alimento: <nombre del plato o alimento>\n"
        "Porcion estimada: <cantidad aproximada>\n"
        "Calorias estimadas: <numero> kcal"
    )

    with Image.open(ruta) as imagen:
        chat = client.chats.create(model=MODEL_NAME)
        response = chat.send_message([prompt, imagen])
        return response.text


if __name__ == "__main__":
    ruta = input("Ruta de la foto de tu comida (deja vacío para buscar una imagen en la carpeta): ").strip()
    ruta = ruta or ""
    try:
        resultado = analizar_comida(ruta)
        print("\n--- Resultado ---")
        print(resultado)
    except Exception as exc:
        print(f"\nError: {exc}")
        print("Intenta usar una ruta completa como C:/Users/.../mi_comida.jpg o colóca la imagen en la carpeta del proyecto.")