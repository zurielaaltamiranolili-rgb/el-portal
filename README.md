# El Portal de Tlacotalpan

Sitio de noticias con bot automático. Archivos: `index.html`, `logo.jpg`, `noticias.json` (lo escribe el bot) y `bot/actualizar_noticias.py`.

## Publicarlo (gratis, con noticias automáticas)
1. Crea un repositorio en GitHub y sube todo el contenido de esta carpeta (incluida `.github`).
2. En el repo: Settings → Pages → Source: "Deploy from a branch" → rama `main`, carpeta `/ (root)`.
3. En Settings → Actions → General → Workflow permissions: "Read and write permissions".
4. En la pestaña Actions, abre "Actualizar noticias" y pulsa "Run workflow". Después se ejecuta solo cada 3 horas.

## Probar en tu computadora
`python bot/actualizar_noticias.py` y luego `python -m http.server` (abre http://localhost:8000).

## Notas
- El sitio muestra título, resumen corto, imagen y enlace a la nota original (con su fuente).
- Cambia las búsquedas en `CONSULTAS` dentro del script.
- Los formularios del sitio aún no envían correos (se puede conectar a Formspree o similar).
