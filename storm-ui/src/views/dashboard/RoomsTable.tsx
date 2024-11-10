'use client'

import { useState } from 'react'

import Link from 'next/link'

import { useRouter } from 'next/navigation'

import type { GridCellParams, GridColDef, GridEventListener } from '@mui/x-data-grid'
import { DataGrid, GridToolbarQuickFilter } from '@mui/x-data-grid'
import Paper from '@mui/material/Paper'

import { Box, IconButton, Tooltip } from '@mui/material'

import { mdiPencil, mdiTrashCan } from '@mdi/js'

import Icon from '@mdi/react'

import type { RoomSummaryRow } from '@core/types'
import DeleteRoomModal from '@/components/actionButtons/DeleteRoomModal'

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

const DeleteRoomCell = (props: { row: RoomSummaryRow }) => {
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

export default function DataTable(props: { rooms: RoomSummaryRow[] }) {
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
      valueGetter: (value, row) => row.devices.doors.open,
      valueFormatter: (value, row) => `${value}/${row.devices.doors.total}`
    },
    {
      field: 'windows',
      headerAlign: 'center',
      headerName: 'Windows',
      align: 'center',
      flex: 0.1,
      renderHeader: () => colHeader('Windows', 'open'),
      valueGetter: (value, row) => row.devices.windows.open,
      valueFormatter: (value, row) => `${value}/${row.devices.windows.total}`
    },
    {
      field: 'lights',
      headerAlign: 'center',
      headerName: 'Lights',
      align: 'center',
      flex: 0.1,
      renderHeader: () => colHeader('Lights', 'on'),
      valueGetter: (value, row) => row.devices.lights.on,
      valueFormatter: (value, row) => `${value}/${row.devices.lights.total}`
    },
    {
      field: 'ventilators',
      headerAlign: 'center',
      headerName: 'Cooling Devices',
      align: 'center',
      flex: 0.1,
      renderHeader: () => colHeader('Cooling Devices', 'on'),
      valueGetter: (value, row) => row.devices.ventilators.on,
      valueFormatter: (value, row) => `${value}/${row.devices.ventilators.total}`
    },
    {
      field: 'people',
      headerAlign: 'center',
      headerName: 'Nº of People',
      align: 'center',
      flex: 0.1,
      type: 'number',
      valueGetter: (value, row) => row.metrics.people
    },
    {
      field: 'co2',
      headerAlign: 'center',
      headerName: 'CO₂ (ppm)',
      align: 'center',
      flex: 0.1,
      type: 'number',
      valueGetter: (value, row) => row.metrics.co2
    },
    {
      field: 'temperature',
      headerAlign: 'center',
      headerName: 'Temperature (Cº)',
      align: 'center',
      flex: 0.1,
      type: 'number',
      valueGetter: (value, row) => row.metrics.temperature
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
      <DataGrid
        rows={rooms}
        columns={columns}
        initialState={{ pagination: { paginationModel } }}
        pageSizeOptions={[10, 20, 40]}
        sx={{ border: 0 }}
        rowSelection={false}
        onCellClick={handleCellClick}
        disableColumnMenu
        slots={{ toolbar: QuickSearchToolbar }}
      />
    </Paper>
  )
}
