
# FORTALEZA SHOP AI 🚀

### Sistema inteligente de automatización comercial y marketing de afiliados

---

## 1. DESCRIPCIÓN

FORTALEZA SHOP AI es un proyecto independiente diseñado para automatizar la creación de contenido comercial para productos de afiliados.

Su objetivo es descubrir oportunidades comerciales, seleccionar productos, generar guiones, producir videos verticales, gestionar enlaces de afiliados y analizar resultados.

Mercado inicial: México.

Idioma: Español.

Formato: Videos verticales 9:16.

Duración objetivo: 15 a 45 segundos.

---

## 2. CATEGORÍAS

El sistema trabajará con cuatro categorías:

1. Productos virales.
2. Hogar y cocina.
3. Tecnología y gadgets.
4. Descubrimientos y ofertas.

---

## 3. ARQUITECTURA

El sistema estará dividido en módulos independientes.

| Módulo | Función |
|---|---|
| PRODUCT FINDER | Encontrar productos |
| PRODUCT SCORER | Evaluar oportunidades |
| AI SCRIPT | Crear guiones |
| VIDEO MAKER | Producir videos |
| VOICE ENGINE | Generar narraciones |
| PUBLISHER | Publicar contenido |
| ANALYTICS | Medir resultados |

---

## 4. TECNOLOGÍAS

- Python
- GitHub
- GitHub Actions
- OpenAI API
- FFmpeg
- MoviePy
- Edge-TTS
- TikTok Content Posting API
- JSON y CSV

---

## 5. MODOS DE OPERACIÓN

### TEST

Genera contenido y realiza pruebas sin publicar.

### REVIEW

Prepara videos para revisión y aprobación manual.

### AUTO

Publica mediante integraciones oficiales autorizadas.

La publicación automática permanecerá desactivada hasta completar las autorizaciones necesarias.

---

## 6. ESTRUCTURA DEL PROYECTO

```text
fortaleza-shop-ai/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── core/
│   ├── product_finder.py
│   ├── product_scorer.py
│   ├── script_generator.py
│   ├── video_generator.py
│   ├── voice_generator.py
│   ├── publisher.py
│   └── analytics.py
│
├── data/
│   ├── products.csv
│   ├── published.json
│   └── analytics.json
│
├── templates/
│   └── commercial_prompt.txt
│
├── output/
│
├── logs/
│
└── .github/
    └── workflows/
        └── daily.yml
```

---

## 7. INSTALACIÓN

Clonar el repositorio:

```bash
git clone https://github.com/TU_USUARIO/fortaleza-shop-ai.git

cd fortaleza-shop-ai
```

Crear entorno virtual:

```bash
python -m venv venv
```

Activar en Windows:

```bash
venv\Scripts\activate
```

Activar en Linux o macOS:

```bash
source venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## 8. EJECUCIÓN

Verificar el proyecto:

```bash
python main.py --check
```

Consultar estado:

```bash
python main.py --status
```

Consultar información:

```bash
python main.py --info
```

Abrir menú:

```bash
python main.py --menu
```

---

## 9. VARIABLES DE ENTORNO

Las credenciales se configurarán mediante variables de entorno o secretos de GitHub.

| Variable | Función |
|---|---|
| OPENAI_API_KEY | Inteligencia artificial |
| OPENAI_MODEL | Modelo de IA |
| PUBLISH_MODE | Modo de operación |
| TIKTOK_CLIENT_KEY | Aplicación TikTok |
| TIKTOK_CLIENT_SECRET | Seguridad |
| TIKTOK_ACCESS_TOKEN | Autorización |
| TIKTOK_OPEN_ID | Identificador |
| VIDEO_STORAGE_URL | Almacenamiento externo |

Nunca guardar credenciales directamente en el código.

---

## 10. AUTOMATIZACIÓN

Horario objetivo:

| Hora México | Actividad |
|---|---|
| 07:00 | Buscar productos |
| 07:15 | Evaluar oportunidades |
| 07:30 | Crear guiones |
| 07:45 | Generar videos |
| 08:15 | Preparar publicaciones |
| 21:00 | Registrar estadísticas |

Los horarios son configurables y dependen de que las integraciones estén disponibles.

---

## 11. REGLAS DE SEGURIDAD

- No inventar precios.
- No inventar comisiones.
- No utilizar enlaces falsos.
- No repetir publicaciones.
- No publicar videos defectuosos.
- No utilizar contenido protegido sin autorización.
- Conservar historial de operaciones.
- Proteger las credenciales.
- Respetar las políticas de las plataformas.
- Detener operaciones ante errores críticos.

---

## 12. AFILIADOS

El catálogo registrará:

- Nombre del producto.
- Categoría.
- Tienda.
- Vendedor.
- Precio verificado.
- Comisión.
- Enlace afiliado.
- Fecha de revisión.
- Videos relacionados.
- Conversiones.
- Ganancias.

Los enlaces y las comisiones deberán proceder de fuentes oficiales de afiliación.

---

## 13. OBJETIVO FINAL

Construir una operación comercial automatizada capaz de:

1. Encontrar productos atractivos.
2. Seleccionar oportunidades rentables.
3. Generar videos originales.
4. Gestionar enlaces de afiliados.
5. Publicar contenido autorizado.
6. Medir resultados.
7. Optimizar futuras publicaciones.

---

## ESTADO DEL PROYECTO

**Nombre:** FORTALEZA SHOP AI

**Versión:** 1.0.0

**Mercado:** México

**Modo inicial:** TEST

**Publicación automática:** Desactivada

**Estado:** En construcción.

---

Proyecto independiente de FORTALEZA MEDIA AI.
