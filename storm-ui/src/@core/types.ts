// React Imports
import type { ReactNode } from 'react'

export type Skin = 'default' | 'bordered'

export type Mode = 'light' | 'dark'

export type SystemMode = 'light' | 'dark'

export type Direction = 'ltr' | 'rtl'

export type ChildrenType = {
  children: ReactNode
}

export type ThemeColor = 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'

export type RoomSummaryRow = {
  id: number,
  name: string,
  size: number,
  devices:{
    doors: {
      open: number,
      total: number
    },
    windows: {
      open: number,
      total: number
    },
    lights: {
      on: number,
      total: number
    },
    ventilators: {
      on: number,
      total: number
    }
  },
  metrics: {
    people: number,
    co2: number,
    temperature: number
  }
}

export type RoomStructureData = {
  id: number,
}

export type RoomRealtimeData = {
  id: number,
}
