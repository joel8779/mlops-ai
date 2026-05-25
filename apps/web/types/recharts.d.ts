declare module "recharts" {
  import * as React from "react";

  type ChartComponent = React.FC<Record<string, unknown>>;

  export const BarChart: ChartComponent;
  export const Bar: ChartComponent;
  export const LineChart: ChartComponent;
  export const Line: ChartComponent;
  export const XAxis: ChartComponent;
  export const YAxis: ChartComponent;
  export const CartesianGrid: ChartComponent;
  export const Tooltip: ChartComponent;
  export const ResponsiveContainer: ChartComponent;
  export const PieChart: ChartComponent;
  export const Pie: ChartComponent;
  export const Cell: ChartComponent;
  export const AreaChart: ChartComponent;
  export const Area: ChartComponent;
  export const Legend: ChartComponent;
}
