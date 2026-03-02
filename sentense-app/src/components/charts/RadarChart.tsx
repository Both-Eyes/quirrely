import { useMemo } from 'react';
import {
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

export interface RadarDataPoint {
  subject: string;
  value: number;
  fullMark?: number;
}

interface RadarChartProps {
  data: RadarDataPoint[];
  color?: string;
  fillOpacity?: number;
  showGrid?: boolean;
  showLabels?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const RadarChart = ({
  data,
  color = '#FF6B6B',
  fillOpacity = 0.3,
  showGrid = true,
  showLabels = true,
  size = 'md',
}: RadarChartProps) => {
  const dimensions = {
    sm: { width: 180, height: 180 },
    md: { width: 250, height: 250 },
    lg: { width: 320, height: 320 },
  };

  const normalizedData = useMemo(() => {
    return data.map((d) => ({
      ...d,
      fullMark: d.fullMark || 100,
    }));
  }, [data]);

  return (
    <div style={{ width: dimensions[size].width, height: dimensions[size].height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadar
          cx="50%"
          cy="50%"
          outerRadius={size === 'sm' ? '65%' : '70%'}
          data={normalizedData}
        >
          {showGrid && (
            <PolarGrid
              stroke="#E5E7EB"
              strokeDasharray="3 3"
            />
          )}
          {showLabels && (
            <PolarAngleAxis
              dataKey="subject"
              tick={{
                fill: '#6B7280',
                fontSize: size === 'sm' ? 10 : 12,
              }}
              tickLine={false}
            />
          )}
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          <Radar
            name="Voice"
            dataKey="value"
            stroke={color}
            fill={color}
            fillOpacity={fillOpacity}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value: number) => [`${value}%`, 'Score']}
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
};
