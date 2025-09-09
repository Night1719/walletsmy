'use client'

import { useState, useEffect } from 'react'
import { PlayIcon, PauseIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'

interface Script {
  id: string
  name: string
  category: string
  status: 'running' | 'completed' | 'failed' | 'scheduled'
  last_executed: string
  execution_count: number
  success_count: number
  failure_count: number
}

export default function ScriptsList() {
  const [scripts, setScripts] = useState<Script[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchScripts = async () => {
      try {
        const response = await fetch('/api/scripts')
        const data = await response.json()
        setScripts(data.slice(0, 5)) // Показываем только первые 5
      } catch (error) {
        console.error('Error fetching scripts:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchScripts()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <PlayIcon className="h-4 w-4 text-blue-600" />
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4 text-green-600" />
      case 'failed':
        return <XCircleIcon className="h-4 w-4 text-red-600" />
      case 'scheduled':
        return <ClockIcon className="h-4 w-4 text-yellow-600" />
      default:
        return <ClockIcon className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return 'Выполняется'
      case 'completed':
        return 'Завершен'
      case 'failed':
        return 'Ошибка'
      case 'scheduled':
        return 'Запланирован'
      default:
        return 'Неизвестно'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'status-info'
      case 'completed':
        return 'status-success'
      case 'failed':
        return 'status-error'
      case 'scheduled':
        return 'status-warning'
      default:
        return 'status-info'
    }
  }

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  if (scripts.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-500">Нет доступных скриптов</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {scripts.map((script) => (
        <div key={script.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            {getStatusIcon(script.status)}
            <div>
              <p className="text-sm font-medium text-gray-900">{script.name}</p>
              <p className="text-xs text-gray-500 capitalize">{script.category}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(script.status)}`}>
              {getStatusText(script.status)}
            </span>
            <div className="text-xs text-gray-500">
              {script.execution_count} выполнений
            </div>
          </div>
        </div>
      ))}
      
      <div className="pt-2">
        <a 
          href="/scripts" 
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Посмотреть все скрипты →
        </a>
      </div>
    </div>
  )
}