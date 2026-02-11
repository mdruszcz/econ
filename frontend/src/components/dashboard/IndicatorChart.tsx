import Plot from 'react-plotly.js';

interface Props {
  title: string;
  years: number[];
  baseline: number[];
  scenario: number[];
  yLabel: string;
}

export function IndicatorChart({ title, years, baseline, scenario, yLabel }: Props) {
  return (
    <Plot
      data={[
        {
          x: years,
          y: baseline,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Baseline',
          line: { color: '#888', dash: 'dash', width: 2 },
          marker: { size: 5 },
        },
        {
          x: years,
          y: scenario,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Scenario',
          line: { color: '#2563eb', width: 2.5 },
          marker: { size: 6 },
        },
      ]}
      layout={{
        title: { text: title, font: { size: 14 } },
        xaxis: { title: 'Year', dtick: 1 },
        yaxis: { title: yLabel },
        legend: { orientation: 'h', y: -0.2 },
        margin: { t: 40, r: 20, b: 60, l: 60 },
        height: 300,
        autosize: true,
      }}
      config={{ responsive: true, displayModeBar: false }}
      style={{ width: '100%' }}
    />
  );
}
