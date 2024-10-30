'use client'

import { useState } from 'react';

import { useRouter } from 'next/navigation';

import {
  Box,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
} from '@mui/material';

import { mdiPlus, mdiWindowClose, mdiTrashCan, mdiHomeEdit } from '@mdi/js';
import Icon from '@mdi/react';

import type { RoomDetailData } from '@/@core/types';
import DeleteRoomModal from './DeleteRoomModal';

const actions = (roomId: number) => [
  { icon: <Icon path={mdiTrashCan} size={1} color="var(--mui-palette-error-main)" />, name: 'Delete Room' },
  { icon: <Icon path={mdiHomeEdit} size={1} />, name: 'Edit Room', path: `/rooms/${roomId}/edit` },
];

const RoomDetailActions = (props: { room: RoomDetailData }) => {
  const [openDelete, setOpenDelete] = useState(false);
  const router = useRouter();
  const room = props.room;

  return (
    <div>
      <Box
        sx={{ position: 'fixed', bottom: '50px', right: '50px', display: 'flex', alignItems: 'flex-end' }}
      >
        {
          room &&
          <SpeedDial
            ariaLabel="Rooms Options"
            icon={
              <SpeedDialIcon
                icon={<Icon path={mdiPlus} size={1} />}
                openIcon={<Icon path={mdiWindowClose} size={1} />}
              />
            }
          >
            {
              actions(room.id).map(action =>
                <SpeedDialAction
                  key={action.name}
                  icon={action.icon}
                  tooltipOpen
                  tooltipTitle={action.name}
                  onClick={() => {
                    if (action.path)
                      router.push(`/rooms/${room.id}/edit`);
                    else
                      setOpenDelete(true);
                  }}
                  sx={{ whiteSpace: "nowrap", maxWidth: "none" }}
                />
              )
            }
          </SpeedDial>
        }
        <DeleteRoomModal
          roomId={room.id}
          roomName={room.name}
          open={openDelete}
          setOpen={setOpenDelete}
        />
      </Box>
    </div>
  )
}

export default RoomDetailActions