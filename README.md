# Whiff

**Know when the smoke is coming.**

Whiff is an installable web app (PWA) that shows where smoke from crop-residue and other fires is coming from, roughly when it could reach you, and how to plan your day around it. It works for any location in India, in Hindi and English, with Delhi-NCR as the flagship.

|  |  |
|---|---|
| **Live app** | https://x5kcojkqsb.execute-api.ap-south-1.amazonaws.com/ |
| **Demo video** | [Add YouTube link here] |
| **Built for** | WeMakeDevs x AWS Bharat Builds Tour, Environmental Hacks (Air track) |

> General guidance, not medical advice. People with health conditions should follow their doctor's advice.

---

## The problem

Air apps tell you today's AQI. They rarely tell you what is coming or what to do about it. In north India, smoke from fires hundreds of kilometres away can worsen air a day or two later, and most people only find out when it arrives. Whiff answers three plain questions: where is the smoke coming from, when could it reach me, and how should I plan my day.

## What Whiff does

- **Smoke radar:** fire clusters around you, the wind direction, an estimated arrival time with a range, a risk level (none, low, medium, high) and an honest confidence level, drawn on a radar-style screen.
- **Plan my day:** hourly air-quality bars, clean-air windows with activity suggestions, or a stay-in plan on bad days. Advice adapts to who you are: just me, sensitive, with a child, or outdoor worker.
- **Smart streak:** staying indoors on an unhealthy day keeps your streak. Time outdoors is never rewarded.
- **Air Wrapped:** a shareable weekly card with corrective actions.
- **Alerts:** a nudge when your clean-air window opens, or a heads-up on unhealthy days.
- **Replays of real past events:** see how Whiff would have looked during real smoke episodes, using saved data and clearly labelled as a replay.
- **Hindi and English** with a one-tap switch, remembered on your device.
- **Light and dark themes** that follow local sunrise and sunset, or choose manually.
- **Works offline:** the last data you saw stays available, marked as saved.
- **Any place in India:** pick a city or use your location.

## How it works

1. **Fires:** satellite fire detections (NASA FIRMS, VIIRS) from the last 48 hours are grouped into 0.25 degree cells. Only nominal or high confidence detections count.
2. **Wind:** for your location, fire cells within 700 km that lie upwind are kept. The wind is the average of the 10 m and 850 hPa forecast winds over the next 24 hours.
3. **Match:** travel time is distance divided by wind speed. Anything over 48 hours is dropped. The score weights recent fires by closeness and alignment, and sets the risk level.
4. **Arrival and confidence:** arrival is the score-weighted median travel time, with a range from the 25th to 75th percentile. Confidence moves with wind steadiness, the trend in fires, how far away the smoke is, and how fresh the data is.

This is a transparent heuristic, not a smoke-dispersion model. The thresholds were calibrated on the past events below. The full logic and its limits are in [docs/architecture.md](docs/architecture.md).

## Architecture and AWS

- **Hosting:** the app and the API share one HTTPS address. An Amazon API Gateway HTTP API sends `/smoke`, `/day`, `/history` and `/replays` to the API functions, and everything else to a function that serves the built app from a private Amazon S3 bucket.
- **Compute:** AWS Lambda (Python 3.12) runs the smoke and day calculations, the replay list, app serving and an hourly ingest job.
- **Schedule:** Amazon EventBridge runs the ingest job every hour, so most requests make no outside calls.
- **Cache:** Amazon DynamoDB (on-demand) stores fire clusters, per-location results and air-quality series, with fresh-until and cleanup times so an expired copy can still be served as "stale" if a data source is down.
- **Storage:** Amazon S3 holds the built app files (not public).
- **Infrastructure as code:** one AWS SAM / CloudFormation template (`infra/template.yaml`).

Diagram and details: [docs/architecture.md](docs/architecture.md)

## Validation

We ran the same code "as of" 48, 36, 24 and 12 hours before each past spike, hiding any fire detection newer than 3 hours before that moment. A **hit** means a medium or high warning at least 12 hours ahead.

| Event | Result | Warned ahead |
|---|---|---|
| Delhi, October 2024 | Hit | 12 h |
| Delhi, November 2024 | Hit | 24 h |
| Lucknow, November 2023 (limitation example, weak evidence) | Hit | 48 h |
| Delhi calm week, 4 to 11 October 2024 | 1 false alarm in 8 mornings | none |

