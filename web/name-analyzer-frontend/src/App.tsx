import { useState } from 'react';
import { NameSearch } from './components/NameSearch';
import { NameChart } from './components/NameChart';
import { BarChart3 } from 'lucide-react';

interface NameData {
  year: number;
  male: number;
  female: number;
}

// Mock data for demonstration
const getMockData = (name: string): NameData[] => {
  const data: NameData[] = [];
  for (let year = 1980; year <= 2023; year++) {
    data.push({
      year,
      male: Math.floor(Math.random() * 1000) + 100,
      female: Math.floor(Math.random() * 1000) + 100,
    });
  }
  return data;
};

export default function App() {
  const [searchedName, setSearchedName] = useState('');
  const [nameData, setNameData] = useState<NameData[]>([]);

  const handleSearch = (
    name: string,
    filters: {
      state: string;
      gender: string;
      yearFrom: string;
      yearTo: string;
    }
  ) => {
    setSearchedName(name);
    const mockData = getMockData(name);
    
    // Filter data based on year range
    let filteredData = mockData;
    if (filters.yearFrom) {
      filteredData = filteredData.filter(d => d.year >= parseInt(filters.yearFrom));
    }
    if (filters.yearTo) {
      filteredData = filteredData.filter(d => d.year <= parseInt(filters.yearTo));
    }
    
    setNameData(filteredData);
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
        {searchedName && nameData.length > 0 && (
          <NameChart name={searchedName} data={nameData} />
        )}
      </div>
    </div>
  );
}
