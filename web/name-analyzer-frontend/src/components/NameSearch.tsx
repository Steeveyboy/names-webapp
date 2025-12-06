import { useState } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';
import { Search, ChevronDown, ChevronUp } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';

interface NameSearchProps {
  onSearch: (
    name: string,
    filters: {
      state: string;
      gender: string;
      yearFrom: string;
      yearTo: string;
    }
  ) => void;
}

const US_STATES = [
  'All States',
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT',
  'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA',
  'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
  'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
  'NJ', 'NM', 'NY', 'NC', 'ND', 'OH',
  'OK', 'OR', 'PA', 'RI', 'SC', 'SD',
  'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
  'WI', 'WY'
];
const currentYear = new Date().getFullYear();
const maxYear = currentYear - 1;

export function NameSearch({ onSearch }: NameSearchProps) {
  const [name, setName] = useState('');
  const [state, setState] = useState('All States');
  const [gender, setGender] = useState('All');
  const [yearFrom, setYearFrom] = useState('1980');
  const [yearTo, setYearTo] = useState(String(maxYear));
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onSearch(name.trim(), { state, gender, yearFrom, yearTo });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <form onSubmit={handleSubmit}>
        {/* Main Search */}
        <div className="mb-4">
          <Label htmlFor="name-input">Search for a name</Label>
          <div className="flex gap-2 mt-2">
            <Input
              id="name-input"
              type="text"
              placeholder="e.g., Jonathan"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white">
              <Search className="w-4 h-4 mr-2" />
              Analyze
            </Button>
          </div>
        </div>

        {/* Advanced Filters */}
        <Collapsible open={isAdvancedOpen} onOpenChange={setIsAdvancedOpen}>
          <CollapsibleTrigger asChild>
            <Button
              type="button"
              variant="ghost"
              className="w-full justify-between text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
            >
              Advanced Filters
              {isAdvancedOpen ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-4">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* State Filter */}
              <div>
                <Label htmlFor="state-select">State</Label>
                <Select value={state} onValueChange={setState}>
                  <SelectTrigger id="state-select" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {US_STATES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Gender Filter */}
              <div>
                <Label htmlFor="gender-select">Gender</Label>
                <Select value={gender} onValueChange={setGender}>
                  <SelectTrigger id="gender-select" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="All">All</SelectItem>
                    <SelectItem value="Male">Male</SelectItem>
                    <SelectItem value="Female">Female</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Year From */}
              <div>
                <Label htmlFor="year-from">From Year</Label>
                <Input
                  id="year-from"
                  type="number"
                  min="1880"
                  max={maxYear}
                  value={yearFrom}
                  onChange={(e) => setYearFrom(e.target.value)}
                  className="mt-2"
                />
              </div>

              {/* Year To */}
              <div>
                <Label htmlFor="year-to">To Year</Label>
                <Input
                  id="year-to"
                  type="number"
                  min="1880"
                  max={maxYear}
                  value={yearTo}
                  onChange={(e) => setYearTo(e.target.value)}
                  className="mt-2"
                />
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </form>
    </div>
  );
}
