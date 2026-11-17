# FORTALEZA SHOP AI

Sistema modular para investigar productos de afiliados, evaluar información comercial y preparar videos verticales en español para México.

## Principios del proyecto

- **Inversión inicial objetivo: $0 MXN.** El flujo predeterminado utiliza plantillas locales, Python y herramientas gratuitas.
- Sin scraping de tiendas ni evasión de restricciones.
- No inventa precios, comisiones, reseñas, ventas ni características.
- No publica automáticamente. Todo contenido requiere revisión humana.
- Solo usa imágenes y videos cuya autorización esté documentada.
- Las funciones que puedan generar cargos permanecen desactivadas por defecto.

## Qué funciona actualmente

| Módulo | Función |
|---|---|
| Product Finder | Importa productos desde JSON o feeds HTTPS que tengas permiso de consultar |
| Product Scorer | Puntúa la calidad de la oportunidad según los datos disponibles |
| Script Generator | Genera guiones en modo gratuito con plantillas; IA externa es opcional y puede tener costo |
| Asset Library | Inventaría imágenes y videos locales y comprueba la autorización declarada |
| Media Pipeline | Prepara un guion y lo relaciona con recursos autorizados |
| Voice Generator | Genera voz en español con Edge TTS; requiere internet |
| Video Generator | Produce MP4 vertical con imágenes y narración disponibles |
| Analytics | Registra e informa datos ingresados manualmente o exportados oficialmente |
| Publishing Manager | Organiza borradores y aprobaciones; no publica automáticamente |

## Instalación

Requiere Python 3.11 o superior.

```bash
git clone https://github.com/z44d2z597w-source/fortaleza-shop-ai.git
cd fortaleza-shop-ai
python -m venv .venv
```

Activar entorno:

- Windows: `.venv\\Scripts\\activate`
- macOS/Linux: `source .venv/bin/activate`

Instalar:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Comandos

```bash
python main.py --check
python main.py --status
python main.py --find-products
python main.py --score-products
python main.py --generate-scripts
python main.py --analytics
python main.py --menu
```

## Catálogo de productos

Importa un archivo JSON con una lista de productos o un objeto con la propiedad `products`. Campos aceptados:

- `name`, `category`, `store`, `seller`
- `price_mxn`, `commission_percent`
- `product_url`, `affiliate_url`, `source_id`

Categorías: `productos_virales`, `hogar`, `tecnologia`, `descubrimientos`.

Para consultar feeds autorizados configura `PRODUCT_FEED_URLS` con URLs HTTPS separadas por punto y coma. No se consulta ninguna tienda automáticamente si no configuras una fuente.

## Imágenes y videos

Los recursos se organizan en `data/product_assets/<product_id>/`. El archivo `authorization.json` debe documentar el permiso del vendedor o de la plataforma con:

```json
{
  "authorized_for_promotion": true,
  "source": "Nombre de la fuente que otorgó el permiso",
  "permission_reference": "Referencia verificable del permiso"
}
```

La declaración no sustituye la verificación de derechos. Sin autorización declarada, los recursos no se consideran utilizables.

## Costos y funciones opcionales

El modo gratuito no necesita clave de OpenAI. La generación por API externa solo puede activarse con `ENABLE_PAID_AI=true` y `OPENAI_API_KEY`; **la API puede generar cargos**. No actives esa opción si quieres mantener el gasto en cero.

Edge TTS requiere conexión a internet y está sujeto a disponibilidad y condiciones del servicio.

TikTok y otras plataformas no se publican automáticamente. La integración oficial y sus autorizaciones aún deben implementarse y probarse. El gestor actual solo prepara borradores para revisión manual.

## Seguridad

- No guardes claves ni tokens en archivos del repositorio.
- Usa variables de entorno o secretos de GitHub.
- No compartas archivos de autorización que contengan información privada.
- Revisa precios, disponibilidad, enlaces y afirmaciones antes de publicar.
- No publiques material sin permiso.
- La rama `main` se verifica con GitHub Actions en cada push y pull request.

## Estado

Versión de desarrollo. El proyecto continúa en construcción; que los tests pasen no significa que todas las integraciones externas estén conectadas ni que las publicaciones estén automatizadas.
