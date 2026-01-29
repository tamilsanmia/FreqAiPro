'use client'

import React from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-dark-950">
      {/* Navigation */}
      <nav className="border-b border-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold gradient-text">FreqAiPro</h1>
          <div className="flex gap-4">
            <Link href="/login" className="btn btn-secondary">
              Login
            </Link>
            <Link href="/register" className="btn btn-primary">
              Register
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-20">
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            Professional Crypto <span className="gradient-text">Trading Dashboard</span>
          </h2>
          <p className="text-xl text-dark-400 mb-8 max-w-2xl mx-auto">
            Monitor real-time trading signals, manage positions, and optimize your crypto trading strategy with advanced analytics
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/register" className="btn btn-primary px-8 py-3 text-lg">
              Get Started <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
            <Link href="/login" className="btn btn-secondary px-8 py-3 text-lg">
              Login
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 py-12">
          <div className="card">
            <div className="w-12 h-12 rounded-lg bg-crypto-primary/10 flex items-center justify-center mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Real-Time Signals</h3>
            <p className="text-dark-400">
              AI-powered trading signals with confidence scores updated every minute
            </p>
          </div>

          <div className="card">
            <div className="w-12 h-12 rounded-lg bg-crypto-success/10 flex items-center justify-center mb-4">
              <span className="text-2xl">💼</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Position Management</h3>
            <p className="text-dark-400">
              Track open positions with dynamic stop-losses and take-profit levels
            </p>
          </div>

          <div className="card">
            <div className="w-12 h-12 rounded-lg bg-crypto-info/10 flex items-center justify-center mb-4">
              <span className="text-2xl">📈</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Advanced Analytics</h3>
            <p className="text-dark-400">
              Comprehensive charts and metrics for performance analysis
            </p>
          </div>

          <div className="card">
            <div className="w-12 h-12 rounded-lg bg-crypto-warning/10 flex items-center justify-center mb-4">
              <span className="text-2xl">🚨</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Instant Alerts</h3>
            <p className="text-dark-400">
              Get notified instantly when signals are generated or positions change
            </p>
          </div>

          <div className="card">
            <div className="w-12 h-12 rounded-lg bg-crypto-primary/10 flex items-center justify-center mb-4">
              <span className="text-2xl">⚙️</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Multi-Timeframe Analysis</h3>
            <p className="text-dark-400">
              Simultaneous analysis across 5m, 15m, 30m, and 1h timeframes
            </p>
          </div>

          <div className="card">
            <div className="w-12 h-12 rounded-lg bg-crypto-success/10 flex items-center justify-center mb-4">
              <span className="text-2xl">🔐</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Secure & Reliable</h3>
            <p className="text-dark-400">
              Enterprise-grade security with encrypted data and secure authentication
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
