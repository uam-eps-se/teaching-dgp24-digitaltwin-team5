'use client'

import { useState } from 'react'

import { useRouter } from 'next/navigation'

import { DataGrid, GridCellParams, GridColDef, GridEventListener, GridToolbarQuickFilter } from '@mui/x-data-grid'
import Paper from '@mui/material/Paper'

import { Box, Tooltip } from '@mui/material'

import type { RoomDetailData } from '@core/types'

const colHeader = (name: string, subtitle: string) => {
  return (
    <Tooltip title={`${name} (${subtitle})`} placement='bottom'>
      <div className='flex flex-col truncate font-medium'>
        <p className='truncate'>{name}</p>
        <p className='truncate self-center'>({subtitle})</p>
      </div>
    </Tooltip>
  )
}

function QuickSearchToolbar() {
  return (
    <Box
      sx={{
        p: 1,
        pt: 2,
        px: 3
      }}
    >
      <GridToolbarQuickFilter
        sx={{
          width: '100%'
        }}
      />
    </Box>
  )
}

export default function DataTable(props: { room: RoomDetailData }) {
  const room = props.room
  const router = useRouter()

  return <Paper sx={{ height: '100%', width: '100%' }}></Paper>
}
