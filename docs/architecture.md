# Whiff architecture (Person A)

_Outline from the playbook. Fill each section as the build progresses._

## 1. Diagram
TODO (S5)

## 2. AWS services and what each does here
- **API Gateway (HTTP API):** public front door; routes `/smoke`, `/day`, `/history`, `/replays`; CORS on.
- **Lambda (Python 3.12):** computes and returns the contract JSON.
- **DynamoDB:** cache of fire clusters and per-city results (TTL). _Planned._
- **EventBridge + Lambda (ingest):** hourly refresh of fire data. _Planned._
- **S3 + CloudFront:** hosts the installable app over HTTPS. _Planned._

## 3. Data sources and credits
- NASA FIRMS (VIIRS active fire detections): attribute NASA FIRMS.
- Open-Meteo (wind and air-quality forecasts): attribution required; free tier is non-commercial. Check terms.

## 4. How the smoke logic works, and its limits
Transparent heuristic, not a dispersion model: fires within 700 km that lie upwind are scored by count, distance and wind alignment; arrival time is distance divided by the wind speed along the route. Uses net (vector-mean) wind at the user's location only; ignores terrain, mixing height, chemistry and rain. Region labels use rough boxes. Thresholds are tunable placeholders to be tuned on replay events.

## 5. Validation results
<!-- validation:start -->
| Event | As-of | Predicted risk | Predicted arrival | Confidence | Actual jump (how found) | Lead if warned | Hit? |
|---|---|---|---|---|---|---|---|
| delhi-2024-10 | 48 h before (Oct 21 12:00) | none | - | medium | Oct 23 12:00 (CPCB date) | | |
| delhi-2024-10 | 36 h before (Oct 22 00:00) | none | - | medium | Oct 23 12:00 (CPCB date) | | |
| delhi-2024-10 | 24 h before (Oct 22 12:00) | none | - | medium | Oct 23 12:00 (CPCB date) | | |
| delhi-2024-10 | 12 h before (Oct 23 00:00) | medium | 40 h | low | Oct 23 12:00 (CPCB date) | | |
| **delhi-2024-10** | **verdict** | | | | | 12 h | **HIT** |
| delhi-2024-11 | 48 h before (Nov 11 12:00) | none | - | medium | Nov 13 12:00 (CPCB date) | | |
| delhi-2024-11 | 36 h before (Nov 12 00:00) | low | 38 h | low | Nov 13 12:00 (CPCB date) | | |
| delhi-2024-11 | 24 h before (Nov 12 12:00) | high | 37 h | low | Nov 13 12:00 (CPCB date) | | |
| delhi-2024-11 | 12 h before (Nov 13 00:00) | low | 29 h | medium | Nov 13 12:00 (CPCB date) | | |
| **delhi-2024-11** | **verdict** | | | | | 24 h | **HIT** |
| lucknow-2023-11 | 48 h before (Nov 02 12:00) | medium | 37 h | low | Nov 04 12:00 (CPCB date) | | |
| lucknow-2023-11 | 36 h before (Nov 03 00:00) | low | 38 h | low | Nov 04 12:00 (CPCB date) | | |
| lucknow-2023-11 | 24 h before (Nov 03 12:00) | low | 35 h | medium | Nov 04 12:00 (CPCB date) | | |
| lucknow-2023-11 | 12 h before (Nov 04 00:00) | low | 35 h | medium | Nov 04 12:00 (CPCB date) | | |
| **lucknow-2023-11** | **verdict** | | | | | 48 h | **HIT** |
| delhi-2024-10-calm | Oct 04 06:00 | none | - | medium | no spike (calm) | - | correct |
| delhi-2024-10-calm | Oct 05 06:00 | none | - | medium | no spike (calm) | - | correct |
| delhi-2024-10-calm | Oct 06 06:00 | none | - | medium | no spike (calm) | - | correct |
| delhi-2024-10-calm | Oct 07 06:00 | low | 31 | medium | no spike (calm) | - | correct |
| delhi-2024-10-calm | Oct 08 06:00 | low | 34 | medium | no spike (calm) | - | correct |
| delhi-2024-10-calm | Oct 09 06:00 | low | 23 | high | no spike (calm) | - | correct |
| delhi-2024-10-calm | Oct 10 06:00 | medium | 45 | low | no spike (calm) | - | FALSE ALARM |
| delhi-2024-10-calm | Oct 11 06:00 | none | - | high | no spike (calm) | - | correct |

- delhi-2024-10: HIT, warned 12 h ahead
- delhi-2024-11: HIT, warned 24 h ahead
- lucknow-2023-11: HIT, warned 48 h ahead
- delhi-2024-10-calm: 1 false alarm(s) in 8 calm mornings

Caveats: archived wind is reanalysis, not a forecast (replays are slightly easier than real life); CAMS is a ~45 km model with 3-hourly steps; very small sample.
<!-- validation:end -->

## 6. Data coverage
<!-- coverage:start -->
| City | Wind ok? | PM2.5 ok? | Notes |
|---|---|---|---|
| Delhi | yes | yes | - |
| Lucknow | yes | yes | - |
| Chandigarh | yes | yes | - |
| Bengaluru | yes | yes | - |
| Chennai | yes | yes | - |
<!-- coverage:end -->

## 7. What we did not build
TODO
