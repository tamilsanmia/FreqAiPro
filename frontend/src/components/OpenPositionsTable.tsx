import React from 'react'
import clsx from 'clsx'

interface Position {
  order_number: number
  coin: string
  entry_price: number
  current_price: number | null
  profit_pct: number | null
  sl: number
  tp1: number
  tp2: number
  tp3: number
  duration: string
  timeframe: string
  tradingview_url: string
}

interface OpenPositionsTableProps {
  positions: Position[]
}

export default function OpenPositionsTable({ positions }: OpenPositionsTableProps) {
  if (!positions || positions.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Open Positions</h3>
        <div className="text-center py-8 text-dark-400">
          No open positions
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">
        Open Positions <span className="text-dark-400 font-normal">({positions.length})</span>
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-dark-400 text-xs font-semibold uppercase tracking-wider border-b border-dark-800">
              <th className="text-left py-3 px-4">Order #</th>
              <th className="text-left py-3 px-4">Coin</th>
              <th className="text-right py-3 px-4">Entry</th>
              <th className="text-right py-3 px-4">Current</th>
              <th className="text-right py-3 px-4">Profit %</th>
              <th className="text-right py-3 px-4">SL</th>
              <th className="text-right py-3 px-4">TP1 / TP2 / TP3</th>
              <th className="text-center py-3 px-4">Duration</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos, idx) => (
              <tr key={idx} className="table-row">
                <td className="py-3 px-4 font-semibold">{pos.order_number}</td>
                <td className="py-3 px-4">
                  <a
                    href={pos.tradingview_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-crypto-primary hover:text-crypto-info transition"
                  >
                    <span className="w-6 h-6 rounded-full bg-dark-800 flex items-center justify-center text-xs font-bold">
                      ₿
                    </span>
                    {pos.coin}
                  </a>
                  <span className="badge badge-primary mt-1">{pos.timeframe}</span>
                </td>
                <td className="text-right py-3 px-4 text-crypto-info">{pos.entry_price.toFixed(4)}</td>
                <td className="text-right py-3 px-4 text-crypto-info">
                  {pos.current_price ? pos.current_price.toFixed(4) : 'N/A'}
                </td>
                <td className={clsx(
                  'text-right py-3 px-4 font-semibold',
                  pos.profit_pct !== null && pos.profit_pct > 0
                    ? 'text-crypto-success'
                    : pos.profit_pct !== null
                    ? 'text-crypto-danger'
                    : 'text-dark-400'
                )}>
                  {pos.profit_pct !== null ? `${pos.profit_pct.toFixed(2)}%` : 'N/A'}
                </td>
                <td className="text-right py-3 px-4 text-crypto-danger">{pos.sl.toFixed(4)}</td>
                <td className="text-right py-3 px-4 text-crypto-success text-xs">
                  {pos.tp1.toFixed(4)} / {pos.tp2.toFixed(4)} / {pos.tp3.toFixed(4)}
                </td>
                <td className="text-center py-3 px-4 text-dark-300">{pos.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
