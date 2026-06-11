interface TaskDisplayProps {
  title: string;
  description: string;
  promptText: string;
  imageUrl?: string;
}

export default function TaskDisplay({
  title,
  description,
  promptText,
  imageUrl,
}: TaskDisplayProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">{title}</h2>
        <p className="text-gray-500 text-sm mt-1">{description}</p>
      </div>
      <div className="border-t pt-4">
        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
          {promptText}
        </p>
        {imageUrl && (
          <img
            src={imageUrl}
            alt="Task image"
            className="mt-4 rounded-lg max-w-full max-h-64 object-contain"
          />
        )}
      </div>
    </div>
  );
}
