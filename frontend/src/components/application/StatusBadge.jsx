/**
 * StatusBadge — colored badge showing application/document status.
 * TODO: Style with Tailwind
 */
export default function StatusBadge({ status }) {
  const colors = {
    created: 'bg-gray-100 text-gray-700',
    processing: 'bg-blue-100 text-blue-700',
    review: 'bg-yellow-100 text-yellow-700',
    decided: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
    uploaded: 'bg-gray-100 text-gray-600',
    extracted: 'bg-purple-100 text-purple-700',
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100'}`}>
      {status}
    </span>
  );
}
