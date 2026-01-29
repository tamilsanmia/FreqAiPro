import React from 'react'
import clsx from 'clsx'

interface OrderHistory {
  order_number: number
  coin: string
  entry_price: number
  exit_price: number | null
  profit_pct: number | null
  exit_reason: string
  duration: string
  timeframe: string
  tradingview_url: string
}

interface OrderHistoryTableProps {
  orders: OrderHistory[]
}

export default function OrderHistoryTable({ orders }: OrderHistoryTableProps) {
  if (!orders || orders.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Order History</h3>
        <div className="text-center py-8 text-dark-400">
          No order history
        </div>
      </div>
    )
  }

  const getExitReasonColor = (reason: string) => {
    if (reason.toLowerCase().includes('tp')) return 'text-crypto-success'
    if (reason.toLowerCase().includes('sl')) return 'text-crypto-danger'
    return 'text-crypto-warning'
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Order History</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-dark-400 text-xs font-semibold uppercase tracking-wider border-b border-dark-800">
              <th className="text-left py-3 px-4">Order #</th>
              <th className="text-left py-3 px-4">Coin</th>
              <th className="text-right py-3 px-4">Entry</th>
              <th className="text-right py-3 px-4">Exit</th>
              <th className="text-right py-3 px-4">Profit %</th>
              <th className="text-left py-3 px-4">Reason</th>
              <th className="text-center py-3 px-4">Duration</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order, idx) => (
              <tr key={idx} className="table-row">
                <td className="py-3 px-4 font-semibold">{order.order_number}</td>
                <td className="py-3 px-4">
                  <a
                    href={order.tradingview_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-crypto-primary hover:text-crypto-info transition"
                  >
                    <span className="w-6 h-6 rounded-full bg-dark-800 flex items-center justify-center text-xs font-bold">
                      ₿
                    </span>
                    {order.coin}
                  </a>
                  <span className="badge badge-primary mt-1">{order.timeframe}</span>
                </td>
                <td className="text-right py-3 px-4">{order.entry_price.toFixed(4)}</td>
                <td className="text-right py-3 px-4">
                  {order.exit_price ? order.exit_price.toFixed(4) : 'N/A'}
                </td>
                <td className={clsx(
                  'text-right py-3 px-4 font-semibold',
                  order.profit_pct !== null && order.profit_pct > 0
                    ? 'text-crypto-success'
                    : order.profit_pct !== null
                    ? 'text-crypto-danger'
                    : 'text-dark-400'
                )}>
                  {order.profit_pct !== null ? `${order.profit_pct.toFixed(2)}%` : 'N/A'}
                </td>
                <td className={clsx('py-3 px-4 text-sm font-medium', getExitReasonColor(order.exit_reason))}>
                  {order.exit_reason}
                </td>
                <td className="text-center py-3 px-4 text-dark-300">{order.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
