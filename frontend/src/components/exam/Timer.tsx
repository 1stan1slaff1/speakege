interface TimerProps {
  display: string;
  label: string;
  isRunning: boolean;
  isRecording?: boolean;
}

export default function Timer({ display, label, isRunning, isRecording }: TimerProps) {
  return (
    <div className="flex flex-col items-center gap-2" aria-live={isRunning ? 'polite' : 'off'}>
      <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">
        {label}
      </span>
      <div className={`flex items-center gap-3 ${isRunning ? 'opacity-100' : 'opacity-80'}`}>
        {isRecording && (
          <span className="relative flex h-3 w-3" aria-hidden="true">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
          </span>
        )}
        <span className="text-5xl font-mono font-bold tracking-tight text-gray-950">
          {display}
        </span>
      </div>
      {isRecording && (
        <span className="text-sm text-red-500 font-medium">Идёт запись</span>
      )}
    </div>
  );
}
