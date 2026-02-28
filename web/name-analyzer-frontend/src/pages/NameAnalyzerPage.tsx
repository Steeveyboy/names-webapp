import { useState } from 'react';
import { NameSearch } from '../components/NameSearch';
import { NameChart } from '../components/NameChart';
import { fetchNameTrends } from '../lib/api';
import type { TrendDataPoint } from '../lib/api';

export default function NameAnalyzerPage() {
  const [searchedName, setSearchedName] = useState('');
  const [nameData, setNameData] = useState<TrendDataPoint[]>([]);

  const handleSearch = async (
    name: string,
    filters: { state: string; gender: string; yearFrom: string; yearTo: string }
  ) => {
    setSearchedName(name);

    try {
      let data = await fetchNameTrends(name);

      // Filter by year range
      if (filters.yearFrom) {
        data = data.filter(d => d.year >= parseInt(filters.yearFrom));
      }
      if (filters.yearTo) {
        data = data.filter(d => d.year <= parseInt(filters.yearTo));
      }

      // Filter by gender — zero out the other line
      if (filters.gender === 'Male') {
        data = data.map(d => ({ ...d, female: 0 }));
      } else if (filters.gender === 'Female') {
        data = data.map(d => ({ ...d, male: 0 }));
      }

      setNameData(data);
    } catch (error) {
      console.error('Error fetching name data:', error);
      setNameData([]);
    }
  };

  return (
    <>
      <NameSearch onSearch={handleSearch} />
      {searchedName && nameData.length > 0 && (
        <NameChart name={searchedName} data={nameData} />
      )}
    </>
  );
}
