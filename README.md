# Demo educativa — Recolección de datos vía link (Ciberseguridad)

Proyecto para evaluación controlada: demuestra cómo un link recolecta datos
**pasivos** (headers HTTP automáticos) y **activos** (JavaScript + APIs del
navegador, con consentimiento para datos sensibles como geolocalización).

## Estructura
```
link-datalogger/
├── app.py                 # servidor Flask
├── templates/
│   ├── index.html          # página que ve quien abre el link
│   └── dashboard.html      # vista para ver lo capturado
├── requirements.txt
└── README.md
```

## Probar en tu máquina (local)
```bash
cd link-datalogger
pip install -r requirements.txt
python app.py
```
Abre `http://localhost:5000` → acepta → revisa `http://localhost:5000/dashboard`.

## Subir a GitHub
```bash
cd link-datalogger
git init
git add .
git commit -m "Demo ciberseguridad - recolección de datos vía link"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/link-datalogger.git
git push -u origin main
```

## Desplegar en Render
1. Entra a render.com → New → Web Service.
2. Conecta tu cuenta de GitHub y selecciona el repo `link-datalogger`.
3. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Deploy. Render te da una URL tipo `https://link-datalogger.onrender.com`.
5. Ese es el link que compartes. Los resultados los ves en `/dashboard`.

## Antes de tu presentación
- Abre el link tú mismo unos minutos antes para "despertar" el servidor (evita el cold start).
- Ten screenshots del dashboard funcionando por si acaso.

## Nota ética
Este proyecto es para un entorno de evaluación controlado, con consentimiento
de quienes abren el link (tu profesor/compañeros informados de que es parte
de la práctica). No está pensado para usarse contra terceros sin su conocimiento.
