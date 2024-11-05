'use client'

// MUI Imports
import { useContext } from 'react'

import Grid from '@mui/material/Grid'

// Components Imports
import { useInterval } from 'react-use'

import { Typography } from '@mui/material'

import RoomsTable from '@/views/dashboard/RoomsTable'

import RoomSummaryButtons from './actionButtons/RoomSummaryButtons'

import { RoomsContext } from '@core/contexts/roomsContext'

const RoomSummary = () => {
  const { deleting, rooms, updateRooms } = useContext(RoomsContext)
  const intervalDelay = process.env.NEXT_PUBLIC_POLL_DELAY_MS || 2000

  useInterval(() => !deleting && updateRooms(), intervalDelay as number)

  return (
    <div>
      <Grid container spacing={6}>
        <Grid item xs={12}>
          {rooms.data.length ? (
            <RoomsTable rooms={rooms.data} />
          ) : (
            rooms.fetched && <Typography className='text-lg'>No rooms available</Typography>
          )}
        </Grid>
      </Grid>
      <RoomSummaryButtons />
    </div>
  )
}

export default RoomSummary
