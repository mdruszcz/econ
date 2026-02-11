import type { InstrumentSpec } from '../../api/types';

interface Props {
  spec: InstrumentSpec;
  value: number;
  onChange: (value: number) => void;
}

export function InstrumentRow({ spec, value, onChange }: Props) {
  return (
    <div className="instrument-row">
      <div className="instrument-label">
        <strong>{spec.label}</strong>
        <span className="instrument-unit">{spec.unit}</span>
      </div>
      <div className="instrument-controls">
        <input
          type="range"
          min={spec.min}
          max={spec.max}
          step={(spec.max - spec.min) / 200}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
        />
        <input
          type="number"
          min={spec.min}
          max={spec.max}
          step={spec.key === 'VIG_X' || spec.key === 'DTH_X' ? 100 : 0.1}
          value={value}
          onChange={(e) => {
            const v = parseFloat(e.target.value);
            if (!isNaN(v)) onChange(Math.min(spec.max, Math.max(spec.min, v)));
          }}
        />
        <span className="instrument-default" title="Baseline default">
          (def: {spec.default})
        </span>
      </div>
    </div>
  );
}
