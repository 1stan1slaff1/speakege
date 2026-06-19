/* eslint-disable @next/next/no-img-element */

interface TaskDisplayProps {
  title: string;
  description: string;
  promptText: string;
  imageUrl?: string;
  imageUrls?: readonly string[];
  imageCaptions?: readonly string[];
}

export default function TaskDisplay({
  title,
  description,
  promptText,
  imageUrl,
  imageUrls,
  imageCaptions,
}: TaskDisplayProps) {
  const images = imageUrls?.length ? imageUrls : imageUrl ? [imageUrl] : [];

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

        {images.length > 0 && (
          <div className={`mt-5 grid gap-4 ${images.length > 1 ? 'sm:grid-cols-2' : ''}`}>
            {images.map((src, index) => (
              <figure key={src} className="rounded-lg border border-gray-200 bg-gray-50 p-3">
                <img
                  src={src}
                  alt={imageCaptions?.[index] ?? `Task image ${index + 1}`}
                  className="rounded-md w-full max-h-72 object-contain bg-white"
                />
                <figcaption className="mt-2 text-center text-sm font-medium text-gray-700">
                  {imageCaptions?.[index] ?? `Photo ${index + 1}`}
                </figcaption>
              </figure>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
