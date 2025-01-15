'use client'

import { useState } from 'react'

import { usePathname, useRouter, useSearchParams } from 'next/navigation'

import { useEffectOnce } from 'react-use'

import { Alert, Box, Chip, Fab } from '@mui/material'

import Icon from '@mdi/react'

import {
  mdiChartLine,
  mdiCog,
  mdiFloorPlan,
  mdiHomeOutline,
  mdiIdentifier,
  mdiThermometerAlert,
  mdiMoleculeCo2
} from '@mdi/js'

import { TabContext, TabPanel } from '@mui/lab'

import { useDebouncedCallback } from 'use-debounce'

import { useEventSource } from '@core/hooks/useEventSource'
import { fetchRoom } from '@core/utils/data'
import { SensorStatus, type RoomDetailData } from '@core/types'

import RoomStructure from '@components/RoomStructure'
import RoomStatus from '@components/RoomStatus'
import RoomControl from '@components/RoomControl'
import RoomDetailButtons from '@components/actionButtons/RoomDetailButtons'

export default function RoomDetail(props: { roomId: string }) {
  const [room, setRoom] = useState<RoomDetailData>()
  const { addEventHandler } = useEventSource([`room-${props.roomId}`])

  const [titleChanged, setTitleChanged] = useState<boolean>(false)
  const [tab, setTab] = useState('0')

  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const updateRoomData = async (newRoomData?: any) => {
    const r = newRoomData || (await fetchRoom(props.roomId))

    if (!r.detail) {
      r.temperatureStatus = r.temperature_status
      r.co2Status = r.co2_status
      delete r.temperature_status, r.co2_status

      setRoom(r)
    }

    if (!titleChanged && r.name) {
      setTitleChanged(true)
      document.title = document.title.replace(`Room ${props.roomId}`, r.name)
    }
  }

  const getAlertContent = (status: SensorStatus, isCo2: boolean) => {
    switch (status) {
      case SensorStatus.HIGH:
        return `High ${isCo2 ? 'CO₂' : 'Temperature'} (> ${isCo2 ? '800 ppm' : '40°C'})`
      case SensorStatus.DANGER:
        return `Critical ${isCo2 ? 'CO₂' : 'Temperature'} (> ${isCo2 ? '1000 ppm' : '70°C'})`
      default:
        return ''
    }
  }

  useEffectOnce(() => {
    updateRoomData().then(() => {
      const routeTab = searchParams.get('tab')

      if (routeTab) setTab(routeTab)
      addEventHandler('message', msgEvent => updateRoomData(msgEvent.data))
    })
  })

  const setTabParam = useDebouncedCallback((tab: string) => {
    router.push(`${pathname}?tab=${tab}`)
  }, 1500)

  const handleTab = (tab: string) => {
    setTab(tab)
    setTabParam(tab)
  }

  const fabTabs = [
    {
      label: 'Room Structure',
      onKeyDown: (e: KeyboardEvent) => {
        if (e.key === 'ArrowRight') {
          handleTab('1')
          document.getElementById('roomdetail-tab-1')?.focus()
        }
      },
      icon: mdiFloorPlan
    },
    {
      label: 'Real-time Status',
      onKeyDown: (e: KeyboardEvent) => {
        if (e.key === 'ArrowLeft') {
          handleTab('0')
          document.getElementById('roomdetail-tab-0')?.focus()
        }

        if (e.key === 'ArrowRight') {
          handleTab('2')
          document.getElementById('roomdetail-tab-2')?.focus()
        }
      },
      icon: mdiChartLine
    },
    {
      label: 'Control Panel',
      onKeyDown: (e: KeyboardEvent) => {
        if (e.key === 'ArrowLeft') {
          handleTab('1')
          document.getElementById('roomdetail-tab-1')?.focus()
        }
      },
      icon: mdiCog
    }
  ]

  return (
    <div>
      {room ? (
        <>
          <h1 className='mb-5 flex flex-wrap justify-between items-center'>
            {room.name}
            <div className='flex flex-wrap gap-2'>
              {!room.temperatureStatus || (
                <Alert
                  severity={room.temperatureStatus === SensorStatus.DANGER ? 'error' : 'warning'}
                  icon={<Icon path={mdiThermometerAlert} size={1} />}
                  className='mr-2 p-2.5'
                >
                  {getAlertContent(room.temperatureStatus, false)}
                </Alert>
              )}
              {!room.co2Status || (
                <Alert
                  severity={room.co2Status === SensorStatus.DANGER ? 'error' : 'warning'}
                  icon={<Icon path={mdiMoleculeCo2} size={1} />}
                  className='p-2.5'
                >
                  {getAlertContent(room.co2Status, true)}
                </Alert>
              )}
            </div>
            <div>
              <Chip label={`${room.size} m²`} icon={<Icon path={mdiHomeOutline} size={1} />} className='mr-4' />
              <Chip label={room.id} icon={<Icon path={mdiIdentifier} size={1} />} />
            </div>
          </h1>
          <TabContext value={tab}>
            <TabPanel value='0'>
              <RoomStructure room={room} />
            </TabPanel>
            <TabPanel value='1'>
              <RoomStatus room={room} />
            </TabPanel>
            <TabPanel value='2'>
              <RoomControl room={room} />
            </TabPanel>
            <Box
              sx={{
                position: 'fixed',
                left: 0,
                right: 0,
                display: 'flex',
                gap: '5vw',
                bottom: '80px',
                marginX: 'auto',
                width: 'fit-content'
              }}
            >
              {fabTabs.map(({ label, onKeyDown, icon }, idx) => {
                return (
                  <Fab
                    key={label}
                    id={`roomdetail-tab-${idx}`}
                    color={tab === idx.toString() ? 'primary' : 'secondary'}
                    variant='extended'
                    onClick={() => handleTab(idx.toString())}
                    onKeyDown={e => onKeyDown(e as unknown as KeyboardEvent)}
                  >
                    <Icon path={icon} size={1} style={{ marginRight: 10 }} />
                    {label}
                  </Fab>
                )
              })}
            </Box>
          </TabContext>
          <RoomDetailButtons room={room} />
        </>
      ) : (
        <h1 className='mb-5 flex justify-between items-center'>Loading room...</h1>
      )}
    </div>
  )
}
