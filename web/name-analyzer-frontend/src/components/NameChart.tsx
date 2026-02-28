import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  TooltipProps,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import type { NameData } from '../App';

interface NameChartProps {
  name: string;
  data: NameData[];
}

/** Formats large numbers with commas, e.g. 12345 → "12,345" */
const fmt = (n: number | null | undefined) =>
  n != null ? n.toLocaleString() : '—';

function CustomTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-4 py-3 text-sm">
      <p className="font-semibold text-gray-800 mb-1">{label}</p>
      {payload.map(entry => (
        <p key={entry.name} style={{ color: entry.color }} className="flex gap-2">
          <span className="font-medium">{entry.name}:</span>
          <span>{fmt(entry.value)}</span>
        </p>
      ))}
    </div>
  );
}

export function NameChart({ name, data }: NameChartProps) {
  const { totalMale, totalFemale, peakMale, peakFemale } = useMemo(() => {
    let totalMale = 0, totalFemale = 0;
    let peakMale = { year: 0, count: 0 }, peakFemale = { year: 0, count: 0 };

    for (const d of data) {
      if (d.male != null) {
        totalMale += d.male;
        if (d.male > peakMale.count) peakMale = { year: d.year, count: d.male };
      }
      if (d.female != null) {
        totalFemale += d.female;
        if (d.female > peakFemale.count) peakFemale = { year: d.year, count: d.female };
      }
    }

    return { totalMale, totalFemale, peakMale, peakFemale };
  }, [data]);

  const showMale = data.some(d => d.male != null);
  const showFemale = data.some(d => d.female != null);

  return (
    <Card className="shadow-md">
      <CardHeader>
        <CardTitle className="capitalize text-xl">{name}</CardTitle>
        <CardDescription>Usage over time by gender</CardDescription>

        {/* Summary stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
          {showMale && (
            <>
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-xs text-blue-500 uppercase font-semibold tracking-wide">Total Male</p>
                <p className="text-lg font-bold text-blue-700">{fmt(totalMale)}</p>
              </div>
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-xs text-blue-500 uppercase font-semibold tracking-wide">Peak Male</p>
                <p className="text-lg font-bold text-blue-700">{peakMale.year}</p>
                <p className="text-xs text-blue-500">{fmt(peakMale.count)}</p>
              </div>
            </>
          )}
          {showFemale && (
            <>
              <div className="bg-pink-50 rounded-lg p-3">
                <p className="text-xs text-pink-500 uppercase font-semibold tracking-wide">Total Female</p>
                <p className="text-lg font-bold text-pink-700">{fmt(totalFemale)}</p>
              </div>
              <div className="bg-pink-50 rounded-lg p-3">
                <p className="text-xs text-pink-500 uppercase font-semibold tracking-wide">Peak Female</p>
                <p className="text-lg font-bold text-pink-700">{peakFemale.year}</p>
                <p className="text-xs text-pink-500">{fmt(peakFemale.count)}</p>
              </div>
            </>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="year"
              stroke="#9ca3af"
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickLine={false}
            />
            <YAxis
              stroke="#9ca3af"
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={v => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}
              label={{
                value: 'Births per year',
                angle: -90,
                position: 'insideLeft',
                offset: 12,
                fill: '#9ca3af',
                fontSize: 12,
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '12px', fontSize: '13px' }}
              formatter={v => <span className="text-gray-700">{v}</span>}
            />

            {/* Peak year reference lines */}
            {showMale && peakMale.year > 0 && (
              <ReferenceLine
                x={peakMale.year}
                stroke="#93c5fd"
                strokeDasharray="4 4"
                label={{ value: `♂ peak`, position: 'top', fill: '#3b82f6', fontSize: 10 }}
              />
            )}
            {showFemale && peakFemale.year > 0 && (
              <ReferenceLine
                x={peakFemale.year}
                stroke="#f9a8d4"
                strokeDasharray="4 4"
                label={{ value: `♀ peak`, position: 'top', fill: '#ec4899', fontSize: 10 }}
              />
            )}

            {showMale && (
              <Line
                type="monotone"
                dataKey="male"
                stroke="#3b82f6"
                strokeWidth={2.5}
                name="Male"
                dot={false}
                activeDot={{ r: 5, strokeWidth: 0 }}
                connectNulls={false}
              />
            )}
            {showFemale && (
              <Line
                type="monotone"
                dataKey="female"
                stroke="#ec4899"
                strokeWidth={2.5}
                name="Female"
                dot={false}
                activeDot={{ r: 5, strokeWidth: 0 }}
                connectNulls={false}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
