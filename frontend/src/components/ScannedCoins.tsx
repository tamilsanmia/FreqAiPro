import React from 'react'

interface ScannedCoinsProps {
  coins: string[]
}

export default function ScannedCoins({ coins }: ScannedCoinsProps) {
  if (!coins || coins.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Scanned Coins</h3>
        <div className="text-center py-8 text-dark-400">
          No coins scanned
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Scanned Coins ({coins.length})</h3>
      <div className="flex flex-wrap gap-2">
        {coins.map((coin, idx) => (
          <span key={idx} className="badge badge-primary">
            {coin}
          </span>
        ))}
      </div>
    </div>
  )
}
