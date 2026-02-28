import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { BarChart3, TrendingUp, Users } from 'lucide-react';

export default function FactsPage() {
  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">Name Facts &amp; Trivia</h2>
        <p className="text-gray-600">Discover interesting facts about baby names in America</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="shadow-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
              <CardTitle className="text-lg">Trending Names</CardTitle>
            </div>
            <CardDescription>Names rising in popularity</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-sm">Coming soon — Top trending names by decade and year.</p>
          </CardContent>
        </Card>

        <Card className="shadow-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-indigo-600" />
              <CardTitle className="text-lg">Name Diversity</CardTitle>
            </div>
            <CardDescription>How unique are names over time?</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-sm">Coming soon — Track how the diversity of baby names has changed since 1880.</p>
          </CardContent>
        </Card>

        <Card className="shadow-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-indigo-600" />
              <CardTitle className="text-lg">All-Time Rankings</CardTitle>
            </div>
            <CardDescription>The most popular names ever</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-sm">Coming soon — All-time most popular baby names in the United States.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
