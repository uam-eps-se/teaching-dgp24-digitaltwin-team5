'use client'

import { useState } from 'react'

import Link from 'next/link'

import { useRouter } from 'next/navigation'

import type { GridCellParams, GridColDef, GridEventListener } from '@mui/x-data-grid'
import { DataGrid, GridToolbarQuickFilter } from '@mui/x-data-grid'

import type { Theme } from '@mui/material/styles'
import { lighten, darken, styled } from '@mui/material/styles'

import { Box, IconButton, Tooltip, Paper } from '@mui/material'

import { mdiPencil, mdiTrashCan } from '@mdi/js'

import Icon from '@mdi/react'

import { SensorStatus, type RoomSummary } from '@core/types'
import DeleteRoomModal from '@/components/actionButtons/DeleteRoomModal'

const getBackgroundColor = (color: string, theme: Theme, coefficient: number) => ({
  backgroundColor: darken(color, coefficient),
  ...theme.applyStyles('light', {
    backgroundColor: lighten(color, coefficient)
  })
})

const getColor = (color: string, theme: Theme, coefficient: number) => ({
  color: darken(color, coefficient),
  ...theme.applyStyles('dark', {
    color: lighten(color, coefficient)
  })
})

const childrenHoverStyle = (theme: Theme) => ({
  '&:hover > .storm-status--0': {
    ...getBackgroundColor(theme.palette.success.main, theme, 0.6)
  },
  '&:hover > .storm-status--1': {
    ...getBackgroundColor(theme.palette.warning.main, theme, 0.6)
  },
  '&:hover > .storm-status--2': {
    ...getBackgroundColor(theme.palette.error.main, theme, 0.6)
  }
})

// Custom DataGrid with row/cell colors by Status
const StyledDataGrid = styled(DataGrid)(({ theme }) => ({
  '& .storm-status--0': {
    ...getBackgroundColor(theme.palette.success.main, theme, 0.7),
    ...getColor(theme.palette.success.main, theme, 0.55),
    '&:hover': {
      ...getBackgroundColor(theme.palette.success.main, theme, 0.6)
    }
  },
  '& .storm-status--1': {
    ...getBackgroundColor(theme.palette.warning.main, theme, 0.7),
    ...getColor(theme.palette.warning.main, theme, 0.55),
    '&:hover': {
      ...getBackgroundColor(theme.palette.warning.main, theme, 0.6)
    }
  },
  '& .storm-status--2': {
    ...getBackgroundColor(theme.palette.error.main, theme, 0.7),
    ...getColor(theme.palette.error.main, theme, 0.55),
    '&:hover': {
      ...getBackgroundColor(theme.palette.error.main, theme, 0.6)
    },
    ...childrenHoverStyle(theme)
  },
  '& .MuiDataGrid-row': childrenHoverStyle(theme)
}))

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

