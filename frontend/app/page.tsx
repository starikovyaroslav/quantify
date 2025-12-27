'use client'

import { useState, useEffect, useRef } from 'react'
import SpatialBackground from '@/components/SpatialBackground'
import GlassCard from '@/components/GlassCard'
import UploadZone from '@/components/UploadZone'
import LivePreview from '@/components/LivePreview'
import ControlsPanel from '@/components/ControlsPanel'
import Navigation from '@/components/Navigation'
import { quantizeImage, cancelTask } from '@/lib/api'
import toast from 'react-hot-toast'

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [width, setWidth] = useState(200)
  const [height, setHeight] = useState(200)
  const [quality, setQuality] = useState(5)
  const [previewText, setPreviewText] = useState<string>('')
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'error' | 'cancelled'>('idle')
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined)
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile)
    setStatus('idle')
    setPreviewText('')
    setCurrentTaskId(null)
  }

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [])

  const handleQuantize = async () => {
    if (!file) {
      toast.error('Пожалуйста, загрузите изображение')
      return
    }

    setStatus('processing')
    setProgress(0)
    setProgressMessage('Инициализация...')
    setErrorMessage(undefined)

    try {
      const result = await quantizeImage(file, width, height, quality)
      setCurrentTaskId(result.task_id)

      // Connect to WebSocket for real-time updates
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001'
      const ws = new WebSocket(`${wsUrl}/api/v1/ws/${result.task_id}`)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
      }

      ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'status' || data.type === 'update') {
            const statusData = data.data
            setProgress(statusData.progress || 0)
            setProgressMessage(statusData.message || 'Обработка...')

            if (statusData.status === 'completed') {
              setStatus('completed')
              setProgress(100)
              setProgressMessage('Готово!')

              // Fetch result
              try {
                const textResult = await fetch(
                  `${process.env.NEXT_PUBLIC_API_URL}/api/v1/quantize/result/${result.task_id}`
                )

                if (!textResult.ok) {
                  throw new Error(`HTTP error! status: ${textResult.status}`)
                }

                const text = await textResult.text()
                setPreviewText(text)
                toast.success('Изображение успешно квантовано!')
              } catch (error) {
                const errorMessage =
                  error instanceof Error ? error.message : 'Ошибка при получении результата'
                toast.error(errorMessage)
                setStatus('error')
              }

              ws.close()
              wsRef.current = null
            } else if (statusData.status === 'error') {
              setStatus('error')
              const errorMsg = statusData.error || statusData.message || 'Ошибка при обработке изображения'
              setProgressMessage(`Ошибка: ${errorMsg}`)
              setErrorMessage(errorMsg)
              toast.error(errorMsg, { duration: 5000 })
              ws.close()
              wsRef.current = null
              setCurrentTaskId(null)
            } else if (statusData.status === 'cancelled') {
              setStatus('cancelled')
              setProgressMessage('Задача отменена')
              toast.success('Задача отменена')
              ws.close()
              wsRef.current = null
              setCurrentTaskId(null)
            }
          } else if (data.type === 'error') {
            setStatus('error')
            toast.error(data.data?.message || 'Ошибка соединения')
            ws.close()
            wsRef.current = null
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        toast.error('Ошибка соединения с сервером')
        setStatus('error')
        ws.close()
        wsRef.current = null
      }

      ws.onclose = () => {
        console.log('WebSocket closed')
        wsRef.current = null
      }

      // Store task ID for cancellation
      setCurrentTaskId(result.task_id)

      // Fallback timeout (5 minutes)
      const timeoutId = setTimeout(() => {
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
          ws.close()
          setStatus('error')
          setProgressMessage('Превышено время ожидания')
          toast.error('Превышено время ожидания (5 минут)')
        }
      }, 300000) // 5 minutes

      // Clear timeout when WebSocket closes
      const originalOnClose = ws.onclose
      ws.onclose = (event) => {
        clearTimeout(timeoutId)
        if (originalOnClose) originalOnClose(event)
      }

    } catch (error) {
      setStatus('error')
      const errorMessage =
        error instanceof Error ? error.message : 'Ошибка при загрузке изображения'
      toast.error(errorMessage)
    }
  }

  const handleCancel = async () => {
    if (!currentTaskId || status !== 'processing') {
      return
    }

    try {
      await cancelTask(currentTaskId)
      toast.success('Задача отменена')
      setStatus('cancelled')
      setProgressMessage('Задача отменена')

      // Close WebSocket
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      setCurrentTaskId(null)
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Ошибка при отмене задачи'
      toast.error(errorMessage)
    }
  }

  return (
    <main className="relative min-h-screen">
      <SpatialBackground />

      <div className="container relative z-10 mx-auto px-4 py-12">
        <Navigation />

        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="mb-4 text-5xl font-bold md:text-7xl">
            <span className="text-gradient">QuantTxt</span>
          </h1>
          <p className="mx-auto max-w-2xl text-xl text-slate-400">
            Преобразуйте изображения в текст с помощью оптического квантования Unicode-символов
          </p>
        </div>

        {/* Main Content */}
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Left Column - Upload & Preview */}
          <div className="space-y-6">
            <GlassCard>
              <UploadZone onFileSelect={handleFileSelect} />
            </GlassCard>

            <GlassCard>
              <LivePreview
                text={previewText}
                status={status}
                progress={progress}
                progressMessage={progressMessage}
                error={errorMessage}
              />
            </GlassCard>
          </div>

          {/* Right Column - Controls */}
          <div>
            <GlassCard>
              <ControlsPanel
                width={width}
                height={height}
                quality={quality}
                onWidthChange={setWidth}
                onHeightChange={setHeight}
                onQualityChange={setQuality}
                onQuantize={handleQuantize}
                onCancel={handleCancel}
                isProcessing={status === 'processing'}
              />
            </GlassCard>
          </div>
        </div>
      </div>
    </main>
  )
}
