interface TimerProps {
  display: string;
  label: string;
  isRunning: boolean;
  isRecording?: boolean;
}

export default function Timer({ display, label, isRunning, isRecording }: TimerProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">
        {label}
      </span>
      <div className="flex items-center gap-3">
        {isRecording && (
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
          </span>
        )}
        <span className="text-5xl font-mono font-bold tracking-tight">
          {display}
        </span>
      </div>
      {isRecording && (
        <span className="text-sm text-red-500 font-medium">Идёт запись</span>
      )}
    </div>
  );
}
