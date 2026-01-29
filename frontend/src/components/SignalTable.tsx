import React from 'react'
import clsx from 'clsx'

interface SignalTableProps {
  signals: Array<{
    coin: string
    price: string
    strength: number
    st_level: string
    timeframe: string
    tradingview_url: string
    signal_type: 'BUY' | 'SELL'
  }>
  title: string
  type: 'BUY' | 'SELL'
}

export default function SignalTable({ signals, title, type }: SignalTableProps) {
  const badgeClass = type === 'BUY' ? 'badge-success' : 'badge-danger'
  const iconColor = type === 'BUY' ? 'text-crypto-success' : 'text-crypto-danger'

  if (!signals || signals.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <div className="text-center py-8 text-dark-400">
          No {type.toLowerCase()} signals available
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <span className={`w-3 h-3 rounded-full ${badgeClass.replace('badge-', 'bg-')}`}></span>
        {title}
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-dark-400 text-xs font-semibold uppercase tracking-wider border-b border-dark-800">
              <th className="text-left py-3 px-4">Coin</th>
              <th className="text-right py-3 px-4">Price</th>
              <th className="text-right py-3 px-4">Strength</th>
              <th className="text-right py-3 px-4">ST Level</th>
              <th className="text-center py-3 px-4">Timeframe</th>
            </tr>
          </thead>
          <tbody>
            {signals.map((signal, idx) => (
              <tr key={idx} className="table-row">
                <td className="py-3 px-4">
                  <a
                    href={signal.tradingview_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-crypto-primary hover:text-crypto-info transition"
                  >
                    <span className="w-6 h-6 rounded-full bg-dark-800 flex items-center justify-center text-xs font-bold">
                      ₿
                    </span>
                    {signal.coin}
                  </a>
                </td>
                <td className={clsx('text-right py-3 px-4 font-semibold', iconColor)}>
                  {signal.price}
                </td>
                <td className="text-right py-3 px-4">
                  <div className="flex justify-end">
                    <span className="bg-dark-800 px-2.5 py-1 rounded text-dark-200">
                      {Number.isFinite(Number(signal.strength))
                        ? Number(signal.strength).toFixed(2)
                        : 'N/A'}
                    </span>
                  </div>
                </td>
                <td className="text-right py-3 px-4 text-dark-300">{signal.st_level}</td>
                <td className="text-center py-3 px-4">
                  <span className={clsx('badge', badgeClass)}>{signal.timeframe}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
