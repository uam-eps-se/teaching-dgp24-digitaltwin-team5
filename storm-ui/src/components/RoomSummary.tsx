'use client'

// MUI Imports
import Grid from '@mui/material/Grid'

// Components Imports
import RoomsTable from '@/views/dashboard/RoomsTable'

import { fetchRooms } from '@core/utils/data'
import { useEffect, useState } from 'react'
import { RoomSummaryRow } from '@core/types'

import RoomSummaryButtons from './actionButtons/RoomSummaryButtons';

const RoomSummary = () => {
  const [rooms, setRooms] = useState<RoomSummaryRow[]>([]);

  // Change with event subscription OR setInterval
  useEffect(() => {
    fetchRooms().then(rs => {
      setRooms(rs);
    })
  }, []);

  return (
    <div>
      <Grid container spacing={6}>
        <Grid item xs={12}>
          <RoomsTable rooms={rooms} />
        </Grid>
      </Grid>
      <RoomSummaryButtons />
    </div>
  )
}

export default RoomSummary