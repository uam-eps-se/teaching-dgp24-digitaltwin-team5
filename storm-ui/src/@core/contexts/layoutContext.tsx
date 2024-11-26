'use client'

import type { ReactNode, Dispatch, SetStateAction } from 'react'
import { createContext, useState } from 'react'

import { useLocalStorage } from 'react-use'

import { AlertType, type Alert, type Context } from '../types'
import { fetchContext } from '../utils/data'
import { confirmAlerts } from '../utils/actions'

interface LayoutContextType {
  context: Context
  storedAlerts: Alert[] | undefined
  setContext: Dispatch<SetStateAction<Context>>
  setStoredAlerts: Dispatch<SetStateAction<Alert[] | undefined>>
  updateContext: () => Promise<void>
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
  const [storedAlerts, setStoredAlerts] = useLocalStorage<Alert[]>('latest-alerts', [])

  const [context, setContext] = useState<Context>({ rooms: [], alerts: [] })

  const maxAlerts = Number(process.env.NEXT_PUBLIC_MAX_STORED_ALERTS || 20)

  const setAlerts = (newAlerts: Alert[]) => {
    setContext({ rooms: context.rooms, alerts: newAlerts })
  }

  const updateContext = async () => {
    return fetchContext()
      .then((c: Context) => {
        if (c) {
          const sortedNewAlerts = c.alerts.toSorted((a, b) => b.time - a.time)

          confirmAlerts(c.alerts.map(alert => alert.id))
          setContext({
            rooms: c.rooms,
            alerts: [...context.alerts, ...sortedNewAlerts.filter(alert => alert.type !== AlertType.INFO)]
          })
          setStoredAlerts([...sortedNewAlerts, ...(storedAlerts || [])].slice(0, maxAlerts))
        }
      })
      .catch(error => console.error(error))
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
