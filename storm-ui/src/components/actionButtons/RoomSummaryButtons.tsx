'use client'

import type { ChangeEvent, FormEvent } from 'react'
import { createRef, useState } from 'react'

import { useRouter } from 'next/navigation'

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
  TextField
} from '@mui/material'

import { mdiHomePlus, mdiFileImport, mdiPlus, mdiWindowClose, mdiFileExport } from '@mdi/js'
import Icon from '@mdi/react'

import { importRooms } from '@core/utils/actions'

const actions = [
  { icon: <Icon path={mdiHomePlus} size={1} />, name: 'New Room', path: 'rooms/create' },
  { icon: <Icon path={mdiFileImport} size={1} />, name: 'Import Rooms' }
]

const RoomSummaryActions = () => {
  const [open, setOpen] = useState(false)
  const [importFile, setImportFile] = useState<File>()
  const router = useRouter()
  const importFileRef = createRef<HTMLInputElement>()

  const handleClickOpen = () => {
    setOpen(true)
  }

  const handleClose = () => {
    setOpen(false)
    setImportFile(undefined)
  }

  const handleActionClick = (action: any) => {
    if (action.path) {
      router.push(action.path)
    } else {
      handleClickOpen()
    }
  }

  const handleImportInputChanged = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length) setImportFile(event.target.files![0])
    else setImportFile(undefined)
  }

  const handleDownloadCSV = () => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/data`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/vnd.ms-excel'
      }
    })
      .then(response => response.blob())
      .then(blob => {
        // Create blob link to download
        const url = window.URL.createObjectURL(new Blob([blob]))

        const link = document.createElement('a')

        link.href = url
        link.setAttribute('download', `Rooms_${new Date().toLocaleString('ES').replace(', ', '-')}.xlsx`)

        // Append to html link element page
        document.body.appendChild(link)

        // Start download
        link.click()

        // Clean up and remove the link
        link.parentNode && link.parentNode.removeChild(link)
      })
  }

  return (
    <div>
      <Box
        sx={{
          position: 'fixed',
          bottom: '50px',
          right: '50px',
          display: 'flex',
          gap: '25px',
          alignItems: 'flex-end',
          maxHeight: '56px'
        }}
      >
        <Tooltip title='Export Rooms to CSV' placement='top'>
          <Fab color='primary' onClick={handleDownloadCSV}>
            <Icon path={mdiFileExport} size={1} />
          </Fab>
        </Tooltip>
        <SpeedDial
          ariaLabel='Rooms Options'
          icon={
            <SpeedDialIcon icon={<Icon path={mdiPlus} size={1} />} openIcon={<Icon path={mdiWindowClose} size={1} />} />
          }
        >
          {actions.map(action => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipOpen
              tooltipTitle={action.name}
              onClick={() => handleActionClick(action)}
              sx={{ whiteSpace: 'nowrap', maxWidth: 'none' }}
            />
          ))}
        </SpeedDial>
      </Box>
      <Dialog
        open={open}
        onClose={handleClose}
        PaperProps={{
          component: 'form',
          onSubmit: async (event: FormEvent<HTMLFormElement>) => {
            event.preventDefault()
            const files = importFileRef.current?.files

            if (files) {
              const formData = new FormData()

              formData.append('database', files[0])

              const res = await importRooms(formData)

              if ('error' in res) console.error(res)
            }

            handleClose()
          }
        }}
      >
        <DialogTitle>Import Rooms</DialogTitle>
        <DialogContent>
          <DialogContentText className='mb-5'>Use an Excel/CSV file to import rooms.</DialogContentText>
          <input
            id='import-file'
            type='file'
            ref={importFileRef}
            hidden
            required
            accept='.csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel'
            onChange={handleImportInputChanged}
          />
          <label htmlFor='import-file'>
            <Button color='primary' variant='contained' component='span' className='mr-5'>
              Upload
            </Button>
          </label>
          <Button
            color='secondary'
            onClick={() => setImportFile(undefined)}
            variant='contained'
            component='span'
            disabled={!importFile}
          >
            Clear
          </Button>
          <TextField
            id='import-file-field'
            aria-readonly
            value={importFile?.name || 'No File Selected'}
            fullWidth
            margin='normal'
            inputProps={{ readOnly: 'readonly' }}
            onClick={() => importFileRef.current?.click()}
          />
        </DialogContent>
        <DialogActions>
          <Button color='secondary' onClick={handleClose}>
            Cancel
          </Button>
          <Button color='primary' type='submit' disabled={!importFile}>
            Import
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}

export default RoomSummaryActions
