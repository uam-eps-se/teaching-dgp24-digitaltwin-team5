'use client'

import { RoomDetailData } from '@core/types'
import { mdiHomeOutline, mdiIdentifier } from '@mdi/js';
import Icon from '@mdi/react';
import { Chip } from '@mui/material'
import { useEffect, useState } from 'react'
import { fetchRoom } from '@core/utils/data'
import RoomForm from '@/views/dashboard/RoomForm'

const RoomEdit = (props: { roomId: string }) => {
  const [room, setRoom] = useState<RoomDetailData>();

  useEffect(() => {
    fetchRoom(props.roomId).then(r => {
      if (r) setRoom(r);
    });
  }, []);

  return (
    <div>
      {
        room ?
          <h1 className='mb-5 flex justify-between items-center'>
            Edit Room
            <div>
              <Chip
                label={`${room.size} m²`}
                icon={<Icon path={mdiHomeOutline} size={1} />}
                className="mr-4"
              />
              <Chip
                label={room.id}
                icon={<Icon path={mdiIdentifier} size={1} />}
              />
            </div>
          </h1>
          :
          <h1 className='mb-5'>Edit Room</h1>
      }
      {
        room && <RoomForm room={room} />
      }
    </div>
  )
}

export default RoomEdit
