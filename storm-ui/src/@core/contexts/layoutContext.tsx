'use client'

import type { ReactNode, Dispatch, SetStateAction } from 'react'
import { createContext, useState } from 'react'

import { useLocalStorage } from 'react-use'

import { AlertType, type Alert, type Context } from '../types'
import { fetchContext } from '../utils/data'

interface LayoutContextType {
  context: Context
  storedAlerts: Alert[] | undefined
  setContext: Dispatch<SetStateAction<Context>>
  setStoredAlerts: Dispatch<SetStateAction<Alert[] | undefined>>
  updateContext: (newContext?: Context) => Promise<void>
  setAlerts: (newAlerts: Alert[]) => void
}

export const LayoutContext = createContext<LayoutContextType>({
  context: { rooms: [], alerts: [] },
  storedAlerts: [],
  setContext: () => {},
  setStoredAlerts: () => {},
  updateContext: async () => {},
  setAlerts: () => {}
})

// LayoutProvider component to provide context
export const LayoutProvider = ({ children }: { children: ReactNode }) => {
  const [storedAlerts, setStoredAlerts] = useLocalStorage<Alert[]>('stored-alerts', [])

  const [context, setContext] = useState<Context>({ rooms: [], alerts: [] })

  const maxAlerts = Number(process.env.NEXT_PUBLIC_MAX_STORED_ALERTS || 99)

  const setAlerts = (newAlerts: Alert[]) => {
    setContext({ rooms: context.rooms, alerts: newAlerts })
  }

  const updateContext = async (newContext?: Context) => {
    const c: Context = newContext || (await fetchContext())

    if (c) {
      if (c.alerts.length) {
        const newestAlertId = Number(localStorage.getItem('newest-alert-id') || -1)

        // Only new DANGER or WARNING alerts
        setContext(prevContext => ({
          rooms: c.rooms,
          alerts: [
            ...prevContext.alerts,
            ...c.alerts.filter(alert => (!newestAlertId || alert.id > newestAlertId) && alert.type !== AlertType.INFO)
          ]
        }))
        setStoredAlerts(c.alerts.toSorted((a, b) => b.type - a.type).slice(0, maxAlerts))
        localStorage.setItem('newest-alert-id', String(c.alerts[0].id))
      } else {
        setContext(prevContext => ({
          rooms: c.rooms,
          alerts: prevContext.alerts
        }))
      }
    }
  }

  return (
    <LayoutContext.Provider
      value={{
        context,
        storedAlerts,
        setContext,
        setStoredAlerts,
        updateContext,
        setAlerts
      }}
    >
      {children}
    </LayoutContext.Provider>
  )
}
