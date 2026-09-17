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

## Estructura

- `app.py`: aplicación principal.
- `app_cal_count.py`: prototipo CLI anterior.
- `data/`: datos generados localmente por el tracker; se excluyen del repositorio.
- `tmp_uploads/`: imágenes temporales; se excluyen del repositorio.
- `.env.example`: plantilla de variables de entorno.
- `requirements.txt`: dependencias de Python.
