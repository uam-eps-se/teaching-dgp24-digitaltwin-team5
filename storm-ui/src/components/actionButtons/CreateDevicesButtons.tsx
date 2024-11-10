'use client'

import { useState } from 'react'

import { Box, Fab, Tooltip } from '@mui/material'

import { mdiDoorOpen, mdiFan, mdiLightbulbOn, mdiWindowClosedVariant } from '@mdi/js'
import Icon from '@mdi/react'

import CreateDeviceModal from './CreateDeviceModal'

const actions = [
  { icon: mdiDoorOpen, name: 'New Door', item: 'door' },
  { icon: mdiWindowClosedVariant, name: 'New Window', item: 'window' },
  { icon: mdiLightbulbOn, name: 'New Light', item: 'light' },
  { icon: mdiFan, name: 'New Cooling Device', item: 'cooling device' }
]

const CreateDeviceButton = (props: {
  name: string
  item: string
  icon: string
  onCreateDevice: (name: string, type: string) => void
}) => {
  const [open, setOpen] = useState(false)
  const { name, item, icon, onCreateDevice } = props

  return (
    <div>
      <Tooltip title={name} placement='top'>
        <Fab
          id={item}
          onClick={() => {
            setOpen(true)
          }}
          color='primary'
        >
          <Icon path={icon} size={1.2} />
        </Fab>
      </Tooltip>
      <CreateDeviceModal
        title={name}
        deviceType={item}
        open={open}
        setOpen={setOpen}
        icon={icon}
        onCreateDevice={onCreateDevice}
      />
    </div>
  )
}

const CreateDevicesButtons = (props: { onCreateDevice: (name: string, type: string) => void }) => {
  return (
    <div>
      <Box
        sx={{
          position: 'fixed',
          bottom: '50px',
          right: '50px',
          display: 'flex',
          flexDirection: 'row',
          gap: '25px'
        }}
      >
        {actions.map(({ name, item, icon }) => (
          <CreateDeviceButton key={item} name={name} item={item} icon={icon} onCreateDevice={props.onCreateDevice} />
        ))}
      </Box>
    </div>
  )
}

export default CreateDevicesButtons
