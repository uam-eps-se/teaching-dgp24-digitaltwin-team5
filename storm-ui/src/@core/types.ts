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

/* ROOMS */

export enum SensorStatus {
  NORMAL = 0,
  HIGH = 1,
  DANGER = 2
}

export type RoomSummary = {
  id: number
  name: string
  size: number
  tempStatus: SensorStatus
  co2Status: SensorStatus
  devices: {
    doors: {
      open: number
      total: number
    }
    windows: {
      open: number
      total: number
    }
    lights: {
      on: number
      total: number
    }
    ventilators: {
      on: number
      total: number
    }
  }
  metrics: {
    people: number
    co2: number
    temperature: number
  }
}

/* ROOM DETAIL */

export type RoomDevice = {
  name: string
  current: boolean
  values: Array<boolean>
  times: Array<number>
}

export type RoomMetric = {
  values: Array<number>
  times: Array<number>
}

export type RoomStructureData = {
  doors: Record<number, RoomDevice>
  windows: Record<number, RoomDevice>
  ventilators: Record<number, RoomDevice>
  lights: Record<number, RoomDevice>
}

export type RoomRealtimeData = {
  people: RoomMetric
  co2: RoomMetric
  temperature: RoomMetric
}

export type RoomDetailData = {
  id: number
  name: string
  size: number
  tempStatus: SensorStatus
  co2Status: SensorStatus
  devices: RoomStructureData
  metrics: RoomRealtimeData
}

/* DEVICES */

export type Device = {
  id: number | undefined
  name: string
}

export type Door = Device & {
  rooms: Array<number>
}

export type AvailableDevices = {
  windows: Array<Device>
  lights: Array<Device>
  ventilators: Array<Device>
}

export type DeviceStatus = Device & {
  status: boolean
}

/* LAYOUT CONTEXT */

export enum AlertType {
  INFO = 0,
  WARNING = 1,
  DANGER = 2
}

export type Alert = {
  type: AlertType
  content: string
  roomId: number
  time: number
}

export type RoomItem = {
  id: number
  name: string
  alerts: Array<Alert>
}
