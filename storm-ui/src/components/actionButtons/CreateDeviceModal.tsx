import type { Dispatch, SetStateAction } from 'react'

import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField } from '@mui/material'
import Icon from '@mdi/react'

export default function CreateDeviceModal(props: {
  title: string
  deviceType: string
  open: boolean
  setOpen: Dispatch<SetStateAction<boolean>>
  icon: string
  onCreateDevice: (name: string, type: string) => void
}) {
  const handleClose = () => props.setOpen(false)

  return (
    <div>
      <Dialog
        open={props.open}
        onClose={handleClose}
        aria-labelledby='create-device-title'
        aria-describedby='create-device-title-description'
        closeAfterTransition
        disableRestoreFocus
      >
        <DialogTitle id='create-device-title' className='flex align-middle'>
          <Icon path={props.icon} size={1} className='mr-3' />
          {props.title}
        </DialogTitle>
        <form
          id='create-device-form'
          onSubmit={e => {
            e.preventDefault()
            const name = (document.getElementById('device-name') as HTMLInputElement).value

            props.onCreateDevice(name, props.deviceType)
            handleClose()
          }}
        >
          <DialogContent className='pt-3'>
            <DialogContentText id='create-device-description'>
              Enter a name for the new <b>{props.deviceType}</b>:
            </DialogContentText>
            <TextField
              id='device-name'
              label='Name'
              className='mt-5 w-full'
              placeholder={`My ${props.deviceType}`}
              autoFocus
              required
            />
          </DialogContent>
          <DialogActions>
            <Button color='secondary' onClick={handleClose}>
              Cancel
            </Button>
            <Button type='submit' color='primary' variant='contained'>
              Create
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </div>
  )
}
