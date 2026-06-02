type ScoreMeterProps = {
  label: string;
  value: number;
};

export function ScoreMeter({ label, value }: ScoreMeterProps) {
  const safeValue = Math.max(0, Math.min(value, 100));
  const color = safeValue >= 80 ? "bg-pine" : safeValue >= 60 ? "bg-cobalt" : "bg-coral";

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="font-medium text-ink">{label}</span>
        <span className="tabular-nums text-ink">{safeValue.toFixed(0)}</span>
      </div>
      <div className="h-2 rounded-full bg-line">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${safeValue}%` }} />
      </div>
    </div>
  );
}

