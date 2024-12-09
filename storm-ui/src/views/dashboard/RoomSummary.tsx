'use client'

// MUI Imports
import { useContext } from 'react'

import { useEffectOnce } from 'react-use'

import { Grid, Typography } from '@mui/material'

import RoomsTable from '@components/RoomsTable'

import RoomSummaryButtons from '@components/actionButtons/RoomSummaryButtons'

import { RoomsContext } from '@core/contexts/roomsContext'
import { useEventSource } from '@core/hooks/useEventSource'

const RoomSummary = () => {
  const { rooms, updateRooms } = useContext(RoomsContext)
  const { addEventHandler } = useEventSource(['summary'])

  useEffectOnce(() => {
    updateRooms().then(() => {
      addEventHandler('message', msgEvent => updateRooms(msgEvent.data))
    })
  })

  return (
    <div>
      <Grid container spacing={6}>
        <Grid item xs={12}>
          {rooms.data && rooms.data.length ? (
            <RoomsTable rooms={rooms.data} />
          ) : (
            <Typography className='text-lg'>{rooms.fetched ? 'No rooms available' : 'Loading rooms...'}</Typography>
          )}
        </Grid>
      </Grid>
      <RoomSummaryButtons />
    </div>
  )
}

export default RoomSummary
