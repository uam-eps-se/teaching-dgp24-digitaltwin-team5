'use client'

import type { ReactNode, Dispatch, SetStateAction } from 'react'
import { createContext, useState } from 'react'

import type { RoomSummary } from '../types'
import { fetchRooms } from '../utils/data'

type RoomsData = {
  data: RoomSummary[]
  fetched: boolean
}

interface RoomsContextType {
  rooms: RoomsData
  setRooms: Dispatch<SetStateAction<RoomsData>>
  updateRooms: (newRooms?: any) => Promise<void>
}

export const RoomsContext = createContext<RoomsContextType>({
  rooms: {
    data: [],
    fetched: false
  },
  setRooms: () => {},
  updateRooms: async () => {}
})

// RoomsProvider component to provide context
export const RoomsProvider = ({ children }: { children: ReactNode }) => {
  const [rooms, setRooms] = useState<RoomsData>({
    data: [],
    fetched: false
  })

  const updateRooms = async (newRooms?: any) => {
    const rs = newRooms || (await fetchRooms())

    if (rs)
      setRooms({
        data: rs.map((r: any) => {
          r.temperatureStatus = r.temperature_status
          r.co2Status = r.co2_status
          delete r.temperature_status, r.co2_status

          return r
        }),
        fetched: true
      })
  }

  return <RoomsContext.Provider value={{ rooms, setRooms, updateRooms }}>{children}</RoomsContext.Provider>
}
