const dictionary = {
  en: {
    // Reason Codes
    smoke_aligned_fires: "{count} fires are upwind and the wind carries smoke toward you",
    smoke_none_upwind: "No significant fires upwind within range",
    wind_from_clean_sector: "Wind is bringing cleaner air in",
    wind_calm_trapping: "Calm wind, pollution sits in place",
    festival_night: "Firecracker-heavy night in the forecast window",
    pm25_below_avg: "Window is cleaner than day average by {percent}%",
    pm25_above_avg: "Period is dirtier than day average by {percent}%",
    best_hour: "Cleanest hour of the day",
    worst_hour: "Dirtiest hour of the day",
    all_day_poor: "Every hour poor",
    forecast_rising: "Air quality forecast to worsen",
    forecast_falling: "Air quality forecast to improve",
    data_stale: "Upstream data older than expected; showing last known values",
    
    // Advice Codes
    keep_windows_closed_evening: "Keep windows closed in the evening",
    run_purifier: "Run your air purifier",
    delay_outdoor_events: "Delay outdoor events",
    mask_n95_outdoors: "Wear an N95 mask outdoors",
    shift_heavy_work: "Shift heavy outdoor work",
    indoor_swap: "Swap outdoor activities for indoor ones"
  },
  hi: {
    smoke_aligned_fires: "[HI: {count} fires are upwind...]",
    // Remaining Hindi stubs will be filled post-review
  }
};

export function t(code, lang = 'en', params = {}) {
  const text = dictionary[lang]?.[code];
  if (!text) {
    console.error(`[i18n ERROR] Missing key: ${code}`);
    return `[${code}]`;
  }
  
  return Object.entries(params).reduce(
    (str, [key, val]) => str.replace(`{${key}}`, val),
    text
  );
}