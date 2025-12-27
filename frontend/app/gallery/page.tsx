'use client'

import { useState, useEffect } from 'react'
import SpatialBackground from '@/components/SpatialBackground'
import GlassCard from '@/components/GlassCard'
import Navigation from '@/components/Navigation'
import { motion } from 'framer-motion'
import { Download, Eye, Trash2, Loader2, XCircle } from 'lucide-react'
import { getGalleryItems, previewGalleryItem, downloadGalleryItem, deleteGalleryItem, cancelTask, type GalleryItem } from '@/lib/api'
import toast from 'react-hot-toast'
import LivePreview from '@/components/LivePreview'

export default function GalleryPage() {
  const [items, setItems] = useState<GalleryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [previewTaskId, setPreviewTaskId] = useState<string | null>(null)
  const [previewText, setPreviewText] = useState<string>('')
  const [previewLoading, setPreviewLoading] = useState(false)

  const loadGallery = async () => {
    try {
      setLoading(true)
      const data = await getGalleryItems(100)
      setItems(data)
    } catch (error) {
      toast.error('Ошибка при загрузке галереи')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadGallery()
  }, [])

  const handlePreview = async (taskId: string) => {
    try {
      setPreviewLoading(true)
      setPreviewTaskId(taskId)
      const text = await previewGalleryItem(taskId, 100)
      setPreviewText(text)
    } catch (error) {
      toast.error('Ошибка при загрузке предпросмотра')
      console.error(error)
    } finally {
      setPreviewLoading(false)
    }
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

  const handleDelete = async (taskId: string) => {
    const item = items.find(i => i.task_id === taskId)
    const isActive = item?.status === 'processing' || item?.status === 'pending' || item?.status === 'started'

    if (!confirm(isActive ? 'Вы уверены, что хотите отменить эту задачу?' : 'Вы уверены, что хотите удалить этот файл?')) {
      return
    }

    try {
      if (isActive) {
        // Cancel active task
        await cancelTask(taskId)
        toast.success('Задача отменена')
      } else {
        // Delete completed task
        await deleteGalleryItem(taskId)
        toast.success('Файл удален')
      }
      loadGallery()
      if (previewTaskId === taskId) {
        setPreviewTaskId(null)
        setPreviewText('')
      }
    } catch (error) {
      toast.error(isActive ? 'Ошибка при отмене задачи' : 'Ошибка при удалении файла')
      console.error(error)
    }
  }

  const formatDate = (timestamp: string | number) => {
    if (typeof timestamp === 'string') {
      // Try to parse as Unix timestamp
      const num = parseInt(timestamp, 10)
      if (!isNaN(num)) {
        return new Date(num * 1000).toLocaleDateString('ru-RU', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      }
      // Try to parse as date string
      try {
        return new Date(timestamp).toLocaleDateString('ru-RU', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      } catch {
        return timestamp
      }
    }
    if (typeof timestamp === 'number') {
      return new Date(timestamp * 1000).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    }
    return 'Неизвестно'
  }

  return (
    <main className="relative min-h-screen">
      <SpatialBackground />

      <div className="container relative z-10 mx-auto px-4 py-12">
        <Navigation />

        <div className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold md:text-6xl">
            <span className="text-gradient">Галерея</span>
          </h1>
          <p className="text-xl text-slate-400">Примеры готовых QuantTxt файлов</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
          </div>
        ) : items.length === 0 ? (
          <GlassCard>
            <div className="py-12 text-center">
              <p className="text-slate-400">Галерея пуста. Создайте первое квантование на главной странице!</p>
            </div>
          </GlassCard>
        ) : (
          <>
            <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {items.map((item, index) => (
                <motion.div
                  key={item.task_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <GlassCard hover className="h-full">
                    <div className="mb-4 flex aspect-square items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20">
                      {item.status === 'processing' || item.status === 'pending' || item.status === 'started' ? (
                        <Loader2 className="h-12 w-12 animate-spin text-emerald-400" />
                      ) : item.status === 'error' ? (
                        <XCircle className="h-12 w-12 text-red-400" />
                      ) : (
                        <span className="text-4xl">📄</span>
                      )}
                    </div>
                    <h3 className="mb-2 font-semibold">{item.filename}</h3>
                    <div className="mb-4 space-y-1 text-sm text-slate-400">
                      {item.width && item.height && (
                        <p>
                          {item.width}×{item.height}px
                        </p>
                      )}
                      {item.quality && <p>Качество: {item.quality}/10</p>}
                      <p>{formatDate(item.created_at)}</p>
                      <p className={`font-medium ${
                        item.status === 'processing' || item.status === 'pending' || item.status === 'started'
                          ? 'text-yellow-400'
                          : item.status === 'error'
                          ? 'text-red-400'
                          : item.status === 'completed'
                          ? 'text-emerald-400'
                          : 'text-slate-400'
                      }`}>
                        {item.status === 'processing' || item.status === 'pending' || item.status === 'started'
                          ? 'Обработка...'
                          : item.status === 'error'
                          ? 'Ошибка'
                          : item.status === 'completed'
                          ? 'Готово'
                          : item.status === 'cancelled'
                          ? 'Отменено'
                          : item.status}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {(item.status === 'completed' || item.status === 'error') && (
                        <>
                          <button
                            onClick={() => handlePreview(item.task_id)}
                            disabled={item.status !== 'completed'}
                            className="glass flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Eye className="mx-auto h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDownload(item.task_id)}
                            disabled={item.status !== 'completed'}
                            className="glass flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Download className="mx-auto h-4 w-4" />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleDelete(item.task_id)}
                        className={`glass rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                          item.status === 'processing' || item.status === 'pending' || item.status === 'started'
                            ? 'text-yellow-400 hover:bg-yellow-400/10'
                            : 'text-red-400 hover:bg-red-400/10'
                        }`}
                        title={item.status === 'processing' || item.status === 'pending' || item.status === 'started' ? 'Отменить' : 'Удалить'}
                      >
                        {item.status === 'processing' || item.status === 'pending' || item.status === 'started' ? (
                          <XCircle className="h-4 w-4" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </GlassCard>
                </motion.div>
              ))}
            </div>

            {previewTaskId && (
              <GlassCard>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Предпросмотр</h2>
                  <button
                    onClick={() => {
                      setPreviewTaskId(null)
                      setPreviewText('')
                    }}
                    className="text-sm text-slate-400 hover:text-white"
                  >
                    Закрыть
                  </button>
                </div>
                {previewLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-6 w-6 animate-spin text-emerald-400" />
                  </div>
                ) : (
                  <LivePreview text={previewText} status="completed" />
                )}
              </GlassCard>
            )}
          </>
        )}
      </div>
    </main>
  )
}
