# validation-events.md

Prepared by Person B for Person A's validation run. Last checked: Fri 9 Oct 2026.

**Rule used:** every number below was read from the linked source during this check, nothing is from memory. Where I could not confirm something, it says so in Notes.
**Format:** your table columns, plus a short `Label` for the label key. **Level:** PM2.5 in µg/m3 when the source gives it (CPCB daily average, 06:00 to 06:00), otherwise AQI plus category. CPCB AQI = 24-hour average at 4 PM.
**Data range:** all events are inside your archive range (Oct 2022 to end 2025). 2024 events have all three satellites.

---

## 1. The events (3 smoke + 1 calm, as you asked)

| # | City | Dates (YYYY-MM-DD) | Spike observed | Likely cause (as stated by the source) | Source link | Season | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Delhi | 2024-10-20 to 2024-10-23 | 23 Oct: **AQI 364, Very Poor** (up from 277 on 20 Oct). PM2.5 on 22 Oct: **188 µg/m3** (PM10 347) | IITM put stubble burning at about 8.0% of PM2.5 on 22 Oct. CPCB lists PM2.5 and PM10 as prominent on 23 Oct (PM10 alone on 22 Oct). Wind forecast for 24 Oct: NNW/N 6 to 12 km/h | [CPCB 20 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-20102024.pdf), [21 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-21102024.pdf), [22 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-22102024.pdf), [23 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-23102024.pdf) | early | **Few-fires case.** Punjab had only 71 fire events on 22 Oct (1,581 since 15 Sep), Haryana 10 (665). Smoke share was small and PM10 (dust) was prominent, so the right answer is probably low or medium risk, and a loud "high" would be an over-call. Also a partial **limitation example**. Label: `Delhi, October 2024` |
| 2 | Delhi | 2024-11-10 to 2024-11-18 | First severe day **13 Nov: AQI 418**, then 14 Nov **424**. Peak **18 Nov: AQI 494, PM2.5 454 µg/m3** (17 Nov daily mean). 19 Nov: AQI 460, PM2.5 594 (18 Nov daily mean) | IITM stubble share about 15% (10 Nov), 18% (11 to 12 Nov), then 31% (13 Nov), 33% (14 Nov), 38% (15 Nov), 13% (17 Nov), 20% (18 Nov). IMD wind forecast **NW** on 13 to 15 Nov. IITM forecast Severe for 19 to 22 Nov | [CPCB 11 Nov](https://cpcb.nic.in/uploads/AQM/AQ-NCR-11112024.pdf), [12](https://cpcb.nic.in/uploads/AQM/AQ-NCR-12112024.pdf), [13](https://cpcb.nic.in/uploads/AQM/AQ-NCR-13112024.pdf), [14](https://cpcb.nic.in/uploads/AQM/AQ-NCR-14112024.pdf), [15](https://cpcb.nic.in/uploads/AQM/AQ-NCR-15112024.pdf), [16](https://cpcb.nic.in/uploads/AQM/AQ-NCR-16112024.pdf), [18](https://cpcb.nic.in/uploads/AQM/AQ-NCR-18112024.pdf), [19 Nov](https://cpcb.nic.in/uploads/AQM/AQ-NCR-19112024.pdf) | peak | **Best smoke-arrival case.** Clear wave 1 (13 to 14 Nov) with the share rising and NW wind, wave 2 (17 to 18 Nov) with more fires: Punjab 404 fire events on 17 Nov (8,404 since 15 Sep), 238 on 15 Nov. IITM **revised** the 13 to 15 Nov shares (see 19 Nov bulletin), treat them as a range. Share fell on 17 Nov while AQI kept rising, so weather and local sources mattered. Label: `Delhi, November 2024` |
| 3 | Lucknow | 2023-11-01 to 2023-11-05 | Weekend of 4 to 5 Nov: **AQI 274, Poor** (CPCB). Jumped **88 points in one day**. Before that, Lucknow had only 2 Poor days in all of October (29 and 30 Oct) | The IANS report describes haze and falling temperatures. It **does not name stubble smoke** as the cause | [IANS, 6 Nov 2023](https://ianslive.in/after-noise-pollution-lucknow-suffers-air-pollution--20231106143606) | peak (start) | **Weaker evidence, flag it.** Smoke link is an inference: Delhi was also Very Poor and rising at the same time (CPCB 1 Nov 2023: 364; 6 Nov: 421 Severe; 8 Nov: 426, from the prior-year columns of the [1 Nov 2024](https://cpcb.nic.in/uploads/AQM/AQ-NCR-01112024.pdf), [6 Nov 2024](https://cpcb.nic.in/uploads/AQM/AQ-NCR-06112024.pdf) and [8 Nov 2024](https://cpcb.nic.in/uploads/AQM/AQ-NCR-08112024.pdf) bulletins). The article does not say which day was 274. Please confirm with Open-Meteo PM2.5 and FIRMS fires upwind (Punjab/Haryana/west UP), and if it does not show a smoke pattern, use it as a **limitation example**. Label: `Lucknow, November 2023` |
| 4 | Delhi | 2024-10-04 to 2024-10-11 (calm) | **No spike.** AQI **126 to 167, Moderate** every day I could read. PM2.5 **41 to 63 µg/m3** | Not a pollution event. IITM forecast Moderate for these days, and CPCB's prominent pollutant on most days was PM10 | [CPCB 5 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-05102024.pdf), [6](https://cpcb.nic.in/uploads/AQM/AQ-NCR-06102024.pdf), [7](https://cpcb.nic.in/uploads/AQM/AQ-NCR-07102024.pdf), [8](https://cpcb.nic.in/uploads/AQM/AQ-NCR-08102024.pdf), [10](https://cpcb.nic.in/uploads/AQM/AQ-NCR-10102024.pdf), [11](https://cpcb.nic.in/uploads/AQM/AQ-NCR-11102024.pdf), [12 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-12102024.pdf) | early | **False-alarm test during fire season.** Punjab fire events per day: 9, 5, 3, 18 (4 to 7 Oct), 33 (9 Oct), then 123 (10 Oct). **Do not extend the window past 11 Oct**: PM2.5 rose to 89 on 12 Oct and 101 on 13 Oct, and AQI was Poor (224) on 13 Oct and 234 on 14 Oct. Wind was variable or SE/NW. The 4 and 9 Oct AQI values I did not read. Label: `Delhi, early October 2024 (calm)` |

Suggested replay ids: `delhi-2024-10`, `delhi-2024-11`, `lucknow-2023-11`, `delhi-2024-10-calm`.

---

## 2. Supporting daily numbers (Delhi, CPCB AQI at 4 PM)

| Date | Event 1 | Event 2 | Calm (4) |
|---|---|---|---|
| Oct 4 | | | PM2.5 54 |
| Oct 5 | | | AQI 145, PM2.5 41 |
| Oct 6 | | | 143, PM2.5 44 |
| Oct 7 | | | 126, PM2.5 57 |
| Oct 8 | | | 167 |
| Oct 9 | | | PM2.5 61 |
| Oct 10 | | | 132, PM2.5 56 |
| Oct 11 | | | 141, PM2.5 63 |
| Oct 12 | | | 155, PM2.5 89 (rise starts) |
| Oct 19 | 278 Poor | | |
| Oct 20 | 277 Poor | | |
| Oct 21 | 310 Very Poor | | |
| Oct 22 | 327 Very Poor, PM2.5 188 | | |
| Oct 23 | **364 Very Poor** | | |
| Nov 11 | | 352 Very Poor | |
| Nov 12 | | 334 Very Poor | |
| Nov 13 | | **418 Severe** | |
| Nov 14 | | **424 Severe** | |
| Nov 15 | | 396 Very Poor, PM2.5 327 (15 Nov) | |
| Nov 16 | | AQI not read | |
| Nov 17 | | PM2.5 454 (mean to 06:00 on 18 Nov) | |
| Nov 18 | | **494 Severe** | |
| Nov 19 | | 460 Severe, PM2.5 594 (18 Nov) | |

The Delhi row for 16 Nov and the 17 Nov AQI are not in the text I could read. Open `AQ-NCR-17112024.pdf` and the 16 Nov bulletin if you need them.

---

## 3. Backup events (use only if one of the above fails your data check)

| # | City | Dates | Spike observed | Likely cause (as stated) | Source | Season | Notes |
|---|---|---|---|---|---|---|---|
| B1 | Delhi | 2024-10-26 to 2024-11-01 | AQI 356 Very Poor on 27 Oct, 307 on 30 Oct, 328 on 31 Oct, 339 on 1 Nov | IITM stubble share about **5.5%** (26 Oct, wind forecast SE) rising to about **27.6%** (31 Oct, NW wind forecast 4 to 14 km/h) | CPCB [27 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-27102024.pdf), [30 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-30102024.pdf), [31 Oct](https://cpcb.nic.in/uploads/AQM/AQ-NCR-31102024.pdf), [1 Nov](https://cpcb.nic.in/uploads/AQM/AQ-NCR-01112024.pdf) | early (late Oct) | Tests whether risk **rises** when smoke share jumps in October, even though AQI was already Very Poor. AQI did not spike, the share did. Label: `Delhi, late October 2024` |
| B2 | Delhi | 2025-11-07 to 2025-11-12 | AQI 322 (7 Nov), 361 (8 Nov), first Severe day 11 Nov **428**, 12 Nov 418 | Stubble burning about 8.7% on 7 Nov, forecast about 31% for 8 to 9 Nov, then 22.4% on 12 Nov (DSS, the season's highest). Northwesterly wind up to 17 km/h on 7 Nov | [Superkalam 8 Nov](https://superkalam.com/current-affairs/08-11-2025/transport-farm-fires-keep-air-very-poor-pg3-ff20afe8-d479-4a81-8588-de8b4b27fa9f), [9 Nov](https://superkalam.com/current-affairs/09-11-2025/aqi-severe-in-many-areas-pg3-1ca747a7-c597-48de-8f67-977e47366e28), [Outlook Business](https://www.outlookbusiness.com/planet/climate/delhi-toxic-smog-crop-burning-surge-air-quality) | peak | **Fewer-fires year, do not over-claim.** Punjab 2,518 fire counts from 15 Sep to 3 Nov 2025 vs 4,132 a year earlier ([Tribune](https://www.tribuneindia.com/news/punjab/sharp-drop-in-stubble-burning-incidents-in-punjab-haryana-caqm/amp)). News figures, so secondary sources. Label: `Delhi, November 2025` |

---

## 4. Caveats to keep (and say in the video)

- **Daily, not hourly.** CPCB bulletins give daily AQI and daily PM2.5. You will find the hour yourself in CAMS, which is a ~45 km model with 3-hourly steps and may under-read city peaks. Report both numbers side by side.
- **Smoke is not the only driver.** Calm wind, inversions, traffic, dust (PM10), waste burning and firecrackers also drive Delhi's worst days. A "hit" means the warning came before a bad day, not that smoke caused it.
- **IITM stubble shares are model estimates** and were revised for 13 to 15 Nov 2024. Treat them as a range.
- **Small sample.** 3 events and 1 calm period cannot support accuracy claims. Say so.
- **Bulletin numbers are 24-hour averages**, the CAMS series will not match exactly.
- Avoided on purpose: Diwali firecracker days and pure-dust events.

## 5. Suggested rubric (change it if you prefer)

Hit: predicted risk medium or high at least 12 h before the first severe or spike day. Miss: none or low at that time. False alarm: medium or high in the calm window. Correct calm: none or low. For Event 1, "medium or lower" counts as a correct, honest reading.

## 6. What I could not confirm

- **Chandigarh:** no documented event found, so I did not use it.
- **Lucknow:** only one source (IANS), which does not name smoke. See the Notes in row 3.
- Hourly values for any event, and FIRMS fire counts per day (that is your data pull). Fire counts quoted here are CPCB's "active fire events" for Punjab and Haryana.
- Delhi AQI on 4 and 9 Oct 2024, 16 and 17 Nov 2024 (see section 2).
- **Removed from my first draft:** the Nov 2023 "wind reversal" event and the Aug 2024 monsoon calm period. The first because I could not confirm the claimed improvement (CPCB shows Delhi at 421 on 6 Nov 2023 and 426 on 8 Nov 2023), the second because you asked for a calm period inside fire season.

*General guidance, not medical advice. Source numbers are as published by each source.*
