const BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Helper to get the saved profile setting
function getAudience() {
  return localStorage.getItem('whiff_audience') || 'general';
}

export async function getSmokeRadar(scenario = 'smoke_high') {
  const audience = getAudience();
  const response = await fetch(`${BASE_URL}/smoke?scenario=${scenario}&audience=${audience}`);
  if (!response.ok) throw new Error(`API Error: ${response.status}`);
  return response.json();
}

export async function getDayPlan(scenario = 'day_windows') {
  const audience = getAudience();
  const response = await fetch(`${BASE_URL}/day?scenario=${scenario}&audience=${audience}`);
  if (!response.ok) throw new Error(`API Error: ${response.status}`);
  return response.json();
}