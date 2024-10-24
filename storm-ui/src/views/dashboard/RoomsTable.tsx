'use client'

import { DataGrid, GridCellParams, GridColDef, GridEventListener } from '@mui/x-data-grid';
import Paper from '@mui/material/Paper';
import { RoomSummaryRow } from '@core/types';
import { IconButton, Tooltip } from '@mui/material';
import DeleteRoomModal from '@/components/actionButtons/DeleteRoomDialog';
import Link from 'next/link';
import { mdiPencil } from '@mdi/js';
import Icon from '@mdi/react';
import { useRouter } from 'next/navigation';

const colHeader = (name: string, subtitle: string) => {
  return (
    <div className="flex flex-col justify-center h-screen font-medium">
      <Tooltip title={name} placement='bottom'>
      <div className="flex flex-col justify-center truncate">
        <p>{name}</p>
        <p>({subtitle})</p>
      </div>
      </Tooltip>
    </div>
  )
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
    valueFormatter: (value, row) => `${value}/${row.devices.doors.total}`,
  },
  { 
    field: 'windows',
    headerAlign: 'center',
    headerName: 'Windows',
    align: 'center',
    flex: 0.1,
    renderHeader: () => colHeader('Windows', 'open'),
    valueGetter: (value, row) => row.devices.windows.open,
    valueFormatter: (value, row) => `${value}/${row.devices.windows.total}`,
  },
  {
    field: 'lights',
    headerAlign: 'center',
    headerName: 'Lights',
    align: 'center',
    flex: 0.1,
    renderHeader: () => colHeader('Lights', 'on'),
    valueGetter: (value, row) => row.devices.lights.on,
    valueFormatter: (value, row) => `${value}/${row.devices.lights.total}`,
  },
  { 
    field: 'ventilator',
    headerAlign: 'center',
    headerName: 'Cooling Devices',
    align: 'center',
    flex: 0.1,
    renderHeader: () => colHeader('Cooling Devices', 'on'),
    valueGetter: (value, row) => row.devices.ventilator.on,
    valueFormatter: (value, row) => `${value}/${row.devices.ventilator.total}`,
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
    renderCell: (params) => {
      return (
        <Link href={`/rooms/edit/${params.row.id}`}>
          <IconButton color='info'><Icon path={mdiPencil} size={1} /></IconButton>
        </Link>
      )}
  },
  {
    field: 'delete',
    headerAlign: 'center',
    headerName: 'Delete',
    align: 'center',
    flex: 0.05,
    disableColumnMenu: true,
    sortable: false,
    renderCell: (params) => <DeleteRoomModal roomId={params.row.id} roomName={params.row.name} />
  }
];

const paginationModel = { page: 0, pageSize: 10 };


export default function DataTable(props: {rooms: RoomSummaryRow[]}) {
  const rooms = props.rooms;

  const router = useRouter();
  const handleCellClick: GridEventListener<'cellClick'> = (params: GridCellParams) => {
    if (!['edit', 'delete'].includes(params.colDef.field))
      router.push(`/rooms/${params.row.id}`);
  };

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
      />
    </Paper>
  );
}
