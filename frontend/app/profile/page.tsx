'use client'

import { useState, useEffect } from 'react'
import SpatialBackground from '@/components/SpatialBackground'
import GlassCard from '@/components/GlassCard'
import Navigation from '@/components/Navigation'
import { Key, History, Settings, Download, Copy, Check, XCircle } from 'lucide-react'
import {
  getHistory,
  downloadGalleryItem,
  getActiveTasks,
  cancelAllActiveTasks,
  type HistoryItem,
} from '@/lib/api'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [activeTasks, setActiveTasks] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [copiedKey, setCopiedKey] = useState(false)
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    loadHistory()
    loadActiveTasks()
    // Refresh active tasks every 5 seconds
    const interval = setInterval(() => {
      loadActiveTasks()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadHistory = async () => {
    try {
      setLoading(true)
      const data = await getHistory(50)
      setHistory(data)
    } catch (error) {
      toast.error('Ошибка при загрузке истории')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadActiveTasks = async () => {
    try {
      const data = await getActiveTasks()
      setActiveTasks(data)
    } catch (error) {
      // Silently fail for active tasks refresh
      console.error('Error loading active tasks:', error)
    }
  }

  const handleCancelAll = async () => {
    if (activeTasks.length === 0) {
      toast.error('Нет активных задач для отмены')
      return
    }

    if (
      !window.confirm(
        `Вы уверены, что хотите отменить все активные задачи (${activeTasks.length})?`
      )
    ) {
      return
    }

    try {
      setCancelling(true)
      const result = await cancelAllActiveTasks()
      toast.success(`Отменено задач: ${result.cancelled_count}`)
      // Reload history and active tasks
      await Promise.all([loadHistory(), loadActiveTasks()])
    } catch (error) {
      toast.error('Ошибка при отмене задач')
      console.error(error)
    } finally {
      setCancelling(false)
    }
  }

  const handleCopyKey = () => {
    // In a real app, this would be an actual API key
    const apiKey =
      'qtxt_live_' + Array.from({ length: 32 }, () => Math.random().toString(36).charAt(2)).join('')
    navigator.clipboard.writeText(apiKey)
    setCopiedKey(true)
    toast.success('API ключ скопирован')
    setTimeout(() => setCopiedKey(false), 2000)
  }

  const handleDownload = async (taskId: string) => {
    try {
      await downloadGalleryItem(taskId)
      toast.success('Файл скачан')
    } catch (error) {
      toast.error('Ошибка при скачивании файла')
      console.error(error)
    }
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Неизвестно'
    try {
      return new Date(dateStr).toLocaleString('ru-RU')
    } catch {
      return dateStr
    }
  }

  return (
    <main className="relative min-h-screen">
      <SpatialBackground />

      <div className="container relative z-10 mx-auto px-4 py-12">
        <Navigation />

        <div className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold md:text-6xl">
            <span className="text-gradient">Профиль</span>
          </h1>
        </div>

        <div className="mx-auto grid max-w-4xl grid-cols-1 gap-6 md:grid-cols-2">
          {/* API Keys */}
          <GlassCard>
            <div className="mb-4 flex items-center gap-3">
              <Key className="h-6 w-6 text-emerald-400" />
              <h2 className="text-xl font-semibold">API Ключи</h2>
            </div>
            <div className="space-y-3">
              <div className="glass rounded-lg p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium">Production Key</span>
                  <button
                    onClick={handleCopyKey}
                    className="flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300"
                  >
                    {copiedKey ? (
                      <>
                        <Check className="h-3 w-3" />
                        Скопировано
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        Скопировать
                      </>
                    )}
                  </button>
                </div>
                <code className="break-all font-mono text-xs text-slate-400">
                  qtxt_live_••••••••••••••••
                </code>
              </div>
              <button className="glass w-full rounded-lg px-4 py-2 text-sm font-medium transition-colors hover:bg-white/10">
                Создать новый ключ
              </button>
            </div>
          </GlassCard>

          {/* History */}
          <GlassCard>
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <History className="h-6 w-6 text-emerald-400" />
                <h2 className="text-xl font-semibold">История</h2>
                {activeTasks.length > 0 && (
                  <span className="rounded-full bg-blue-500/20 px-2 py-1 text-xs text-blue-400">
                    {activeTasks.length} активных
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {activeTasks.length > 0 && (
                  <button
                    onClick={handleCancelAll}
                    disabled={cancelling}
                    className="flex items-center gap-2 rounded-lg bg-red-500/20 px-3 py-1.5 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/30 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <XCircle className="h-4 w-4" />
                    <span>{cancelling ? 'Отмена...' : 'Отменить все'}</span>
                  </button>
                )}
                <button
                  onClick={loadHistory}
                  className="text-sm text-emerald-400 hover:text-emerald-300"
                >
                  Обновить
                </button>
              </div>
            </div>
            <div className="max-h-96 space-y-2 overflow-y-auto">
              {loading ? (
                <div className="py-8 text-center text-slate-400">Загрузка...</div>
              ) : history.length === 0 ? (
                <div className="py-8 text-center text-slate-400">История пуста</div>
              ) : (
                history.map(item => (
                  <div
                    key={item.task_id}
                    className="glass flex items-center justify-between rounded-lg p-3"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-medium">
                        {item.width && item.height
                          ? `${item.width}×${item.height}px`
                          : 'Квантование'}
                      </p>
                      <div className="mt-1 flex items-center gap-2 text-xs text-slate-400">
                        <span
                          className={`${
                            item.status === 'completed'
                              ? 'text-emerald-400'
                              : item.status === 'error'
                                ? 'text-red-400'
                                : item.status === 'cancelled'
                                  ? 'text-orange-400'
                                  : 'text-yellow-400'
                          }`}
                        >
                          {item.status === 'completed'
                            ? '✓ Готово'
                            : item.status === 'error'
                              ? '✗ Ошибка'
                              : item.status === 'cancelled'
                                ? '⊘ Отменено'
                                : '⏳ Обработка'}
                        </span>
                        <span>•</span>
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                      {item.error && <p className="mt-1 text-xs text-red-400">{item.error}</p>}
                    </div>
                    {item.status === 'completed' && (
                      <button
                        onClick={() => handleDownload(item.task_id)}
                        className="ml-2 text-emerald-400 hover:text-emerald-300"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          </GlassCard>

          {/* Settings */}
          <GlassCard className="md:col-span-2">
            <div className="mb-6 flex items-center gap-3">
              <Settings className="h-6 w-6 text-emerald-400" />
              <h2 className="text-xl font-semibold">Настройки</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium">Тема</label>
                <select className="glass w-full rounded-lg px-4 py-2 text-sm">
                  <option>Темная</option>
                  <option>Светлая</option>
                  <option>Системная</option>
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium">Язык</label>
                <select className="glass w-full rounded-lg px-4 py-2 text-sm">
                  <option>Русский</option>
                  <option>English</option>
                </select>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </main>
  )
}
