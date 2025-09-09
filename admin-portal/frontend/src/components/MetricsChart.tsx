'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { time: '00:00', cpu: 20, memory: 45, disk: 60 },
  { time: '04:00', cpu: 15, memory: 42, disk: 58 },
  { time: '08:00', cpu: 35, memory: 55, disk: 62 },
  { time: '12:00', cpu: 45, memory: 60, disk: 65 },
  { time: '16:00', cpu: 55, memory: 65, disk: 68 },
  { time: '20:00', cpu: 40, memory: 58, disk: 66 },
  { time: '24:00', cpu: 25, memory: 50, disk: 63 },
]

export default function MetricsChart() {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="cpu" 
            stroke="#3b82f6" 
            strokeWidth={2}
            name="CPU %"
          />
          <Line 
            type="monotone" 
            dataKey="memory" 
            stroke="#10b981" 
            strokeWidth={2}
            name="Memory %"
          />
          <Line 
            type="monotone" 
            dataKey="disk" 
            stroke="#f59e0b" 
            strokeWidth={2}
            name="Disk %"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}