'use client'

import { useContext, useState } from 'react'

import type { BadgeProps } from '@mui/material'
import { Badge, Button, IconButton, List, ListItem, Menu, styled, Tooltip, Typography } from '@mui/material'

import { useEffectOnce } from 'react-use'

import StormAlert from '@components/StormAlert'
import { LayoutContext } from '@core/contexts/layoutContext'

const StyledBadge = styled(Badge)<BadgeProps>(({ theme }) => ({
  '& .MuiBadge-badge': {
    right: 7,
    top: 10,
    border: `2px solid ${theme.palette.background.paper}`,
    padding: '0 4px',
    color: theme.palette.primary.contrastText
  }
}))

const AlertsMenu = () => {
  const { context, storedAlerts, setStoredAlerts, setAlerts } = useContext(LayoutContext)
  const [isClient, setIsClient] = useState(false)

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const open = Boolean(anchorEl)

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleDeleteAlert = (alertId: number) => {
    setAlerts(context.alerts.filter(alert => alert.id !== alertId))
    setStoredAlerts(storedAlerts?.filter(alert => alert.id !== alertId))
  }

  const handleClearAlerts = () => {
    setAlerts([])
    setStoredAlerts([])
  }

  useEffectOnce(() => {
    setIsClient(true)
  })

  return (
    <>
      <Tooltip title='Latest Alerts'>
        <StyledBadge badgeContent={isClient ? storedAlerts?.length : null} color='primary' max={20} className='p-1'>
          <IconButton className='text-textPrimary' onClick={handleClick}>
            <i className='ri-notification-2-line' />
          </IconButton>
        </StyledBadge>
      </Tooltip>
      <Menu anchorEl={anchorEl} open={open} onClose={handleClose} className='max-h-full'>
        <ListItem className='flex justify-between items-center'>
          <Typography className='w-max'>{storedAlerts?.length ? 'Latest' : 'No'} Alerts</Typography>
          {!storedAlerts?.length || (
            <Button onClick={() => handleClearAlerts()} className='py-1 px-2'>
              Clear
            </Button>
          )}
        </ListItem>
        {!storedAlerts?.length || (
          <List className='flex flex-wrap max-w-xl w-xl'>
            {storedAlerts.map((alert, index) => (
              <ListItem key={index}>
                <StormAlert
                  title={String(alert.roomName)}
                  alert={alert}
                  onDeleteAlert={() => handleDeleteAlert(alert.id)}
                />
              </ListItem>
            ))}
          </List>
        )}
      </Menu>
    </>
  )
}

export default AlertsMenu
