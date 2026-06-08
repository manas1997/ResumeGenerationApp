type ScoreMeterProps = {
  label: string;
  value: number;
};

export function ScoreMeter({ label, value }: ScoreMeterProps) {
  const safeValue = Math.max(0, Math.min(value, 100));
  const status = safeValue >= 80 ? "S" : safeValue >= 60 ? "A" : "C";

  return (
    <div className="score-meter group">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="font-medium text-slate-100">{label}</span>
        <span className="score-rank" aria-label={`Rank ${status}`}>
          {status}
        </span>
      </div>
      <div className="mt-3 flex items-center gap-3">
        <div className="h-2 flex-1 overflow-hidden rounded-sm bg-white/10">
          <div className="score-fill h-full rounded-sm" style={{ width: `${safeValue}%` }} />
        </div>
        <span className="w-11 text-right text-sm font-semibold tabular-nums text-cyan-100">
          {safeValue.toFixed(0)}
        </span>
      </div>
    </div>
  );
}
