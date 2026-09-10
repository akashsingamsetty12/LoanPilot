/** FileUpload — Drag-and-drop multi-file upload."""
export default function FileUpload({ files, setFiles, accept = '.pdf,.jpg,.jpeg,.png' }) {
  // TODO: Implement drag-and-drop with progress bars
  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
      <p>Drag & drop documents here (PDF, JPG, PNG)</p>
      <input type="file" multiple accept={accept} onChange={(e) => setFiles([...e.target.files])} />
      {files.length > 0 && <p>{files.length} file(s) selected</p>}
    </div>
  );
}
