# Whiff

**Know when the smoke is coming.**

Whiff is an installable web app (PWA) that shows where smoke from crop-residue and other fires is coming from, roughly when it could reach you, and how to plan your day around it. It works anywhere in India, in Hindi and English.

**Live app:** https://x5kcojkqsb.execute-api.ap-south-1.amazonaws.com/
**Demo video:** [B: paste YouTube link]
**Built for:** Bharat Builds Tour, Environmental Hacks (Air track), by a team of two.

> General guidance, not medical advice. People with health conditions should follow their doctor's advice.

---

## The problem

Air apps tell you today's AQI. They rarely tell you what is coming or what to do about it. In north India, smoke from fires hundreds of kilometres away can raise pollution a day or two later, and most people only find out when it arrives. India's official systems (for example IITM's Decision Support System for Delhi) forecast pollution for policymakers; Whiff is aimed at ordinary people, schools and workers, in plain language.

## What Whiff does

- **Smoke radar:** fire clusters around you, the wind direction, an estimated arrival time with a range, a risk level (none, low, medium, high) and an honest confidence level.
- **Plan my day:** hourly air-quality bars, clean-air windows and what to do in them, or a stay-in plan on bad days. Advice adapts to who you are (just me, sensitive, with a child, outdoor worker).
- **Hindi and English:** one-tap language switch, remembered on your device.
- **Light and dark themes:** follows local sunrise and sunset, or choose manually.
- **Replays of real past events:** see how Whiff would have looked during real smoke episodes (saved data, clearly labelled).
- **Works offline:** the last data you saw stays available, marked as saved.

### Status (update before submitting)

| Feature | Status |
|---|---|
| Smoke radar, risk, arrival range, confidence | Built |
| Plan my day, audience-aware advice | Built |
| Profile, city and location | Built |
| Hindi / English, light / dark themes, installable PWA | Built |
| Replays of past events | [B: confirm after deploy] |
| Smart streak (staying in on a bad day counts) | [B: built / in progress / not built] |
| Air Wrapped shareable card | [B: built / not built] |
| Damage report (worst day and likely cause) | [A/B: confirm] |

## How it works (plain language)

1. **Fires:** satellite fire detections (NASA FIRMS) are fetched and grouped into clusters.
2. **Wind:** the wind forecast for your location says which way smoke would travel.
3. **Match:** fire clusters upwind of you, and how fast the wind could carry smoke over that distance, give a risk level and an arrival range.
4. **Confidence:** lower when the wind keeps changing, the fire data is old, or the smoke is far away.

This is a transparent heuristic, not a full smoke-dispersion model.

## Architecture and AWS

[A: fill in and keep it accurate. Suggested structure:]

- Hosting: [A: what serves the app, and the note that the app and API share one HTTPS address because CloudFront was blocked on the new account]
- API: [A: API Gateway + Lambda routes /smoke, /day, /history, /replays]
- Scheduled refresh: [A: EventBridge, if used]
- Cache: [A: DynamoDB, if used]
- Diagram: [A: link to docs/architecture.md]

## Validation

[A: paste the final numbers. Keep it honest.]

- Events tested: [A]
- Hits / misses / false alarms on the calm period: [A]
- Small sample: this is a handful of events, not an accuracy claim.
- Archived events use two satellites (S-NPP and NOAA-20), not three.
- Archived wind is real observed wind, not a forecast, so replays are slightly easier than live use.
- The model we compare against (CAMS) reads Delhi's peak PM2.5 much lower than CPCB measurements, so November events are graded against CPCB dates; October against 23 Oct.
- One replay (Lucknow, Nov 2023) is a **limitation example** with weak evidence, shown on purpose.

## Run it locally

```bash
git clone https://github.com/aashvi0722/Whiff.git
cd Whiff/frontend
npm install
npm run dev
```

Create `frontend/.env.local`:

```
VITE_USE_MOCK=false
VITE_API_BASE_URL=https://x5kcojkqsb.execute-api.ap-south-1.amazonaws.com
```

Set `VITE_USE_MOCK=true` to run on the sample files in `/contract` without the API.

Useful test URLs (put the query **before** the `#`):

- `/?replay=delhi-2024-11#/` : replay of a past event
- `/?scenario=smoke_high#/` : sample states (`smoke_none`, `smoke_stale`, `error`, ...)
- `/?scenario=day_stay_in#/day`
- `/?theme=light#/` or `?theme=dark`

Backend and deployment: see `backend/`, `infra/` and `docs/architecture.md`. [A: add the exact deploy commands.]

## Repository layout

- `contract/` : the agreed data shapes and sample files shared by the app and the API
- `frontend/` : the PWA (React + Vite)
- `backend/`, `infra/`, `scripts/` : API, AWS setup and tools
- `docs/` : architecture notes and validation events

## Limitations (honestly)

- Smoke arrival is an estimate with a confidence level, not a promise.
- Early in the burning season there are few fires, so live results often show low or no risk.
- Hourly AQI shown for planning is estimated from forecast PM2.5.
- The cigarette-equivalent figure is a rough comparison, not a medical measure.
- Activity check-ins are on the honor system; there is no verification.

## Team and AI tools

- **Person A:** data, API and AWS
- **Person B:** app, design, Hindi/English, video
- **AI tools used:** Claude (Anthropic) for planning, code drafting, documentation and data-source research. All code was run, tested and edited by the team.

## Credits

See [CREDITS.md](CREDITS.md).