Read these honestly:

- This is three events and one calm week. It is calibration, not an accuracy claim.
- Most of the warnings carried low confidence, and the November 2024 forecast changed from high to low in the last 12 hours.
- Archived wind is reanalysis, not the forecast that existed at the time, so replays are slightly easier than live use.
- Archived events use two satellites (S-NPP and NOAA-20); live data adds NOAA-21.
- The air-quality model (CAMS, coarse grid, modelled not measured) reads Delhi's worst days far lower than CPCB measurements. Events are therefore graded against CPCB-reported spike days, not against that model.
- A hit means a warning came before a bad day, not that smoke caused it. Calm wind, dust, traffic and firecrackers also drive Delhi's worst days.

Evidence and sources for each event: [docs/validation-events.md](docs/validation-events.md).

## Related tools

Plume Labs' Air Report (hourly air-quality forecasts and clean-air timing advice), Google's Air Quality API (which absorbed BreezoMeter) and the US AirNow Fire and Smoke Map (wildfire smoke direction from fire data) already do parts of this elsewhere. In India, IITM's Decision Support System and the Ministry of Earth Sciences' early-warning system forecast pollution and stubble-fire contributions for policymakers. Whiff differs by focusing on India's crop-residue smoke, giving a plain-language arrival time with a confidence level, working in Hindi and English, and rewarding smart choices with the streak.

## Run it locally

```bash
git clone https://github.com/aashvi0722/Whiff.git
cd Whiff/frontend
npm install
npm run dev
```

Create `frontend/.env.local` (it is git-ignored):

```
VITE_USE_MOCK=false
VITE_API_BASE_URL=https://x5kcojkqsb.execute-api.ap-south-1.amazonaws.com
```

Set `VITE_USE_MOCK=true` to run on the sample files in `/contract` without the API.

Useful test URLs (put the query **before** the `#`):

- `/?replay=delhi-2024-11#/` : replay of a past event (`delhi-2024-10` and `lucknow-2023-11` also work)
- `/?scenario=smoke_high#/` : sample states (`smoke_medium`, `smoke_low`, `smoke_none`, `smoke_stale`, `error`)
- `/?scenario=day_stay_in#/day` : stay-in day (`day_windows`, `day_caution`)
- `/?theme=light#/` or `/?theme=dark#/`

## Repository layout

- `contract/` : the agreed data shapes and sample files shared by the app and the API
- `frontend/` : the PWA (React and Vite)
- `backend/`, `infra/`, `scripts/` : API, AWS setup, validation and tests
- `docs/` : architecture, decisions and validation events

## Limitations

- Smoke arrival is an estimate with a confidence level, not a promise.
- Early in the burning season there are few fires, so live results often show low or no risk. Use the replays to see how Whiff behaves on real past events.
- Wind is taken at your location only, not along the route. There is no terrain, mixing height, chemistry or rain, and all fire detections count, including non-crop fires.
- Hourly AQI is estimated from modelled PM2.5 (CAMS via Open-Meteo) on a coarse grid, so nearby places can differ a lot: on 11 October 2026 two points in Delhi-NCR about 16 km apart returned 66 and 148 µg/m³ for the same hour. It is not a station reading. For ground measurements, see CPCB.
- The cigarette-equivalent figure is Berkeley Earth's rough rule of thumb (about 22 µg/m³ for a day is one cigarette), not a medical measure.
- Alerts appear while Whiff is open or installed on your device. They do not run in the background when the app is closed.
- Open-Meteo's free tier is for non-commercial use, which fits this project. A real service would need a commercial plan.
- Activity check-ins are on the honor system, with no verification.

## Team and AI tools

- **Umang Agarwal** ([@umang3307](https://github.com/umang3307)): app, design, Hindi and English text, demo video
- **Aashvi** ([@aashvi0722](https://github.com/aashvi0722)): data pipeline, API and AWS
- **AI tools used:** Claude (Anthropic) for planning, code drafting, UI and icon design help, documentation and data-source research. The team ran, tested and edited everything submitted.

## Credits

Data, software, fonts and hosting are credited in [CREDITS.md](CREDITS.md).
