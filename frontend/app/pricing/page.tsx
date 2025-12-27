'use client'

import SpatialBackground from '@/components/SpatialBackground'
import GlassCard from '@/components/GlassCard'
import Navigation from '@/components/Navigation'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    price: '0₽',
    description: 'Для начала работы',
    features: ['5 квантований в день', 'Максимум 200x200px', 'Качество до 5', 'Базовая поддержка'],
    gradient: 'from-slate-600 to-slate-700',
  },
  {
    name: 'Pro',
    price: '499₽',
    period: '/месяц',
    description: 'Для профессионалов',
    features: [
      'Безлимитные квантования',
      'До 1000x1000px',
      'Максимальное качество',
      'Приоритетная поддержка',
      'API доступ',
      'Экспорт в разные форматы',
    ],
    gradient: 'from-emerald-500 to-teal-500',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'По запросу',
    description: 'Для команд',
    features: [
      'Все из Pro',
      'Выделенные ресурсы',
      'Кастомные интеграции',
      'SLA гарантии',
      'Персональный менеджер',
    ],
    gradient: 'from-purple-500 to-pink-500',
  },
]

export default function PricingPage() {
  return (
    <main className="relative min-h-screen">
      <SpatialBackground />

      <div className="container relative z-10 mx-auto px-4 py-12">
        <Navigation />

        <div className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold md:text-6xl">
            <span className="text-gradient">Тарифы</span>
          </h1>
          <p className="text-xl text-slate-400">Выберите план, который подходит вам</p>
        </div>

        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 md:grid-cols-3">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={plan.popular ? 'md:-mt-4' : ''}
            >
              <GlassCard className={`h-full ${plan.popular ? 'ring-2 ring-emerald-400' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-1 text-sm font-semibold text-white">
                      Популярный
                    </span>
                  </div>
                )}

                <div className="mb-8 text-center">
                  <h3 className="mb-2 text-2xl font-bold">{plan.name}</h3>
                  <div className="mb-2 flex items-baseline justify-center gap-2">
                    <span
                      className={`bg-gradient-to-r text-4xl font-bold ${plan.gradient} bg-clip-text text-transparent`}
                    >
                      {plan.price}
                    </span>
                    {plan.period && <span className="text-slate-400">{plan.period}</span>}
                  </div>
                  <p className="text-sm text-slate-400">{plan.description}</p>
                </div>

                <ul className="mb-8 space-y-4">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <Check className="mt-0.5 h-5 w-5 flex-shrink-0 text-emerald-400" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <motion.button
                  className={`w-full rounded-xl px-6 py-3 font-semibold ${
                    plan.popular
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
                      : 'glass text-white hover:bg-white/10'
                  }`}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {plan.name === 'Enterprise' ? 'Связаться' : 'Начать'}
                </motion.button>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>
    </main>
  )
}
