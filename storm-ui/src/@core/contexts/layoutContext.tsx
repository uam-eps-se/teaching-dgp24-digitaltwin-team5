'use client'

import type { ReactNode, Dispatch, SetStateAction } from 'react'
import { createContext, useState } from 'react'

import type { RoomItem } from '../types'
import { fetchContext } from '../utils/data'

interface LayoutContextType {
  context: RoomItem[]
  setContext: Dispatch<SetStateAction<RoomItem[]>>
  updateContext: () => Promise<void>
}

export const LayoutContext = createContext<LayoutContextType>({
  context: [],
  setContext: () => {},
  updateContext: async () => {}
})

// LayoutProvider component to provide context
export const LayoutProvider = ({ children }: { children: ReactNode }) => {
  const [context, setContext] = useState<RoomItem[]>([])

  const updateContext = async () => {
    return fetchContext().then(c => {
      if (c) setContext(c)
    })
  }

  return <LayoutContext.Provider value={{ context, setContext, updateContext }}>{children}</LayoutContext.Provider>
}
