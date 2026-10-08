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
TODO (S4)

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
