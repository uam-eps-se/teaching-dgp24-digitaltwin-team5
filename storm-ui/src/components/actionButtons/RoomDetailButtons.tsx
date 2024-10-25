'use client'

import { fetchRooms } from '@core/utils/data'
import { useRouter } from 'next/navigation';
import { ChangeEvent, useEffect, useState } from 'react'

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Box,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Tooltip,
  TextField,
} from '@mui/material';

import { mdiHomePlus, mdiFileImport, mdiPlus, mdiWindowClose, mdiFileExport } from '@mdi/js';
import Icon from '@mdi/react';
import { importRooms } from '@core/utils/actions';

const actions = [
  { icon: <Icon path={mdiHomePlus} size={1} />, name: 'New Room', path: 'rooms/create' },
  { icon: <Icon path={mdiFileImport} size={1} />, name: 'Import Rooms' },
];

const RoomSummaryActions = () => {
  const [open, setOpen] = useState(false);
  const [importFile, setImportFile] = useState<File>()
  const router = useRouter();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleActionClick = (action: any) => {
    if (action.path) {
      router.push('/rooms/create');
    } else {
      handleClickOpen();
    }
  }

  const handleImportInputChanged = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length)
      setImportFile(event.target.files![0]);
    else
      setImportFile(undefined);
  }

  return (
    <div>
      <Box
        sx={{ position: 'fixed', bottom: '50px', right: '50px', display: 'flex', gap: '25px', alignItems: 'flex-end' }}
      >
        <Tooltip title='Export Rooms to CSV' placement='top'>
          <Fab color="primary">
            <Icon path={mdiFileExport} size={1} />
          </Fab>
        </Tooltip>
        <SpeedDial
          ariaLabel="Rooms Options"
          icon={
            <SpeedDialIcon
              icon={<Icon path={mdiPlus} size={1} />}
              openIcon={<Icon path={mdiWindowClose} size={1} />}
            />
          }
        >
          {actions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipOpen
              tooltipTitle={action.name}
              onClick={() => handleActionClick(action)}
              sx={{ whiteSpace: "nowrap", maxWidth: "none" }}
            />
          ))}
        </SpeedDial>
      </Box>
      <Dialog
        open={open}
        onClose={handleClose}
        PaperProps={{
          component: 'form',
          onSubmit: async (event: React.FormEvent<HTMLFormElement>) => {
            event.preventDefault();
            const formData = new FormData(event.currentTarget);
            for (var [key, value] of formData.entries()) { 
              console.log(key, value);
          }
            await importRooms(formData);
            handleClose();
          },
        }}
      >
        <DialogTitle>Import Rooms</DialogTitle>
        <DialogContent>
          <DialogContentText className='mb-5'>
            Use an Excel file to import rooms.
          </DialogContentText>
          <input
            id="import-file"
            type="file"
            hidden
            required
            accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
            onChange={handleImportInputChanged}
          />
          <label htmlFor="import-file">
            <Button color='primary' variant="contained" component="span" className='mr-5'>
              Upload
            </Button>
          </label>
          <Button color='secondary' onClick={() => setImportFile(undefined)} variant="contained" component="span">
            Clear
          </Button>
          <TextField
            id="import-file-field"
            disabled
            aria-readonly
            value={importFile?.name || 'No File Selected'}
            fullWidth
            margin='normal'
          />
        </DialogContent>
        <DialogActions>
          <Button color='secondary' onClick={handleClose}>Cancel</Button>
          <Button color='primary' type="submit" disabled={!importFile}>Import</Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}

export default RoomSummaryActions