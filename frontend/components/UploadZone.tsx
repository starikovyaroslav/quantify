'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, X } from 'lucide-react'

interface UploadZoneProps {
  onFileSelect: (file: File) => void
  maxSize?: number
  acceptedTypes?: string[]
}

export default function UploadZone({
  onFileSelect,
  maxSize = 10 * 1024 * 1024,
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp'],
}: UploadZoneProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (file) {
        setFile(file)
        const reader = new FileReader()
        reader.onload = () => {
          setPreview(reader.result as string)
        }
        reader.readAsDataURL(file)
        onFileSelect(file)
      }
    },
    [onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxSize,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
      'image/gif': ['.gif'],
    },
    multiple: false,
  })

  const removeFile = () => {
    setFile(null)
    setPreview(null)
  }

  return (
    <div className="w-full">
      {!preview ? (
        <div
          {...getRootProps()}
          className={`
            relative h-80 w-full cursor-pointer rounded-2xl border-2
            border-dashed transition-all duration-300
            ${
              isDragActive
                ? 'scale-105 border-emerald-400 bg-emerald-500/10'
                : 'border-white/20 hover:border-white/40 hover:bg-white/5'
            }
          `}
        >
          <input {...getInputProps()} />
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-6">
            <motion.div
              className="relative h-20 w-20"
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
            >
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-emerald-400 to-teal-500 opacity-20 blur-xl" />
              <div className="absolute inset-2 rounded-full bg-gradient-to-r from-emerald-400 to-teal-500" />
              <Upload className="absolute inset-0 m-auto h-8 w-8 text-white" />
            </motion.div>
            <div className="space-y-2 text-center">
              <p className="text-lg font-medium">
                {isDragActive ? 'Отпустите для загрузки' : 'Перетащите изображение или кликните'}
              </p>
              <p className="text-sm text-slate-400">PNG, JPG, WEBP до {maxSize / 1024 / 1024}MB</p>
            </div>
          </div>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="group relative w-full overflow-hidden rounded-2xl"
        >
          <div className="relative aspect-square w-full">
            <img src={preview || ''} alt="Preview" className="h-full w-full object-cover" />
            <button
              onClick={removeFile}
              className="absolute right-4 top-4 z-10 rounded-full bg-black/50 p-2 backdrop-blur-sm transition-colors hover:bg-black/70"
            >
              <X className="h-5 w-5 text-white" />
            </button>
            <div className="glass absolute bottom-4 left-4 right-4 z-10 rounded-lg p-3">
              <p className="truncate text-sm font-medium">{file?.name}</p>
              <p className="text-xs text-slate-400">
                {((file?.size || 0) / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
