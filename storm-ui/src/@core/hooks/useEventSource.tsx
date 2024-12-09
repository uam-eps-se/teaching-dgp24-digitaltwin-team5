'use client'

import { useRef } from 'react'

import { useEffectOnce } from 'react-use'
import type { ReconnectingEventSourceInit } from 'reconnecting-eventsource'
import ReconnectingEventSource from 'reconnecting-eventsource'

interface UseEventSourceHook {
  eventSource: ReconnectingEventSource | null
  addEventHandler: (event: string, handler: (msgEvent: MessageEvent) => any) => void
  removeEventHandlers: (event: string) => void
}

export const useEventSource = (channels: string[], configuration?: ReconnectingEventSourceInit): UseEventSourceHook => {
  const eventSource = useRef<ReconnectingEventSource | null>(null)
  const eventHandlers = useRef<Map<string, Array<(event: MessageEvent) => void>>>(new Map())

  const addEventHandler = (event: string, handler: (msgEvent: MessageEvent) => any) => {
    if (eventSource.current) {
      const prevHandlers = eventHandlers.current.get(event)
      const action = (msgEvent: MessageEvent) => handler({ ...msgEvent, data: JSON.parse(msgEvent.data) })

      eventSource.current.addEventListener(event, action)
      prevHandlers ? prevHandlers.push(action) : eventHandlers.current.set(event, [action])
    } else {
      throw new Error('EventSource not created or closed')
    }
  }

  const _removeEventHandlers = (event: string, handlers: ((msgEvent: MessageEvent) => any)[]) => {
    handlers.forEach(handler => {
      eventSource.current?.removeEventListener(event, handler)
    })
  }

  // To be called optionally in component cleanup
  const removeEventHandlers = (event: string) => {
    if (eventSource.current) {
      _removeEventHandlers(event, eventHandlers.current.get(event) || [])
      eventHandlers.current.delete(event)
    } else {
      throw new Error('EventSource not created or closed')
    }
  }

  const closeEventSource = () => {
    if (eventSource.current) {
      eventHandlers.current.forEach((handlers, event) => _removeEventHandlers(event, handlers))
      eventHandlers.current.clear()

      eventSource.current.onmessage = undefined as unknown as (event: Event) => void
      eventSource.current.onerror = undefined as unknown as (event: Event) => void
      eventSource.current.close()
      eventSource.current = null
    }
  }

  useEffectOnce(() => {
    if (!eventSource.current) {
      const eventUrl = new URL(`${process.env.NEXT_PUBLIC_API_URL}/events`)

      eventUrl.searchParams.set('channel', channels.toString())
      eventSource.current = new ReconnectingEventSource(eventUrl, configuration)
    }

    return closeEventSource
  })

  return {
    eventSource: eventSource.current,
    addEventHandler,
    removeEventHandlers
  }
}
