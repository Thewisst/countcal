# Analizador de comida y tracker de calorias

Aplicacion Streamlit que analiza una foto de comida con Gemini, permite agregar contexto y guarda un tracker diario de calorias.

## Requisitos

- Python 3.10 o posterior
- Una clave de Gemini API

## Instalacion local

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y agrega tu clave en `GEMINI_API_KEY`. No subas `.env` a GitHub.

## Ejecutar

```powershell
python -m streamlit run app.py
```

Luego abre `http://localhost:8501`.

## Usarla como app en el celular

La aplicación es responsive y puede instalarse como una app web desde el navegador.

1. Publica la aplicación en Streamlit Community Cloud siguiendo la sección inferior.
2. Abre el enlace público desde el celular.
3. En Android, abre el menú del navegador y selecciona `Instalar aplicación` o `Agregar a pantalla de inicio`.
4. En iPhone, abre el menú de compartir de Safari y selecciona `Agregar a pantalla de inicio`.

Después aparecerá un icono en la pantalla del teléfono y podrás abrir el analizador como una aplicación.

Esta versión conserva el análisis con Gemini, la subida de fotos, el contexto adicional y el tracker diario. Para una app nativa publicada en Play Store o App Store habría que crear además un cliente Android/iOS y un backend seguro para la clave de Gemini.

## Estructura

- `app.py`: aplicación principal.
- `app_cal_count.py`: prototipo CLI anterior.
- `data/`: datos generados localmente por el tracker; se excluyen del repositorio.
- `tmp_uploads/`: imágenes temporales; se excluyen del repositorio.
- `.env.example`: plantilla de variables de entorno.
- `requirements.txt`: dependencias de Python.

## Publicar en Streamlit Community Cloud

1. Sube este proyecto a un repositorio de GitHub.
2. Crea una app nueva en Streamlit Community Cloud y selecciona `app.py` como archivo principal.
3. En la configuración de secrets agrega:

```toml
GEMINI_API_KEY = "tu_clave_de_gemini"
```

No publiques la clave en el código, README ni commits.

