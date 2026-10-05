# SWU Trade Machine

Simulador de tradeos de **Star Wars: Unlimited** entre dos personas, al estilo del Trade Machine de ESPN.

- Buscador con todas las cartas de TCGplayer, con precio Normal y Foil.
- Totales por persona y veredicto de balance (justo / algo desbalanceado / desbalanceado).
- Imágenes de las cartas (hover para agrandar, click/toque para verla en grande).
- USD o CLP con tipo de cambio editable.

## Cómo se actualizan los precios

`.github/workflows/update.yml` corre todos los días a las 21:30 UTC (≈18:30 en Chile):

1. `scripts/update_prices.py` descarga productos y precios de [tcgcsv.com](https://tcgcsv.com) (espejo diario de TCGplayer) y genera `site/data/cards.json`.
2. Publica la carpeta `site/` en GitHub Pages.

Para actualizar a mano: pestaña **Actions → Actualizar precios y publicar → Run workflow**.

## Estructura

```
site/index.html            la app (un solo archivo)
site/data/cards.json       generado por el workflow (no se versiona)
scripts/update_prices.py   descarga de precios
.github/workflows/         tarea diaria + publicación
```
