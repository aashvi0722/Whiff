# Credits

Whiff is built on open data, open-source software and open fonts. Thank you to everyone who makes them available.

## Data

| Source | What we use it for | Credit |
|---|---|---|
| **NASA FIRMS** | Satellite active-fire detections (VIIRS: S-NPP, NOAA-20, NOAA-21; the archive for replays has S-NPP and NOAA-20) | We acknowledge the use of data and/or imagery from NASA's Fire Information for Resource Management System (FIRMS), https://earthdata.nasa.gov/firms , part of NASA's Earth Science Data and Information System (ESDIS). |
| **Open-Meteo** | Wind forecasts (10 m and 850 hPa), archived wind, and air-quality data | Weather data by Open-Meteo.com, https://open-meteo.com/ , licensed CC BY 4.0. Used on the free, non-commercial tier. |
| **Copernicus Atmosphere Monitoring Service (CAMS)**, via Open-Meteo | Modelled PM2.5 and PM10 (global model, about 45 km) | Contains modified Copernicus Atmosphere Monitoring Service information. |
| **CPCB** (Central Pollution Control Board, India) | The National AQI categories and PM2.5 / PM10 breakpoints used for AQI bands, and daily Delhi-NCR bulletins used to choose and check past events | https://cpcb.nic.in/ and https://caqm.nic.in/ . Public information, cited as sources. |
| **Berkeley Earth** | The rule of thumb that about 22 µg/m³ of PM2.5 over a day is comparable to one cigarette | https://berkeleyearth.org/air-pollution-and-cigarette-equivalence . A rough comparison, not a medical measure. |
| **IITM / SAFAR estimates**, as printed in CPCB bulletins and news reports | Stubble-burning share figures quoted in the validation notes | Quoted with their source for context only. Estimates differ between sources. |

News and government sources for each validation event are linked in [docs/validation-events.md](docs/validation-events.md).

## Software (frontend)

| Library | Version | Licence |
|---|---|---|
| React and React DOM | 19 | MIT |
| React Router | 7 | MIT |
| html-to-image (Air Wrapped share card) | 1.11 | MIT |
| Vite and @vitejs/plugin-react | 8 and 6 | MIT |
| vite-plugin-pwa (uses Workbox) | 2 | MIT |
| ESLint and its React plugins (development only) | | MIT |

Exact versions are in `frontend/package.json` and `frontend/package-lock.json`. Backend tools are listed in the backend files.

## Fonts

| Font | Packaged by | Licence |
|---|---|---|
| Montserrat | Fontsource | SIL Open Font License 1.1 |
| Noto Sans Devanagari | Fontsource | SIL Open Font License 1.1 |

Both fonts are bundled with the app, not loaded from a font server.

## Icons, logo and design

All icons, the logo and the radar are SVG or PNG artwork drawn for this project. The glass-style look was inspired by public design references (pastel and glassmorphism app designs, weather icon sets). No artwork from those references was copied or used.

## AI tools

Claude (Anthropic) was used for planning, drafting code, UI, icon and logo design help, writing documentation, drafting Hindi text and researching data sources. The team ran, tested and edited everything, and takes responsibility for what is submitted.

## Hosting

Amazon Web Services: API Gateway (HTTP API), AWS Lambda, Amazon EventBridge, Amazon DynamoDB, Amazon S3, and AWS SAM / CloudFormation for deployment. Details are in [docs/architecture.md](docs/architecture.md).
