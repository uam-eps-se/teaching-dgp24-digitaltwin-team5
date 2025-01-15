// MUI Imports
import { useContext, useEffect, useState } from 'react'

import { useTheme, alpha } from '@mui/material/styles'

// Third-party Imports
import PerfectScrollbar from 'react-perfect-scrollbar'

// Type Imports
import Icon from '@mdi/react'

import { mdiDotsHorizontal, mdiHomePlus } from '@mdi/js'

import type { SnackbarCloseReason } from '@mui/material'
import { Chip, Paper, Snackbar } from '@mui/material'

import { useEffectOnce } from 'react-use'

import type { VerticalMenuContextProps } from '@menu/components/vertical-menu/Menu'

// Component Imports
import { Menu, SubMenu, MenuItem, MenuSection } from '@menu/vertical-menu'

// Hook Imports
import useVerticalNav from '@menu/hooks/useVerticalNav'

// Styled Component Imports
import StyledVerticalNavExpandIcon from '@menu/styles/vertical/StyledVerticalNavExpandIcon'

// Style Imports
import menuItemStyles from '@core/styles/vertical/menuItemStyles'
import menuSectionStyles from '@core/styles/vertical/menuSectionStyles'

import StormAlert from '@components/StormAlert'

import type { Alert } from '@core/types'
import { AlertType } from '@core/types'

import { LayoutContext } from '@core/contexts/layoutContext'
import { useEventSource } from '@core/hooks/useEventSource'
import { confirmAlerts } from '@core/utils/actions'

type RenderExpandIconProps = {
  open?: boolean
  transitionDuration?: VerticalMenuContextProps['transitionDuration']
}

const RenderExpandIcon = ({ open, transitionDuration }: RenderExpandIconProps) => (
  <StyledVerticalNavExpandIcon open={open} transitionDuration={transitionDuration}>
    <i className='ri-arrow-right-s-line' />
  </StyledVerticalNavExpandIcon>
)

const VerticalMenu = ({ scrollMenu }: { scrollMenu: (container: any, isPerfectScrollbar: boolean) => void }) => {
  const ignoredReasons = ['clickaway', 'escapeKeyDown']

  const theme = useTheme()
  const { isBreakpointReached, transitionDuration } = useVerticalNav()

  const { context, storedAlerts, setStoredAlerts, setContext, updateContext, setAlerts } = useContext(LayoutContext)
  const { addEventHandler } = useEventSource(['context'])

  const [openSnackbar, setOpenSnackbar] = useState<boolean>(false)
  const [currentAlert, setCurrentAlert] = useState<Alert>()

  const ScrollWrapper = isBreakpointReached ? 'div' : PerfectScrollbar

  const showNextAlert = () => {
    if (context.alerts.length) {
      setCurrentAlert(context.alerts[0])
      setOpenSnackbar(true)
    } else setCurrentAlert(undefined)
  }

  const handleCloseSnackbar = (reason: SnackbarCloseReason) => {
    if (!ignoredReasons.includes(reason)) {
      setOpenSnackbar(false)

      // Remove current alert from queue
      if (context.alerts.length) setAlerts(context.alerts.slice(1))
    }
  }

  useEffectOnce(() => {
    const pendingAlerts: Alert[] = JSON.parse(localStorage.getItem('pending-alerts') || '[]')

    setContext(prevContext => ({
      rooms: prevContext.rooms,
      alerts: pendingAlerts
    }))
    updateContext().then(() => {
      addEventHandler('message', msgEvent => updateContext(msgEvent.data))
    })
  })

  useEffect(() => {
    // Cycle through alerts
    if (!openSnackbar && context.alerts.length) {
      setTimeout(() => showNextAlert(), 500)
    }

    // Store pending alerts
    localStorage.setItem('pending-alerts', JSON.stringify(context.alerts))
    // eslint-disable-next-line
  }, [context.alerts])

  return (
    // eslint-disable-next-line lines-around-comment
    <ScrollWrapper
      {...(isBreakpointReached
        ? {
            className: 'bs-full overflow-y-auto overflow-x-hidden',
            onScroll: container => scrollMenu(container, false)
          }
        : {
            options: { wheelPropagation: false, suppressScrollX: true },
            onScrollY: container => scrollMenu(container, true)
          })}
    >
      {/* Vertical Menu */}
      <Menu
        menuItemStyles={menuItemStyles(theme)}
        renderExpandIcon={({ open }) => <RenderExpandIcon open={open} transitionDuration={transitionDuration} />}
        renderExpandedMenuItemIcon={{ icon: <i className='ri-circle-line' /> }}
        menuSectionStyles={menuSectionStyles(theme)}
      >
        <MenuSection label='Rooms' />
        <MenuItem href={`/rooms`}>Rooms Summary</MenuItem>
        <SubMenu
          label='My Rooms'
          icon={<i className='ri-home-smile-line' />}
          defaultOpen
          suffix={
            context.rooms.length > 0 && (
              <Chip label={context.rooms.length} size='small' color='primary' variant='tonal' />
            )
          }
        >
          {context.rooms
            .toSorted((a, b) => a.id - b.id)
            .slice(0, 10)
            .map(room => (
              <MenuItem key={room.id} href={`/rooms/${room.id}`}>
                {room.name}
              </MenuItem>
            ))}
          {context.rooms.length > 10 && (
            <MenuItem disabled>
              <Icon path={mdiDotsHorizontal} size={1} />
            </MenuItem>
          )}
        </SubMenu>
        <MenuSection label='Actions' />
        <MenuItem href='/rooms/create' prefix={<Icon path={mdiHomePlus} size={1} />}>
          Create Room
        </MenuItem>
        {!currentAlert || (
          <Snackbar
            anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
            open={openSnackbar}
            onClose={(_event, reason) => handleCloseSnackbar(reason)}
            autoHideDuration={
              currentAlert.type === AlertType.DANGER
                ? 60000 // 1 minute timeout for DANGER
                : 30000 // 30 second timeout for WARNING
            }
          >
            <Paper
              className='max-w-2xl w-full max-h-full backdrop-blur'
              sx={{
                backgroundColor: alpha(theme.palette.background.paper, 0.5)
              }}
            >
              <StormAlert
                title={currentAlert.roomName}
                alert={currentAlert}
                showTime={false}
                onDeleteAlert={() => {
                  if (currentAlert && storedAlerts?.length) {
                    setStoredAlerts(storedAlerts.filter(alert => alert.id !== currentAlert.id))
                    confirmAlerts([currentAlert.id])
                  }

                  handleCloseSnackbar('timeout')
                }}
              ></StormAlert>
            </Paper>
          </Snackbar>
        )}
      </Menu>
    </ScrollWrapper>
  )
}

export default VerticalMenu
