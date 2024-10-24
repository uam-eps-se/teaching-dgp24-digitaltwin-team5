// MUI Imports
import Chip from '@mui/material/Chip'
import { useTheme } from '@mui/material/styles'

// Third-party Imports
import PerfectScrollbar from 'react-perfect-scrollbar'

// Type Imports
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
import { RoomSummaryRow } from '@core/types'
import { fetchRooms } from '@core/utils/data'
import { useEffect, useState } from 'react'
import Icon from '@mdi/react'
import { mdiDotsHorizontal, mdiHomePlus } from '@mdi/js'

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
  // Hooks
  const theme = useTheme()
  const { isBreakpointReached, transitionDuration } = useVerticalNav()

  const ScrollWrapper = isBreakpointReached ? 'div' : PerfectScrollbar

  const [rooms, setRooms] = useState<RoomSummaryRow[]>([]);

  // Change with event subscription OR setInterval
  useEffect(() => {
    fetchRooms().then(rs => {
      setRooms(rs);
    })
  }, []);

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
        <MenuItem
          href={`/rooms`}
        // suffix={<Chip label='Pro' size='small' color='primary' variant='tonal' />}
        >
          Rooms Summary
        </MenuItem>
        <SubMenu
          label='My Rooms'
          icon={<i className='ri-home-smile-line' />}
          defaultOpen
          suffix={
            rooms.length > 0 &&
            <Chip label={rooms.length} size='small' color='primary' variant='tonal' />
          }
        >
          {
            rooms.toSorted((a, b) => a.id - b.id).slice(0, 10).map((room) => (
              <MenuItem key={room.id} href={`/rooms/${room.id}`}>{room.name}</MenuItem>
            ))
          }
          {
            rooms.length > 10 &&
            <MenuItem disabled>
              <Icon path={mdiDotsHorizontal} size={1} />
            </MenuItem>
          }
        </SubMenu>
        <MenuSection label='Actions' />
        <MenuItem href='/rooms/create' prefix={<Icon path={mdiHomePlus} size={1} />}>
          Create Room
        </MenuItem>
      </Menu>
    </ScrollWrapper>
  )
}

export default VerticalMenu
