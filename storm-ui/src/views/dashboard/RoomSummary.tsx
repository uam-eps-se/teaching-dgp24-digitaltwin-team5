'use client'

// MUI Imports
import { useContext } from 'react'

import Grid from '@mui/material/Grid'

// Components Imports
import { useInterval } from 'react-use'

import { Typography } from '@mui/material'

import RoomsTable from '@components/RoomsTable'

import RoomSummaryButtons from '@components/actionButtons/RoomSummaryButtons'

import { RoomsContext } from '@core/contexts/roomsContext'

const RoomSummary = () => {
  const { deleting, rooms, updateRooms } = useContext(RoomsContext)
  const intervalDelay = process.env.NEXT_PUBLIC_POLL_DELAY_MS || 2000

  useInterval(() => !deleting && updateRooms(), intervalDelay as number)

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
