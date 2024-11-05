'use client'

import type { ReactNode, Dispatch, SetStateAction } from 'react'
import { createContext, useState } from 'react'

import type { RoomDetailData } from '../types'

interface RoomContextType {
  room: RoomDetailData | undefined
  setRoom: Dispatch<SetStateAction<RoomDetailData | undefined>>
}

export const RoomContext = createContext<RoomContextType>({
  room: undefined,
  setRoom: () => {}
})

// RoomsProvider component to provide context
export const RoomsProvider = ({ children }: { children: ReactNode }) => {
  const [room, setRoom] = useState<RoomDetailData>()

  return <RoomContext.Provider value={{ room, setRoom }}>{children}</RoomContext.Provider>
}
