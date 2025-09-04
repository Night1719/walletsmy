'use client'

import { useState, useEffect } from 'react'
import { 
  ExclamationTriangleIcon, 
  InformationCircleIcon, 
  CheckCircleIcon,
  XCircleIcon 
} from '@heroicons/react/24/outline'

interface LogEntry {
  id: number
  timestamp: string
  level: string
  message: string
  module: string
}

export default function LogsPreview() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch('/api/logs?limit=10')
        const data = await response.json()
        setLogs(data.logs || [])
      } catch (error) {
        console.error('Error fetching logs:', error)
        // Показываем тестовые данные если API недоступен
        setLogs([
          {
            id: 1,
            timestamp: new Date().toISOString(),
            level: 'INFO',
            message: 'System started successfully',
            module: 'system'
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 60000).toISOString(),
            level: 'WARNING',
            message: 'High CPU usage detected',
            module: 'monitoring'
          },
          {
            id: 3,
            timestamp: new Date(Date.now() - 120000).toISOString(),
            level: 'ERROR',
            message: 'Failed to connect to database',
            module: 'database'
          },
          {
            id: 4,
            timestamp: new Date(Date.now() - 180000).toISOString(),
            level: 'INFO',
            message: 'Backup completed successfully',
            module: 'backup'
          }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchLogs()
  }, [])

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'ERROR':
      case 'CRITICAL':
        return <XCircleIcon className="h-4 w-4 text-red-600" />
      case 'WARNING':
        return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-600" />
      case 'INFO':
        return <InformationCircleIcon className="h-4 w-4 text-blue-600" />
      case 'DEBUG':
        return <CheckCircleIcon className="h-4 w-4 text-gray-600" />
      default:
        return <InformationCircleIcon className="h-4 w-4 text-gray-600" />
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
      case 'CRITICAL':
        return 'text-red-600 bg-red-50'
      case 'WARNING':
        return 'text-yellow-600 bg-yellow-50'
      case 'INFO':
        return 'text-blue-600 bg-blue-50'
      case 'DEBUG':
        return 'text-gray-600 bg-gray-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ru-RU', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="flex items-center space-x-3">
              <div className="h-4 w-4 bg-gray-200 rounded"></div>
              <div className="h-3 bg-gray-200 rounded w-20"></div>
              <div className="h-3 bg-gray-200 rounded w-32"></div>
              <div className="h-3 bg-gray-200 rounded w-48"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {logs.map((log) => (
        <div key={log.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
          <div className="flex-shrink-0 mt-0.5">
            {getLevelIcon(log.level)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLevelColor(log.level)}`}>
                {log.level}
              </span>
              <span className="text-xs text-gray-500">
                {formatTimestamp(log.timestamp)}
              </span>
              {log.module && (
                <span className="text-xs text-gray-400">
                  [{log.module}]
                </span>
              )}
            </div>
            <p className="text-sm text-gray-900">{log.message}</p>
          </div>
        </div>
      ))}
      
      <div className="pt-2">
        <a 
          href="/logs" 
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Посмотреть все логи →
        </a>
      </div>
    </div>
  )
}