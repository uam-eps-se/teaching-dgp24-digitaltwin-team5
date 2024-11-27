'use client'

import type { ReactNode } from 'react'
import { createContext } from 'react'

import ReconnectingEventSource from 'reconnecting-eventsource'

interface EventContextType {
  getOrCreateEventSource: () => ReconnectingEventSource | void
  addEventAction: (event: string, action: (msgEvent: MessageEvent) => any) => void
  removeEventHandlers: (eventTypes: string[]) => ReconnectingEventSource | void
}

export const EventContext = createContext<EventContextType>({
  getOrCreateEventSource: () => {},
  addEventAction: () => {},
  removeEventHandlers: () => {}
})

// EventProvider component to provide context
export const EventProvider = ({ children }: { children: ReactNode }) => {
  const eventHandlers: Map<string, Array<(ev: MessageEvent) => any>> = new Map()
  let eventSource: ReconnectingEventSource | null = null

  const getOrCreateEventSource = () => {
    if (!eventSource) eventSource = new ReconnectingEventSource(`${process.env.NEXT_PUBLIC_API_URL}/events`)

    return eventSource
  }

  const addEventAction = (event: string, action: (msgEvent: MessageEvent) => any) => {
    const evtSource = getOrCreateEventSource()
    const prevHandlers = eventHandlers.get(event)

    console.log('ADDED HANDLER FOR', event)

    const handler = (msgEvent: MessageEvent) => action({ ...msgEvent, data: JSON.parse(msgEvent.data) })

    evtSource.addEventListener(event, handler)
    if (!prevHandlers) eventHandlers.set(event, [handler])
    else prevHandlers!.push(handler)
  }

  const removeEventHandlers = (eventTypes: string[]) => {
    if (eventSource) {
      eventTypes.forEach(event => {
        eventHandlers.get(event)?.forEach(handler => {
          eventSource?.removeEventListener(event, handler)
        })
        eventHandlers.delete(event)
      })
    }

    return getOrCreateEventSource()
  }

  return (
    <EventContext.Provider
      value={{
        getOrCreateEventSource,
        addEventAction,
        removeEventHandlers
      }}
    >
      {children}
    </EventContext.Provider>
  )
}
