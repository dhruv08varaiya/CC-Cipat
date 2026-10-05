import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts';
import { MetricSnapshot } from '../../hooks/useDigitalTwinEngine';

interface OscilloscopeProps {
  history: MetricSnapshot[];
}

export const DigitalTwinOscilloscope: React.FC<OscilloscopeProps> = ({ history }) => {
  const chartData = history.slice(-40);

  return (
    <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-2 h-full flex flex-col">
      <div className="flex items-center justify-between pb-1.5 border-b border-[#27272A]">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs font-semibold text-zinc-200">
            LATENCY OSCILLOSCOPE (TIME-SERIES)
          </span>
          <span className="font-mono text-[10px] text-zinc-500">&bull; SLA Threshold 30.0 ms</span>
        </div>
        <span className="font-mono text-[11px] text-emerald-400">
          Nominal P95 &lt; 35ms
        </span>
      </div>

      <div className="flex-1 min-h-[160px] w-full pt-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 8, right: 10, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272A" vertical={false} />
            <XAxis 
              dataKey="timeSec" 
              stroke="#52525B" 
              tick={{ fontSize: 9, fontFamily: 'monospace' }} 
              interval="preserveStartEnd"
              tickFormatter={(v) => `${v.toFixed(0)}s`}
            />
            <YAxis 
              stroke="#52525B" 
              tick={{ fontSize: 9, fontFamily: 'monospace' }}
              domain={[0, 'auto']}
              unit="ms"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090A0F',
                borderColor: '#27272A',
                fontSize: '11px',
                fontFamily: 'monospace',
                color: '#F4F4F5'
              }}
            />
            {/* SLA Alert Threshold Line */}
            <ReferenceLine 
              y={30} 
              stroke="#F97316" 
              strokeDasharray="4 4" 
              label={{ value: 'SLA 30ms', fill: '#F97316', fontSize: 9, position: 'insideTopRight', fontFamily: 'monospace' }} 
            />
            <Line
              type="monotone"
              dataKey="latencyMs"
              name="Mean Latency"
              stroke="#38BDF8"
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="p95LatencyMs"
              name="P95 Latency"
              stroke="#818CF8"
              strokeWidth={1}
              strokeDasharray="2 2"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
