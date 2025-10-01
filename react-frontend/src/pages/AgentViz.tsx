import React, {useEffect, useState} from 'react';

export default function AgentViz() {
  const [imgSrc, setImgSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('/api/agents/visualize');
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        setImgSrc(url);
      } catch (e: any) {
        setError(e.message || 'Failed to fetch graph');
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-semibold mb-4">Agent Visualization</h2>
      {loading && <p>Generating graph...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {imgSrc && (
        <div>
          <img src={imgSrc} alt="Agent Graph" style={{maxWidth: '100%', height: 'auto'}} />
        </div>
      )}
    </div>
  );
}
