import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { BookOpen } from 'lucide-react';

export default function EtymologyPage() {
  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">Name Etymology</h2>
        <p className="text-gray-600">Explore the origins and meanings of names</p>
      </div>

      <Card className="shadow-md max-w-2xl mx-auto">
        <CardHeader>
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            <CardTitle>Etymology Explorer</CardTitle>
          </div>
          <CardDescription>Discover the history behind names</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">
            This feature is coming soon. You&apos;ll be able to search for any name and discover its linguistic origins,
            historical meaning, cultural significance, and how it has evolved over time.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
