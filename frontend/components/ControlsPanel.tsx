'use client'

import { motion } from 'framer-motion'
import { Sparkles, X } from 'lucide-react'

interface ControlsPanelProps {
  width: number
  height: number
  quality: number
  onWidthChange: (value: number) => void
  onHeightChange: (value: number) => void
  onQualityChange: (value: number) => void
  onQuantize: () => void
  onCancel?: () => void
  isProcessing: boolean
}

export default function ControlsPanel({
  width,
  height,
  quality,
  onWidthChange,
  onHeightChange,
  onQualityChange,
  onQuantize,
  onCancel,
  isProcessing,
}: ControlsPanelProps) {
  return (
    <div className="space-y-6">
      {/* Width Slider */}
      <div>
        <label className="mb-3 block text-sm font-medium">Ширина: {width}px</label>
        <input
          type="range"
          min="64"
          max="320"
          value={width}
          onChange={e => onWidthChange(Number(e.target.value))}
          className="chrome-none h-2 w-full appearance-none rounded-lg bg-slate-800 accent-emerald-500"
        />
        <div className="mt-1 flex justify-between text-xs text-slate-400">
          <span>64px</span>
          <span>320px</span>
        </div>
      </div>

      {/* Height Slider */}
      <div>
        <label className="mb-3 block text-sm font-medium">Высота: {height}px</label>
        <input
          type="range"
          min="64"
          max="320"
          value={height}
          onChange={e => onHeightChange(Number(e.target.value))}
          className="chrome-none h-2 w-full appearance-none rounded-lg bg-slate-800 accent-emerald-500"
        />
        <div className="mt-1 flex justify-between text-xs text-slate-400">
          <span>64px</span>
          <span>320px</span>
        </div>
      </div>

      {/* Quality Slider */}
      <div>
        <label className="mb-3 block text-sm font-medium">Качество: {quality}/10</label>
        <input
          type="range"
          min="1"
          max="10"
          value={quality}
          onChange={e => onQualityChange(Number(e.target.value))}
          className="chrome-none h-2 w-full appearance-none rounded-lg bg-slate-800 accent-emerald-500"
        />
        <div className="mt-1 flex justify-between text-xs text-slate-400">
          <span>Быстро</span>
          <span>Максимум</span>
        </div>
      </div>

      {/* Quantize/Cancel Button */}
      {isProcessing && onCancel ? (
        <motion.button
          onClick={onCancel}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-red-500 to-orange-500 px-6 py-4 font-semibold text-white"
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.2 }}
        >
          <X className="h-5 w-5" />
          <span>Отменить</span>
        </motion.button>
      ) : (
        <motion.button
          onClick={onQuantize}
          disabled={isProcessing}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-6 py-4 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.2 }}
        >
          {isProcessing ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              >
                <Sparkles className="h-5 w-5" />
              </motion.div>
              <span>Обработка...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5" />
              <span>Квантовать</span>
            </>
          )}
        </motion.button>
      )}
    </div>
  )
}
