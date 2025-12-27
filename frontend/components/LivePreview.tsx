'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, XCircle } from 'lucide-react'

interface LivePreviewProps {
  text?: string
  status: 'idle' | 'processing' | 'completed' | 'error' | 'cancelled'
  progress?: number
  progressMessage?: string
  error?: string
  className?: string
}

export default function LivePreview({
  text,
  status,
  progress = 0,
  progressMessage,
  error,
  className,
}: LivePreviewProps) {
  return (
    <div className={className}>
      <div className="mb-4 space-y-2">
        <div className="flex items-center gap-2">
          <div className="relative h-5 w-5">
            {status === 'processing' && (
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-emerald-400 border-t-transparent"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
            )}
            {status === 'completed' && (
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              </motion.div>
            )}
            {status === 'error' && (
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                <XCircle className="h-5 w-5 text-red-400" />
              </motion.div>
            )}
            {status === 'cancelled' && (
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                <XCircle className="h-5 w-5 text-orange-400" />
              </motion.div>
            )}
            {status === 'idle' && <div className="h-5 w-5 rounded-full bg-slate-600" />}
          </div>
          <span className="text-sm font-medium">
            {status === 'processing' && (progressMessage || 'Обработка...')}
            {status === 'completed' && 'Готово'}
            {status === 'idle' && 'Предпросмотр'}
            {status === 'error' && (progressMessage || 'Ошибка')}
            {status === 'cancelled' && (progressMessage || 'Отменено')}
          </span>
        </div>

        {status === 'processing' && (
          <div className="space-y-1">
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
              <motion.div
                className="h-full bg-gradient-to-r from-emerald-500 to-teal-500"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-400">
              <span>{progressMessage || 'Обработка...'}</span>
              <span>{progress}%</span>
            </div>
          </div>
        )}

        {status === 'error' && error && (
          <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>

      <motion.div
        className="glass max-h-64 overflow-auto rounded-2xl p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {text ? (
          <pre
            className="quant-preview whitespace-pre font-mono leading-none text-white/90"
            style={{ fontSize: '1pt' }}
          >
            {text}
          </pre>
        ) : (
          <div className="flex h-32 items-center justify-center text-slate-500">
            <p className="text-sm">Загрузите изображение для предпросмотра</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}
