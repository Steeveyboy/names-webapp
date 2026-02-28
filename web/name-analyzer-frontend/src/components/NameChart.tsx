import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import type { TrendDataPoint } from '../lib/api';

interface NameChartProps {
  name: string;
  data: TrendDataPoint[];
}

export function NameChart({ name, data }: NameChartProps) {
  // Calculate total occurrences
  const totalMale = data.reduce((sum, d) => sum + d.male, 0);
  const totalFemale = data.reduce((sum, d) => sum + d.female, 0);
  const total = totalMale + totalFemale;

  return (
    <Card className="shadow-md">
      <CardHeader>
        <CardTitle className="capitalize">{name}</CardTitle>
        <CardDescription>
          Name popularity over time • Total occurrences: {total.toLocaleString()} 
          {' '}({totalMale.toLocaleString()} male, {totalFemale.toLocaleString()} female)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="year" 
              stroke="#6b7280"
              tick={{ fill: '#6b7280' }}
            />
            <YAxis 
              stroke="#6b7280"
              tick={{ fill: '#6b7280' }}
              label={{ value: 'Number of Occurrences', angle: -90, position: 'insideLeft', fill: '#6b7280' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="male" 
              stroke="#3b82f6" 
              strokeWidth={2}
              name="Male"
              dot={false}
            />
            <Line 
              type="monotone" 
              dataKey="female" 
              stroke="#ec4899" 
              strokeWidth={2}
              name="Female"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
