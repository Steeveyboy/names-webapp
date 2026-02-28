import { useState } from 'react';
import { NameSearch } from './components/NameSearch';
import { NameChart } from './components/NameChart';
import { BarChart3 } from 'lucide-react';

interface NameData {
  year: number;
  male: number;
  female: number;
  state: string;
  name: string;
}


// const mockData: NameData[] = [
//   { name: "Veronica", year: 1985, male: 200, female: 180, state: "California" },
//   { name: "Veronica", year: 1986, male: 150, female: 170, state: "New York" },
//   { name: "Veronica", year: 1987, male: 100, female: 50, state: "California" },
//   { name: "James", year: 1985, male: 300, female: 50, state: "Texas" },
//   { name: "James", year: 1986, male: 250, female: 60, state: "Florida" },
// ];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// returns arrays of NameData objects for a given name
const getNameData = async (name: string): Promise<NameData[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/searchName/${name}`);
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data: NameData[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching name data:", error);
    return [];
  }
};

// const getNameData = async (name: string): Promise<NameData[]> => {
//   console.log(`Fetching data for ${name} (mock)`);
//   // Simulate network delay
//   return new Promise(resolve => {
//     setTimeout(() => {
//       resolve(mockData.filter(d => d.name.toLowerCase() === name.toLowerCase()));
//     }, 200);
//   });
// };


export default function App() {
  const [searchedName, setSearchedName] = useState('');
  const [nameData, setNameData] = useState<NameData[]>([]);

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

  try {
    let nameData = await getNameData(name);
    // Given NameData[], filter results if given from on submit in namesearch.tsx

    // Filter by year range
    if (filters.yearFrom) {
      nameData = nameData.filter(d => d.year >= parseInt(filters.yearFrom));
    }
    if (filters.yearTo) {
      nameData = nameData.filter(d => d.year <= parseInt(filters.yearTo));
    }

    // Filter by state
    if (filters.state && filters.state !== "All") {
      nameData = nameData.filter(d => d.state === filters.state);
    }

    // Filter by gender
    if (filters.gender && filters.gender !== "All") {
      // d is each NameData object returned from api call
      nameData = nameData.map(d => {
        // if the gender is filtered to only male, set female count to 0 so the chart ignores it [ vice versa]
        if (filters.gender === "Male") return { ...d, female: 0 };
        if (filters.gender === "Female") return { ...d, male: 0 };
        return d;
      });
    }

    setNameData(nameData);
  } catch (error) {
    console.error("Error fetching or filtering name data:", error);
    setNameData([]);
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
        {searchedName && nameData.length > 0 && (
          <NameChart name={searchedName} data={nameData} />
        )}
      </div>
    </div>
  );
}
