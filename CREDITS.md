# Credits

Whiff is built on open data, open-source software and open fonts. Thank you to everyone who makes them available.

> **Before submitting:** the wording and licence terms below are my best understanding. Open each link and confirm the required attribution text. Items marked **[verify]** are the ones to check.

## Data

| Source | What we use it for | Attribution / licence |
|---|---|---|
| **NASA FIRMS** (Fire Information for Resource Management System, part of NASA's Earth Science Data and Information System) | Satellite fire detections (VIIRS) | Data and imagery from NASA FIRMS, https://firms.modaps.eosdis.nasa.gov/ . **[verify exact acknowledgement wording on the FIRMS site]** |
| **Open-Meteo** | Wind and air-quality forecasts, and archived weather | Weather data by Open-Meteo.com, https://open-meteo.com/ , licensed CC BY 4.0. **[verify the free tier is allowed for our use and the required wording]** |
| **CAMS** (Copernicus Atmosphere Monitoring Service), via Open-Meteo | Air-quality model data and archives | Contains Copernicus Atmosphere Monitoring Service information. **[verify required wording on the Open-Meteo / Copernicus licence pages]** |
| **CPCB** (Central Pollution Control Board, India) | Daily Delhi-NCR air-quality bulletins used to choose and check past events | https://cpcb.nic.in/ . Public bulletins, cited as sources. **[verify terms of use for government data]** |
| **IITM / SAFAR estimates**, as printed in CPCB bulletins and news reports | Stubble-burning share figures quoted in validation notes | Quoted with their source for context only; estimates differ between sources. |

Supporting news and government sources for the validation events are linked in `docs/validation-events.md`.

## Software

| Library | Licence |
|---|---|
| React, React DOM | MIT |
| React Router | MIT |
| Vite | MIT |
| vite-plugin-pwa (with Workbox) | MIT |
| html-to-image (if used for the share card) | **[verify licence and that it was installed]** |

The full list, with exact versions, is in `frontend/package.json` and `frontend/package-lock.json`.

## Fonts

| Font | Licence |
|---|---|
| Montserrat, via Fontsource | SIL Open Font License 1.1 |
| Noto Sans Devanagari, via Fontsource | SIL Open Font License 1.1 |

## Icons and graphics

All icons are simple inline SVG drawn for this project. [B: update if any external icon set is added.]

## AI tools

Claude (Anthropic) was used for planning, drafting code, documentation and researching data sources. The team ran, tested, edited and takes responsibility for everything submitted.

## Hosting

Amazon Web Services. [A: list the services actually used.]
