const API_BASE = 'http://localhost:8000';

// Types matching backend models
export interface YearCount {
  year: number;
  count: number;
}

export interface GenderBreakdown {
  gender: 'M' | 'F';
  total_count: number;
}

export interface NameStats {
  name: string;
  total_count: number;
  peak_year: number;
  peak_count: number;
  first_year: number;
  last_year: number;
  gender_breakdown: GenderBreakdown[];
}

export interface TrendDataPoint {
  year: number;
  male: number;
  female: number;
}

export interface StateCount {
  state: string;
  count: number;
}

export interface RankedName {
  name: string;
  gender: 'M' | 'F';
  count: number;
  rank: number;
}

/**
 * Fetch male and female trends separately and merge into comparative format.
 * Both endpoints return YearCount[], which we combine into TrendDataPoint[].
 */
export async function fetchNameTrends(name: string): Promise<TrendDataPoint[]> {
  const encodedName = encodeURIComponent(name);
  const [maleRes, femaleRes] = await Promise.all([
    fetch(`${API_BASE}/api/names/${encodedName}/trends?gender=M`),
    fetch(`${API_BASE}/api/names/${encodedName}/trends?gender=F`),
  ]);

  // If both requests failed, throw so the caller can display a meaningful error.
  if (!maleRes.ok && !femaleRes.ok) {
    throw new Error('Failed to fetch name trends');
  }

  const maleData: YearCount[] = maleRes.ok ? await maleRes.json() : [];
  const femaleData: YearCount[] = femaleRes.ok ? await femaleRes.json() : [];

  // Merge by year
  const yearMap = new Map<number, TrendDataPoint>();
  for (const d of maleData) {
    yearMap.set(d.year, { year: d.year, male: d.count, female: 0 });
  }
  for (const d of femaleData) {
    const existing = yearMap.get(d.year);
    if (existing) {
      existing.female = d.count;
    } else {
      yearMap.set(d.year, { year: d.year, male: 0, female: d.count });
    }
  }

  return Array.from(yearMap.values()).sort((a, b) => a.year - b.year);
}

export async function fetchNameStats(name: string): Promise<NameStats | null> {
  const res = await fetch(`${API_BASE}/api/names/${encodeURIComponent(name)}/stats`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchStateDistribution(name: string): Promise<StateCount[]> {
  const res = await fetch(`${API_BASE}/api/names/${encodeURIComponent(name)}/state-distribution`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchTopNames(year: number, limit = 10): Promise<RankedName[]> {
  const res = await fetch(`${API_BASE}/api/rankings/${year}?limit=${limit}`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchDiversity(year?: number): Promise<{ unique_names: number; year: number | null }> {
  const url = year != null
    ? `${API_BASE}/api/diversity?year=${year}`
    : `${API_BASE}/api/diversity`;
  const res = await fetch(url);
  if (!res.ok) return { unique_names: 0, year: null };
  return res.json();
}
