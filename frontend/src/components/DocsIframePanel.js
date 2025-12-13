export default function DocsIframePanel({ docUrl }) {
  if (!docUrl) {
    return (
      <div className="h-full border-l flex items-center justify-center text-gray-500">
        Run code to open relevant documentation
      </div>
    );
  }

  return (
    <div className="h-full border-l">
      <iframe
        key={docUrl}
        src={docUrl}
        title="Library Docs"
        className="w-full h-full"
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
      />
    </div>
  );
}
