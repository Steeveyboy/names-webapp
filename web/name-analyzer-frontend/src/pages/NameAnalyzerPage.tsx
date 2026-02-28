import { useState } from 'react';
import { NameSearch } from '../components/NameSearch';
import { NameChart } from '../components/NameChart';
import { fetchNameTrends } from '../lib/api';
import type { TrendDataPoint } from '../lib/api';

export default function NameAnalyzerPage() {
  const [searchedName, setSearchedName] = useState('');
  const [nameData, setNameData] = useState<TrendDataPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (
    name: string,
    filters: { state: string; gender: string; yearFrom: string; yearTo: string }
  ) => {
    setSearchedName(name);
    setError(null);

    try {
      let data = await fetchNameTrends(name);

      // Filter by year range
      if (filters.yearFrom) {
        data = data.filter(d => d.year >= parseInt(filters.yearFrom, 10));
      }
      if (filters.yearTo) {
        data = data.filter(d => d.year <= parseInt(filters.yearTo, 10));
      }

      // Filter by gender — zero out the other line
      if (filters.gender === 'Male') {
        data = data.map(d => ({ ...d, female: 0 }));
      } else if (filters.gender === 'Female') {
        data = data.map(d => ({ ...d, male: 0 }));
      }

      setNameData(data);
    } catch (err) {
      console.error('Error fetching name data:', err);
      setError('Unable to load name data. Please check your connection and try again.');
      setNameData([]);
    }
  };

  return (
    <>
      <NameSearch onSearch={handleSearch} />
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-4 text-sm">
          {error}
        </div>
      )}
      {searchedName && nameData.length > 0 && (
        <NameChart name={searchedName} data={nameData} />
      )}
    </>
  );
}
