'use client';

import { useEffect, useState } from 'react';
import { apiService } from '@/lib/api';

export default function TestPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Starting API call...');
        const result = await apiService.getNextRace();
        console.log('API result:', result);
        console.log('Result type:', typeof result);
        console.log('Result keys:', Object.keys(result));
        setData(result);
        setLoading(false);
      } catch (err: any) {
        console.error('API Error:', err);
        console.error('Error message:', err.message);
        console.error('Error response:', err.response);
        setError(err.message || 'Unknown error');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <h1 className="text-4xl font-bold mb-8">API Test Page</h1>
      
      {loading && <div>Loading...</div>}
      
      {error && (
        <div className="bg-red-900/30 border border-red-500 p-4 rounded">
          <h2 className="text-xl font-bold mb-2">Error:</h2>
          <pre>{error}</pre>
        </div>
      )}
      
      {data && (
        <div className="bg-green-900/30 border border-green-500 p-4 rounded">
          <h2 className="text-xl font-bold mb-2">Success! Data received:</h2>
          <pre className="whitespace-pre-wrap">{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
