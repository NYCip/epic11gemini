'use client'

import { useState } from 'react'

export function EmergencyOverride() {
  const [confirmCode, setConfirmCode] = useState('')
  const [reason, setReason] = useState('')

  const handleHalt = () => {
    // Placeholder for halt functionality
    console.log('Halt initiated with reason:', reason)
  }

  return (
    <div className="bg-red-900/20 border border-red-600 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-red-500">EDWARD OVERRIDE ALPHA</h2>
      <p className="text-gray-300 mb-6">
        Emergency system control. Use only in critical situations.
      </p>
      <div className="flex space-x-4">
        <input
          type="text"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Reason for halt"
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-md"
        />
        <input
          type="text"
          value={confirmCode}
          onChange={(e) => setConfirmCode(e.target.value)}
          placeholder="Confirmation code"
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-md"
        />
        <button
          onClick={handleHalt}
          className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg"
        >
          HALT SYSTEM
        </button>
      </div>
    </div>
  )
}
