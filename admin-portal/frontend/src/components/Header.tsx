'use client'

import { useState } from 'react'
import { Bars3Icon, BellIcon } from '@heroicons/react/24/outline'
import { Menu, Transition } from '@headlessui/react'
import { Fragment } from 'react'

interface HeaderProps {
  onMenuClick: () => void
}

export default function Header({ onMenuClick }: HeaderProps) {
  const [notifications] = useState([
    { id: 1, message: 'High CPU usage detected', type: 'warning' },
    { id: 2, message: 'Backup completed successfully', type: 'success' },
    { id: 3, message: 'Disk space low', type: 'error' },
  ])

  return (
    <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      <button
        type="button"
        className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
        onClick={onMenuClick}
      >
        <span className="sr-only">Открыть боковую панель</span>
        <Bars3Icon className="h-6 w-6" aria-hidden="true" />
      </button>

      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div className="flex flex-1"></div>
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Notifications */}
          <Menu as="div" className="relative">
            <Menu.Button className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500">
              <span className="sr-only">Уведомления</span>
              <BellIcon className="h-6 w-6" aria-hidden="true" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-xs text-white flex items-center justify-center">
                  {notifications.length}
                </span>
              )}
            </Menu.Button>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 z-10 mt-2.5 w-80 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                <div className="px-4 py-2 text-sm font-medium text-gray-900">
                  Уведомления
                </div>
                {notifications.map((notification) => (
                  <Menu.Item key={notification.id}>
                    <div className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      <div className={`inline-block w-2 h-2 rounded-full mr-2 ${
                        notification.type === 'error' ? 'bg-red-500' :
                        notification.type === 'warning' ? 'bg-yellow-500' :
                        notification.type === 'success' ? 'bg-green-500' :
                        'bg-blue-500'
                      }`} />
                      {notification.message}
                    </div>
                  </Menu.Item>
                ))}
              </Menu.Items>
            </Transition>
          </Menu>

          {/* Profile dropdown */}
          <Menu as="div" className="relative">
            <Menu.Button className="-m-1.5 flex items-center p-1.5">
              <span className="sr-only">Открыть меню пользователя</span>
              <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                <span className="text-sm font-medium text-white">А</span>
              </div>
            </Menu.Button>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 z-10 mt-2.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                <Menu.Item>
                  <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                    Профиль
                  </a>
                </Menu.Item>
                <Menu.Item>
                  <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                    Выйти
                  </a>
                </Menu.Item>
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </div>
  )
}