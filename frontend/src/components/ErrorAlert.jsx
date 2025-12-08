"use client"

import { AlertCircle, X } from "lucide-react"
import { useState } from "react"

export default function ErrorAlert({ message, onClose }) {
  const [isVisible, setIsVisible] = useState(true)

  const handleClose = () => {
    setIsVisible(false)
    onClose?.()
  }

  if (!isVisible) return null

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
      <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
      <div className="flex-1">
        <p className="text-red-800">{message}</p>
      </div>
      <button onClick={handleClose} className="text-red-600 hover:text-red-800">
        <X size={20} />
      </button>
    </div>
  )
}
