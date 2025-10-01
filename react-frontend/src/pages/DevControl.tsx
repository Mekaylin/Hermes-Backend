import React, { useState } from 'react';

const DevControl: React.FC = () => {
  const [status, setStatus] = useState<string>('idle');
  const [output, setOutput] = useState<any>(null);

  const baseUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8001' : '';

  const [symbol, setSymbol] = useState<string>('SPY');
  const [startDate, setStartDate] = useState<string>('2020-01-01');
  const [endDate, setEndDate] = useState<string>('2021-01-01');
  const [file, setFile] = useState<File | null>(null);
  // Background job state
  const [bgRespId, setBgRespId] = useState<string | null>(null);
  const [bgStatus, setBgStatus] = useState<string | null>(null);
  const [bgOutput, setBgOutput] = useState<any>(null);

  const runTrain = async () => {
    setStatus('training');
    setOutput(null);
    try {
      const form = new FormData();
      form.append('epochs', '3');
      if (symbol) form.append('symbol', symbol);
      if (startDate) form.append('start_date', startDate);
      if (endDate) form.append('end_date', endDate);
      if (file) form.append('file', file, file.name);

      const res = await fetch(`${baseUrl}/api/agent/train`, { method: 'POST', body: form });
      const data = await res.json();
      setOutput(data);
      setStatus('trained');
    } catch (err) {
      setStatus('error');
      setOutput(String(err));
    }
  };

  const runTest = async () => {
    setStatus('testing');
    setOutput(null);
    try {
      const res = await fetch(`${baseUrl}/api/agent/test`, { method: 'POST' });
      const data = await res.json();
      setOutput(data);
      setStatus('tested');
    } catch (err) {
      setStatus('error');
      setOutput(String(err));
    }
  };

  return (
    <div className="p-6 bg-white rounded shadow">
      <h2 className="text-lg font-semibold mb-4">Developer Control</h2>

      <div className="mb-4">
        <a href="/agent-viz" className="px-3 py-2 bg-gray-700 text-white rounded">Open Agent Visualization</a>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2">Start backend (manual):</div>
        <pre className="bg-gray-100 p-2 rounded">cd backend && ./venv/bin/python -m uvicorn backend.simple_main:app --reload --port 8001</pre>
      </div>

      <div className="mb-4 p-4 border rounded">
        <h3 className="text-sm font-medium mb-2">Training Options</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-2">
          <input className="p-2 border rounded" value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="Symbol (e.g. SPY)" />
          <input type="date" className="p-2 border rounded" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          <input type="date" className="p-2 border rounded" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </div>
        <div className="mb-2">
          <label className="text-sm text-gray-600">Upload CSV (optional):</label>
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} />
        </div>
        <div className="flex space-x-2 mt-2">
          <button onClick={runTrain} className="px-3 py-2 bg-indigo-600 text-white rounded">Run Train</button>
          <button onClick={runTest} className="px-3 py-2 bg-green-600 text-white rounded">Run Test</button>
        </div>
      </div>

      <div>
        <div className="text-sm text-gray-600">Status: {status}</div>
        <pre className="mt-2 bg-gray-50 p-2 rounded w-full max-h-64 overflow-auto">{JSON.stringify(output, null, 2)}</pre>
      </div>

      {/* Background Jobs Panel */}
      <div className="mt-6 p-4 border rounded">
        <h3 className="text-sm font-medium mb-2">Background Jobs (Long responses)</h3>
        <div className="grid grid-cols-1 gap-2 mb-2">
          <textarea placeholder="Prompt for long response" id="bg-input" className="w-full p-2 border rounded" />
        </div>
        <div className="flex space-x-2">
          <button
            onClick={async () => {
              const input = (document.getElementById('bg-input') as HTMLTextAreaElement).value || 'Long running task';
              setBgStatus('starting');
              try {
                const form = new FormData();
                form.append('model', 'o3');
                form.append('input_text', input);
                const res = await fetch(`${baseUrl}/api/background/start`, { method: 'POST', body: form });
                const data = await res.json();
                setBgRespId(data.response.id || data.response['id']);
                setBgStatus(data.response.status || 'queued');
                setBgOutput(data.response);
              } catch (e) {
                setBgStatus('error');
                setBgOutput(String(e));
              }
            }}
            className="px-3 py-2 bg-indigo-600 text-white rounded"
          >
            Start Background
          </button>

          <button
            onClick={async () => {
              if (!bgRespId) return;
              setBgStatus('polling');
              try {
                const res = await fetch(`${baseUrl}/api/background/status/${bgRespId}`);
                const data = await res.json();
                setBgStatus(data.response.status || 'unknown');
                setBgOutput(data.response);
              } catch (e) {
                setBgStatus('error');
                setBgOutput(String(e));
              }
            }}
            className="px-3 py-2 bg-yellow-600 text-white rounded"
          >
            Poll Status
          </button>

          <button
            onClick={async () => {
              if (!bgRespId) return;
              try {
                const form = new FormData();
                form.append('resp_id', bgRespId);
                const res = await fetch(`${baseUrl}/api/background/cancel`, { method: 'POST', body: form });
                const data = await res.json();
                setBgStatus(data.response.status || 'cancelled');
                setBgOutput(data.response);
              } catch (e) {
                setBgStatus('error');
                setBgOutput(String(e));
              }
            }}
            className="px-3 py-2 bg-red-600 text-white rounded"
          >
            Cancel
          </button>
        </div>

        <div className="mt-3">
          <div className="text-sm text-gray-600">Background Response ID: {bgRespId}</div>
          <div className="text-sm text-gray-600">Status: {bgStatus}</div>
          <pre className="mt-2 bg-gray-50 p-2 rounded w-full max-h-64 overflow-auto">{JSON.stringify(bgOutput, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
};

export default DevControl;
