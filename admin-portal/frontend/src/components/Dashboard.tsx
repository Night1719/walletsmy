'use client'

import { useState, useEffect } from 'react'
import { 
  CpuChipIcon, 
  ServerIcon, 
  HardDriveIcon, 
  WifiIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import MetricsChart from './MetricsChart'
import ScriptsList from './ScriptsList'
import LogsPreview from './LogsPreview'

interface SystemMetrics {
  cpu_percent: number
  memory: {
    total: number
    available: number
    percent: number
    used: number
  }
  disk: {
    total: number
    used: number
    free: number
    percent: number
  }
  network: {
    bytes_sent: number
    bytes_recv: number
    packets_sent: number
    packets_recv: number
  }
  timestamp: string
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/metrics/system')
        const data = await response.json()
        setMetrics(data)
      } catch (error) {
        console.error('Error fetching metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000) // Обновляем каждые 5 секунд

    return () => clearInterval(interval)
  }, [])

  const formatBytes = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return '0 Bytes'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getStatusColor = (percent: number, thresholds: { warning: number; critical: number }) => {
    if (percent >= thresholds.critical) return 'text-red-600'
    if (percent >= thresholds.warning) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getStatusIcon = (percent: number, thresholds: { warning: number; critical: number }) => {
    if (percent >= thresholds.critical) return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
    if (percent >= thresholds.warning) return <ClockIcon className="h-5 w-5 text-yellow-600" />
    return <CheckCircleIcon className="h-5 w-5 text-green-600" />
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
        <p className="mt-1 text-sm text-gray-500">
          Обзор состояния системы и активных процессов
        </p>
      </div>

      {/* System Metrics Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* CPU Usage */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CpuChipIcon className="h-8 w-8 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Использование CPU
                </dt>
                <dd className="flex items-baseline">
                  <div className="flex items-baseline text-2xl font-semibold text-gray-900">
                    {metrics?.cpu_percent.toFixed(1)}%
                  </div>
                  <div className="ml-2">
                    {getStatusIcon(metrics?.cpu_percent || 0, { warning: 70, critical: 90 })}
                  </div>
                </dd>
              </dl>
            </div>
          </div>
        </div>

        {/* Memory Usage */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ServerIcon className="h-8 w-8 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Использование памяти
                </dt>
                <dd className="flex items-baseline">
                  <div className="flex items-baseline text-2xl font-semibold text-gray-900">
                    {metrics?.memory.percent.toFixed(1)}%
                  </div>
                  <div className="ml-2">
                    {getStatusIcon(metrics?.memory.percent || 0, { warning: 80, critical: 90 })}
                  </div>
                </dd>
                <dd className="text-sm text-gray-500">
                  {formatBytes(metrics?.memory.used || 0)} / {formatBytes(metrics?.memory.total || 0)}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        {/* Disk Usage */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <HardDriveIcon className="h-8 w-8 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Использование диска
                </dt>
                <dd className="flex items-baseline">
                  <div className="flex items-baseline text-2xl font-semibold text-gray-900">
                    {metrics?.disk.percent.toFixed(1)}%
                  </div>
                  <div className="ml-2">
                    {getStatusIcon(metrics?.disk.percent || 0, { warning: 85, critical: 95 })}
                  </div>
                </dd>
                <dd className="text-sm text-gray-500">
                  {formatBytes(metrics?.disk.used || 0)} / {formatBytes(metrics?.disk.total || 0)}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        {/* Network */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <WifiIcon className="h-8 w-8 text-gray-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Сетевая активность
                </dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {formatBytes(metrics?.network.bytes_sent || 0)}
                </dd>
                <dd className="text-sm text-gray-500">
                  отправлено / {formatBytes(metrics?.network.bytes_recv || 0)} получено
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Charts and Additional Info */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Metrics Chart */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Метрики системы</h3>
          <MetricsChart />
        </div>

        {/* Recent Scripts */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Недавние скрипты</h3>
          <ScriptsList />
        </div>
      </div>

      {/* Logs Preview */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Последние логи</h3>
        <LogsPreview />
      </div>
    </div>
  )
}