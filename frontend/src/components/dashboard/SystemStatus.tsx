'use client'

import { useState, useEffect } from 'react'

export function SystemStatus() {
  const [status, setStatus] = useState('Loading...')

  useEffect(() => {
    // In a real application, you would fetch this data from an API
    setStatus('All systems operational')
  }, [])

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-xl font-bold mb-4">System Status</h2>
      <p>{status}</p>
    </div>
  )
}