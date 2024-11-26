'use client'

import type { ReactNode } from 'react'
import { createContext } from 'react'

import ReconnectingEventSource from 'reconnecting-eventsource'

import type { EventMessage } from '../types'

interface EventContextType {
  getOrCreateEventSource: () => ReconnectingEventSource | void
  setEventAction: (action: (msg: EventMessage) => void, typeFilter?: string) => EventSource | void
}

export const EventContext = createContext<EventContextType>({
  getOrCreateEventSource: () => {},
  setEventAction: () => {}
})

// EventProvider component to provide context
export const EventProvider = ({ children }: { children: ReactNode }) => {
  let eventSource: ReconnectingEventSource | null = null

  const getOrCreateEventSource = () => {
    if (!eventSource) eventSource = new ReconnectingEventSource(`${process.env.NEXT_PUBLIC_API_URL}/events`)

    return eventSource
  }

  const setEventAction = (action: (msg: EventMessage) => void, typeFilter?: string) => {
    const evtSource = getOrCreateEventSource()

    if (evtSource && action)
      evtSource.onmessage = (msgEvent: MessageEvent) => {
        const msg = JSON.parse(msgEvent.data)

        typeFilter ? msg.type === typeFilter && action(msg) : action(msg)
      }
  }

  return (
    <EventContext.Provider
      value={{
        getOrCreateEventSource,
        setEventAction
      }}
    >
      {children}
    </EventContext.Provider>
  )
}