const QuickSearchToolbar = () => {
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

const DeleteRoomCell = (props: { row: RoomSummary }) => {
  const [openDelete, setOpenDelete] = useState(false)
  const { row } = props

  return (
    <>
      <Tooltip title={`Delete ${row.name}`}>
        <IconButton color='error' onClick={() => setOpenDelete(true)}>
          <Icon path={mdiTrashCan} size={1} />
        </IconButton>
      </Tooltip>
      <DeleteRoomModal roomId={row.id} roomName={row.name} open={openDelete} setOpen={setOpenDelete} />
    </>
  )
}

const paginationModel = { page: 0, pageSize: 10 }

export default function DataTable(props: { rooms: RoomSummary[] }) {
  const rooms = props.rooms
  const router = useRouter()

  const handleCellClick: GridEventListener<'cellClick'> = (params: GridCellParams) => {
    if (!['edit', 'delete'].includes(params.colDef.field)) {
      router.push(`/rooms/${params.row.id}`)
    }
  }

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Room',
      flex: 0.12
    },
    {
      field: 'doors',
      headerAlign: 'center',
      headerName: 'Doors',
      align: 'center',
      flex: 0.1,
      renderHeader: () => colHeader('Doors', 'open'),
      valueGetter: (_value, row: RoomSummary) => row.devices.doors.open,
      valueFormatter: (value, row: RoomSummary) => `${value}/${row.devices.doors.total}`
    },
    {
      field: 'windows',
      headerAlign: 'center',
      headerName: 'Windows',
      align: 'center',
      flex: 0.1,
      renderHeader: () => colHeader('Windows', 'open'),
      valueGetter: (_value, row: RoomSummary) => row.devices.windows.open,
      valueFormatter: (value, row: RoomSummary) => `${value}/${row.devices.windows.total}`
    },
    {
      field: 'lights',
      headerAlign: 'center',
      headerName: 'Lights',
      align: 'center',
      flex: 0.1,
      renderHeader: () => colHeader('Lights', 'on'),
      valueGetter: (_value, row: RoomSummary) => row.devices.lights.on,
      valueFormatter: (value, row: RoomSummary) => `${value}/${row.devices.lights.total}`
    },
    {
      field: 'ventilators',
      headerAlign: 'center',
      headerName: 'Cooling Devices',
      align: 'center',
      flex: 0.1,
      renderHeader: () => colHeader('Cooling Devices', 'on'),
      valueGetter: (_value, row: RoomSummary) => row.devices.ventilators.on,
      valueFormatter: (value, row: RoomSummary) => `${value}/${row.devices.ventilators.total}`
    },
    {
      field: 'people',
      headerAlign: 'center',
      headerName: 'Nº of People',
      align: 'center',
      flex: 0.1,
      type: 'number',
      valueGetter: (_value, row: RoomSummary) => row.metrics.people
    },
    {
      field: 'co2',
      headerAlign: 'center',
      headerName: 'CO₂ (ppm)',
      align: 'center',
      flex: 0.1,
      type: 'number',
      valueGetter: (_value, row: RoomSummary) => row.metrics.co2
    },
    {
      field: 'temperature',
      headerAlign: 'center',
      headerName: 'Temperature (Cº)',
      align: 'center',
      flex: 0.1,
      type: 'number',
      valueGetter: (_value, row: RoomSummary) => row.metrics.temperature
    },
    {
      field: 'edit',
      headerAlign: 'center',
      headerName: 'Edit',
      align: 'center',
      flex: 0.05,
      disableColumnMenu: true,
      sortable: false,
      renderCell: params => {
        return (
          <Link href={`/rooms/${params.row.id}/edit`}>
            <Tooltip title={`Edit ${params.row.name}`}>
              <IconButton color='info'>
                <Icon path={mdiPencil} size={1} />
              </IconButton>
            </Tooltip>
          </Link>
        )
      }
    },
    {
      field: 'delete',
      headerAlign: 'center',
      headerName: 'Delete',
      align: 'center',
      flex: 0.05,
      disableColumnMenu: true,
      sortable: false,
      renderCell: params => <DeleteRoomCell row={params.row} />
    }
  ]

  return (
    <Paper sx={{ height: '100%', width: '100%' }}>
      <StyledDataGrid
        rows={rooms}
        columns={columns}
        initialState={{ pagination: { paginationModel } }}
        pageSizeOptions={[10, 20, 40]}
        sx={{ border: 0 }}
        rowSelection={false}
        onCellClick={handleCellClick}
        disableColumnMenu
        slots={{ toolbar: QuickSearchToolbar }}
        getCellClassName={params => {
          // Show sensor cell in corresponding colors
          if (params.field === 'co2') return `storm-status--${params.row.co2Status}`
          else if (params.field === 'temperature') return `storm-status--${params.row.temperatureStatus}`

          return ''
        }}
        getRowClassName={params => {
          // If CO2 or Temperature in dangerous level, show row in red
          if ([params.row.co2Status, params.row.temperatureStatus].includes(SensorStatus.DANGER))
            return `storm-status--${SensorStatus.DANGER}`

          return ''
        }}
      />
    </Paper>
  )
}
