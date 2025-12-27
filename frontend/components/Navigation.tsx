'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Image as ImageIcon, Settings, CreditCard } from 'lucide-react'
import { motion } from 'framer-motion'

const navItems = [
  { href: '/', label: 'Главная', icon: Home },
  { href: '/gallery', label: 'Галерея', icon: ImageIcon },
  { href: '/pricing', label: 'Тарифы', icon: CreditCard },
  { href: '/profile', label: 'Профиль', icon: Settings },
]

export default function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="glass mb-8 rounded-2xl p-2">
      <div className="flex items-center justify-center gap-2">
        {navItems.map(item => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                className={`
                  relative rounded-xl px-6 py-3 transition-colors
                  ${
                    isActive
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'text-slate-400 hover:bg-white/5 hover:text-white'
                  }
                `}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="flex items-center gap-2">
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </div>
                {isActive && (
                  <motion.div
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-400"
                    layoutId="activeTab"
                    initial={false}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </motion.div>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
