# Whiff data contract (v1)

Frozen at S0. Both sides build against these files. **If code and a sample disagree, the sample is right.**
All values in the samples are **illustrative**, not real measurements.

## Rules
- Every response has `contract_version`. Adding a field is safe; removing or renaming one bumps the version.
- Times are Asia/Kolkata ISO strings. Hours are integers 0-23.
- The backend sends **reason codes + params**, never user-facing sentences. B maps every code to English and Hindi.
- Change process: message the other person, wait for "yes", change sample + code in one commit, post it in the Decisions message.

## Endpoints and sample files
| Call | Sample file(s) |
|---|---|
| `GET /smoke?lat&lon` (+ `&replay=id`) | `smoke_high`, `smoke_medium`, `smoke_low`, `smoke_none`, `smoke_stale`, `smoke_replay` |
| `GET /day?lat&lon&audience=general\|sensitive\|child\|outdoor` (+ `wake_h`, `replay`) | `day_windows`, `day_caution`, `day_stay_in` |
| `GET /history?lat&lon&days=7` | `history` |
| `GET /replays` | `replays` |
| any error (HTTP 502/503) | `error` |

## `?scenario=` switch (stub and real API)
`smoke_high`, `smoke_medium`, `smoke_low`, `smoke_none`, `smoke_stale`, `smoke_replay`, `day_windows`, `day_caution`, `day_stay_in`, `history`, `replays`, `error`
returns the file `<scenario>.sample.json`.

## Field notes (decisions made while writing the samples)
- `sources[].bearing_deg`: compass bearing **from the user toward the fire cluster** (0 = north). This is where B draws the dot on the radar. When smoke is aligned it is close to `wind.from_deg`. The smoke arrow points at `wind.from_deg + 180`.
- `replay.label_key` (not a free-text label): B owns all wording.
- `location.label`: the English city name from `backend/config/cities.json`; B may map it to Hindi.
- `/day` additions to the original draft: top-level `reason_codes` (best_hour, worst_hour, all_day_poor) and `aqi_is_estimate: true` (hourly AQI is an estimate; label it "estimated").
- `/day` summary fields (`best_hour`, `worst_hour`, `day_avg_pm25`, `exposure_avoided_hours`, windows) use **active hours 5-21**; `hours[]` extends to 22 for display.
- `day_state: "windows"` => `windows` non-empty. `caution` => `windows` empty, use `best_hour`. `stay_in` => `windows` empty, every active hour is "stay".
- `cigarette_equiv` is always `approx: true`.
- Replay event ids in `replays.sample.json` are **placeholders** until `docs/validation-events.md` fixes the real events.

## Check before every sync
`python3 scripts/check_contract.py`
