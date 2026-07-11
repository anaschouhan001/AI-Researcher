"use client";

import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
  type ChartData,
  type ChartOptions,
} from "chart.js";
import { Bar, Doughnut, Line, Pie } from "react-chartjs-2";
import { BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ChartSpec } from "@/lib/types";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip
);

/** Validated categorical palette for the dark slate surface (fixed order, never cycled). */
const SERIES_COLORS = [
  "#e0447f", // pink
  "#9d5ce6", // violet
  "#e08a3c", // apricot
  "#3c9bd6", // sky
  "#c93cb0", // magenta
  "#5cb85c", // mint
  "#e06666", // coral
  "#8a6d3b", // latte
] as const;

const SURFACE = "#ffffff";
const INK_SECONDARY = "#b45580";
const GRID = "rgba(244, 114, 182, 0.15)";

function seriesColor(i: number): string {
  return SERIES_COLORS[Math.min(i, SERIES_COLORS.length - 1)];
}

function withAlpha(hex: string, alpha: string): string {
  return `${hex}${alpha}`;
}

const legendConfig = (display: boolean) => ({
  display,
  position: "bottom" as const,
  labels: {
    color: INK_SECONDARY,
    usePointStyle: true,
    pointStyle: "circle" as const,
    boxWidth: 8,
    boxHeight: 8,
    padding: 16,
  },
});

const tooltipConfig = {
  backgroundColor: "#fff0f6",
  titleColor: "#9a1a4e",
  bodyColor: "#7d1a43",
  borderColor: "rgba(249, 73, 140, 0.3)",
  borderWidth: 1,
  padding: 10,
  cornerRadius: 8,
  usePointStyle: true,
} as const;

function cartesianScales() {
  return {
    x: {
      grid: { color: GRID, drawTicks: false },
      border: { color: "rgba(244, 114, 182, 0.4)" },
      ticks: { color: INK_SECONDARY, maxRotation: 45 },
    },
    y: {
      grid: { color: GRID, drawTicks: false },
      border: { display: false },
      ticks: { color: INK_SECONDARY },
      beginAtZero: true,
    },
  };
}

function BarChart({ spec }: { spec: ChartSpec }) {
  const data: ChartData<"bar"> = {
    labels: spec.labels,
    datasets: spec.datasets.map((ds, i) => ({
      label: ds.label,
      data: ds.data,
      backgroundColor: withAlpha(seriesColor(i), "cc"),
      hoverBackgroundColor: seriesColor(i),
      borderRadius: 4,
      borderSkipped: "bottom" as const,
      // 2px surface gap between adjacent bars
      borderColor: SURFACE,
      borderWidth: 1,
      maxBarThickness: 44,
    })),
  };
  const options: ChartOptions<"bar"> = {
    responsive: true,
    maintainAspectRatio: false,
    scales: cartesianScales(),
    plugins: {
      legend: legendConfig(spec.datasets.length > 1),
      tooltip: tooltipConfig,
    },
  };
  return <Bar data={data} options={options} />;
}

function LineChart({ spec }: { spec: ChartSpec }) {
  const data: ChartData<"line"> = {
    labels: spec.labels,
    datasets: spec.datasets.map((ds, i) => ({
      label: ds.label,
      data: ds.data,
      borderColor: seriesColor(i),
      backgroundColor: withAlpha(seriesColor(i), "26"),
      pointBackgroundColor: seriesColor(i),
      pointBorderColor: SURFACE,
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2,
      tension: 0.3,
      fill: spec.datasets.length === 1,
    })),
  };
  const options: ChartOptions<"line"> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    scales: cartesianScales(),
    plugins: {
      legend: legendConfig(spec.datasets.length > 1),
      tooltip: tooltipConfig,
    },
  };
  return <Line data={data} options={options} />;
}

function CircularChart({ spec }: { spec: ChartSpec }) {
  const ds = spec.datasets[0] ?? { label: spec.title, data: [] };
  const dataset = {
    label: ds.label,
    data: ds.data,
    backgroundColor: spec.labels.map((_, i) => withAlpha(seriesColor(i), "cc")),
    hoverBackgroundColor: spec.labels.map((_, i) => seriesColor(i)),
    // 2px surface gap between segments
    borderColor: SURFACE,
    borderWidth: 2,
  };

  if (spec.type === "doughnut") {
    const data: ChartData<"doughnut"> = { labels: spec.labels, datasets: [dataset] };
    const options: ChartOptions<"doughnut"> = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: legendConfig(true), tooltip: tooltipConfig },
    };
    return <Doughnut data={data} options={options} />;
  }

  const data: ChartData<"pie"> = { labels: spec.labels, datasets: [dataset] };
  const options: ChartOptions<"pie"> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: legendConfig(true), tooltip: tooltipConfig },
  };
  return <Pie data={data} options={options} />;
}

function SingleChart({ spec }: { spec: ChartSpec }) {
  if (spec.labels.length === 0 || spec.datasets.every((d) => d.data.length === 0)) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-pink-400">
        No data points for this chart.
      </div>
    );
  }
  switch (spec.type) {
    case "bar":
      return <BarChart spec={spec} />;
    case "line":
      return <LineChart spec={spec} />;
    case "pie":
    case "doughnut":
      return <CircularChart spec={spec} />;
    default:
      return <BarChart spec={spec} />;
  }
}

export interface ChartPanelProps {
  charts: ChartSpec[];
}

export default function ChartPanel({ charts }: ChartPanelProps) {
  if (charts.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-2 p-10 text-center">
          <BarChart3 className="h-8 w-8 text-pink-300" aria-hidden="true" />
          <p className="text-sm text-pink-400">No charts were generated for this topic.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
      {charts.map((spec) => (
        <Card key={spec.id}>
          <CardHeader>
            <CardTitle className="text-sm">{spec.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <SingleChart spec={spec} />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
