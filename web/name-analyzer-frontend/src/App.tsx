import { useState } from 'react';
import { NameSearch } from './components/NameSearch';
import { NameChart } from './components/NameChart';
import { BarChart3 } from 'lucide-react';

/** Shape of a single row returned by GET /api/names/{name} */
interface NameRecord {
  name: string;
  gender: 'M' | 'F';
  count: number;
  year: number;
}

/** Pivoted per-year data used by the chart */
export interface NameData {
  year: number;
  male: number | null;
  female: number | null;
}

/** Fetch raw records from the versioned endpoint and pivot by year. */
const getNameData = async (name: string): Promise<NameData[]> => {
  const base = import.meta.env.VITE_API_URL ?? '';
  const response = await fetch(`${base}/api/names/${encodeURIComponent(name)}`);
  if (!response.ok) throw new Error(`API error: ${response.status}`);

  const records: NameRecord[] = await response.json();

  // Aggregate counts by year, splitting M vs F
  const byYear = new Map<number, { male: number; female: number }>();
  for (const r of records) {
    const entry = byYear.get(r.year) ?? { male: 0, female: 0 };
    if (r.gender === 'M') entry.male += r.count;
    else entry.female += r.count;
    byYear.set(r.year, entry);
  }

  return Array.from(byYear.entries())
    .sort(([a], [b]) => a - b)
    .map(([year, { male, female }]) => ({
      year,
      male: male || null,
      female: female || null,
    }));
};

export default function App() {
  const [searchedName, setSearchedName] = useState('');
  const [nameData, setNameData] = useState<NameData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (
    name: string,
    filters: {
      state: string;
      gender: string;
      yearFrom: string;
      yearTo: string;
    }
  ) => {
    setSearchedName(name);
    setError(null);
    setIsLoading(true);

    try {
      let data = await getNameData(name);

      // Filter by year range
      if (filters.yearFrom) {
        data = data.filter(d => d.year >= parseInt(filters.yearFrom));
      }
      if (filters.yearTo) {
        data = data.filter(d => d.year <= parseInt(filters.yearTo));
      }

      // Hide the irrelevant gender series rather than removing points,
      // so the chart axis scale stays consistent.
      if (filters.gender === 'Male') {
        data = data.map(d => ({ ...d, female: null }));
      } else if (filters.gender === 'Female') {
        data = data.map(d => ({ ...d, male: null }));
      }

      setNameData(data);
    } catch (err) {
      console.error('Error fetching name data:', err);
      setError('Failed to load data. Is the API server running?');
      setNameData([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <BarChart3 className="w-10 h-10 text-indigo-600" />
            <h1 className="text-indigo-600">Nomi</h1>
          </div>
          
          {/* App Description */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <p className="text-gray-700 mb-4">
              Nomi helps you understand name uniqueness and popularity with three powerful insights:
            </p>
            <div className="grid md:grid-cols-3 gap-4 text-left">
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  1
                </div>
                <p className="text-gray-600">
                  Analyze name uniqueness by <span className="text-indigo-600">gender</span>
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  2
                </div>
                <p className="text-gray-600">
                  Compare popularity across <span className="text-indigo-600">different states</span>
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  3
                </div>
                <p className="text-gray-600">
                  Track trends over <span className="text-indigo-600">specific years</span> for choosing a name
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search Component */}
        <NameSearch onSearch={handleSearch} />

        {/* Chart Component */}
        {isLoading && (
          <div className="flex justify-center items-center py-16 text-indigo-600">
            <svg className="animate-spin w-8 h-8 mr-3" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Loading…
          </div>
        )}
        {!isLoading && error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-center">
            {error}
          </div>
        )}
        {!isLoading && !error && searchedName && nameData.length === 0 && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 rounded-lg p-4 text-center">
            No data found for <strong>{searchedName}</strong>.
          </div>
        )}
        {!isLoading && !error && searchedName && nameData.length > 0 && (
          <NameChart name={searchedName} data={nameData} />
        )}
      </div>
    </div>
  );
}
