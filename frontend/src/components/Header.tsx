'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Menu, X, LogOut, Home, TrendingUp, BarChart3, Settings } from 'lucide-react'

export default function Header() {
  const router = useRouter()
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    router.push('/login')
  }

  return (
    <header className="sticky top-0 z-50 bg-dark-900/95 border-b border-dark-800 backdrop-blur">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-crypto-primary to-crypto-info flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <span className="hidden sm:inline text-xl font-bold gradient-text">FreqAiPro</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <Link href="/dashboard" className="text-dark-300 hover:text-white transition">
              Dashboard
            </Link>
            <Link href="/signals" className="text-dark-300 hover:text-white transition">
              Signals
            </Link>
            <Link href="/positions" className="text-dark-300 hover:text-white transition">
              Positions
            </Link>
            <Link href="/history" className="text-dark-300 hover:text-white transition">
              History
            </Link>
            <Link href="/analytics" className="text-dark-300 hover:text-white transition">
              Analytics
            </Link>
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-4">
            <Link href="/settings" className="p-2 hover:bg-dark-800 rounded-lg transition">
              <Settings className="w-5 h-5 text-dark-300" />
            </Link>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-dark-800 rounded-lg transition text-dark-300"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 hover:bg-dark-800 rounded-lg transition"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <nav className="md:hidden pb-4 space-y-2">
            <Link
              href="/dashboard"
              className="block px-4 py-2 text-dark-300 hover:bg-dark-800 rounded-lg transition"
            >
              Dashboard
            </Link>
            <Link
              href="/signals"
              className="block px-4 py-2 text-dark-300 hover:bg-dark-800 rounded-lg transition"
            >
              Signals
            </Link>
            <Link
              href="/positions"
              className="block px-4 py-2 text-dark-300 hover:bg-dark-800 rounded-lg transition"
            >
              Positions
            </Link>
            <Link
              href="/history"
              className="block px-4 py-2 text-dark-300 hover:bg-dark-800 rounded-lg transition"
            >
              History
            </Link>
            <Link
              href="/analytics"
              className="block px-4 py-2 text-dark-300 hover:bg-dark-800 rounded-lg transition"
            >
              Analytics
            </Link>
          </nav>
        )}
      </div>
    </header>
  )
}
