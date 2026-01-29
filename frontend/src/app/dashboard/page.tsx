'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle, Loader } from 'lucide-react'
import Header from '@/components/Header'
import ProtectedRoute from '@/components/ProtectedRoute'
import SignalTable from '@/components/SignalTable'
import OpenPositionsTable from '@/components/OpenPositionsTable'
import OrderHistoryTable from '@/components/OrderHistoryTable'
import ScannedCoins from '@/components/ScannedCoins'

export default function Dashboard() {
  const router = useRouter()
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/`, {
          credentials: 'include',
          headers: {
            'Accept': 'application/json'
          }
        })

        if (response.status === 401) {
          router.push('/login')
          return
        }

        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data')
        }

        const dashboardData = await response.json()
        setData(dashboardData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 60000) // Refresh every minute

    return () => clearInterval(interval)
  }, [router])

  return (
    <ProtectedRoute>
      <Header />
      <main className="min-h-screen bg-dark-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Trading Dashboard</h1>
            <p className="text-dark-400">Monitor your signals, positions, and trading activity</p>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-crypto-danger/10 border border-crypto-danger rounded-lg p-4 mb-8 flex items-gap-3">
              <AlertCircle className="w-5 h-5 text-crypto-danger flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-crypto-danger">Error</h3>
                <p className="text-sm text-dark-300">{error}</p>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <Loader className="w-8 h-8 animate-spin text-crypto-primary mx-auto mb-4" />
                <p className="text-dark-400">Loading dashboard...</p>
              </div>
            </div>
          )}

          {/* Content */}
          {!loading && data && (
            <div className="space-y-6">
              {/* Signals Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SignalTable
                  signals={data.buy_signals || []}
                  title="Buy Signals"
                  type="BUY"
                />
                <SignalTable
                  signals={data.sell_signals || []}
                  title="Sell Signals"
                  type="SELL"
                />
              </div>

              {/* Scanned Coins */}
              <ScannedCoins coins={data.scanned_coins || []} />

              {/* Positions */}
              <OpenPositionsTable positions={data.open_positions || []} />

              {/* Order History */}
              <OrderHistoryTable orders={data.order_history || []} />
            </div>
          )}
        </div>
      </main>
    </ProtectedRoute>
  )
}
