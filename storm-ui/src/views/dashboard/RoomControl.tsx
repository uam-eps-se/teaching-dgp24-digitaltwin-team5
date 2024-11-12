'use client'

import { useState } from 'react'

import type { GridColDef } from '@mui/x-data-grid'
import { DataGrid, gridClasses, GridPagination, GridToolbarQuickFilter } from '@mui/x-data-grid'
import Paper from '@mui/material/Paper'

import { Box, Button, Grid, Tooltip, Typography } from '@mui/material'

import { useDebouncedCallback } from 'use-debounce'

import type { DeviceStatus, RoomDetailData, RoomDevice } from '@core/types'
import { updateDeviceAction } from '@/@core/utils/actions'

function QuickSearchFooter() {
  return (
    <Box
      sx={{
        display: 'flex',
        borderTop: '1px solid',
        borderColor: 'var(--mui-palette-TableCell-border)'
      }}
    >
      <GridToolbarQuickFilter
        sx={{
          p: 1,
          pt: 2,
          px: 3
        }}
      />
      <GridPagination sx={{ minWidth: 'fit-content' }} />
    </Box>
  )
}

const paginationModel = { page: 0, pageSize: 5 }

function ControlTable(props: { devices: DeviceStatus[]; type: string; title: string | undefined }) {
  const devices = props.devices
  const type = props.type
  const title = props.title

  let actionTrue: string = 'On'
  let actionFalse: string = 'Off'
  let statusFalse: string = 'Off'
  let getTooltip = (name: string, action: string) => `Turn ${name} ${action}`

  if (['door', 'window'].includes(type)) {
    actionTrue = 'Open'
    actionFalse = 'Close'
    statusFalse = 'Closed'
    getTooltip = (name: string, action: string) => `${action} ${name}`
  }

  const columns: GridColDef[] = [
    {
      field: 'name',
      renderHeader: () => (
        <Typography fontWeight='bold'>{title || `${type[0].toUpperCase()}${type.slice(1)}s`}</Typography>
      ),
      flex: 0.4
    },
    {
      field: 'status',
      headerAlign: 'center',
      headerName: 'Status',
      align: 'center',
      flex: 0.3,
      valueGetter: value => (value ? actionTrue : statusFalse),
      renderCell: params => {
        return (
          <Typography
            variant='inherit'
            color={params.row.status ? 'var(--mui-palette-success-main)' : 'error'}
            className='font-medium'
          >
            {params.row.status ? actionTrue : statusFalse}
          </Typography>
        )
      }
    },
    {
      field: 'action',
      headerAlign: 'center',
      headerName: 'Action',
      align: 'center',
      flex: 0.3,
      disableColumnMenu: true,
      sortable: false,
      renderCell: params => {
        const [disabled, setDisabled] = useState<boolean>(false)
        const [active, setActive] = useState<boolean>(params.row.status)

        const handleAction = useDebouncedCallback(async () => {
          const res: any = await updateDeviceAction(params.row.id as number, type, !active)

          if (!('error' in res)) {
            // TODO Check if button actually updates with params.row.status value
            params.row.status = !active
            setActive(!active)
          }

          setDisabled(false)
        }, 500)

        return (
          <Tooltip
            title={getTooltip(params.row.name, active ? actionFalse : actionTrue)}
            enterDelay={500}
            enterNextDelay={500}
          >
            <Button
              variant='outlined'
              size='small'
              disabled={disabled}
              onClick={() => {
                setDisabled(true)
                handleAction()
              }}
              color={active ? 'error' : 'success'}
              className='h-3/5 rounded'
            >
              {active ? actionFalse : actionTrue}
            </Button>
          </Tooltip>
        )
      }
    }
  ]

  return (
    <Paper sx={{ height: 'auto', width: '100%' }}>
      <DataGrid
        rows={devices}
        columns={columns}
        initialState={{ pagination: { paginationModel } }}
        pageSizeOptions={[5]}
        rowSelection={false}
        rowHeight={41}
        columnHeaderHeight={41}
        disableColumnMenu
        slots={{
          footer: QuickSearchFooter
        }}
        sx={{
          border: 0,
          [`& .${gridClasses.cell}:focus, & .${gridClasses.cell}:focus-within`]: {
            outline: 'none'
          }
        }}
      />
    </Paper>
  )
}

export default function RoomControl(props: { room: RoomDetailData }) {
  const room = props.room

  const mapRoomDevices = (rd: Record<number, RoomDevice>): DeviceStatus[] =>
    Object.entries(rd).map(([deviceId, device]) => {
      return {
        id: Number(deviceId),
        name: device.name,
        status: device.values[0] // TODO change to device.current
      }
    })

  const deviceMap = [
    { records: room.devices.doors, type: 'door', errorLabel: 'doors' },
    { records: room.devices.windows, type: 'window', errorLabel: 'windows' },
    { records: room.devices.lights, type: 'light', errorLabel: 'lights' },
    { records: room.devices.ventilators, type: 'ventilator', errorLabel: 'cooling devices', title: 'Cooling Devices' }
  ]

  return (
    <div>
      <Grid container spacing={6} columnSpacing={15}>
        {deviceMap.map(d => (
          <Grid key={d.type} item xs={12} md={6}>
            {Object.keys(d.records).length ? (
              <ControlTable devices={mapRoomDevices(d.records)} type={d.type} title={d.title} />
            ) : (
              <Typography variant='h5' className='mt-4'>
                No {d.errorLabel} available
              </Typography>
            )}
          </Grid>
        ))}
      </Grid>
    </div>
  )
}
