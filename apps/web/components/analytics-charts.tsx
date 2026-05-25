"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const hiringFunnelData = [
  { name: "Applied", value: 1000 },
  { name: "Screened", value: 600 },
  { name: "Interviewed", value: 300 },
  { name: "Offered", value: 150 },
  { name: "Hired", value: 75 },
]

const skillDemandData = [
  { skill: "Python", demand: 85 },
  { skill: "React", demand: 72 },
  { skill: "AWS", demand: 65 },
  { skill: "ML", demand: 58 },
  { skill: "Go", demand: 45 },
]

const COLORS = ["#3b82f6", "#8b5cf6", "#ec4899", "#f97316", "#22c55e"]

export function AnalyticsCharts() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Hiring Funnel</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hiringFunnelData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Skill Demand Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={skillDemandData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ skill, percent }: { skill: string; percent: number }) =>
                  `${skill} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="demand"
              >
                {skillDemandData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
