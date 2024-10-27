import { Dispatch, SetStateAction, useContext } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';

import { deleteRoom } from '@core/utils/actions';
import { RoomsContext } from '@core/contexts/roomsContext';
import { useRouter, usePathname } from 'next/navigation';

export default function DeleteRoomModal(props: {
  roomId: number,
  roomName: string,
  open: boolean,
  setOpen: Dispatch<SetStateAction<boolean>>
}) {
  const handleClose = () => props.setOpen(false);
  const { setDeleting, rooms, setRooms } = useContext(RoomsContext);
  const router = useRouter();
  const pathName = usePathname();

  return (
    <div>
      <Dialog
        open={props.open}
        onClose={handleClose}
        aria-labelledby="delete-room-title"
        aria-describedby="delete-room-title-description"
        closeAfterTransition
        disableRestoreFocus
      >
        <DialogTitle id="delete-room-title">
          Delete {props.roomName}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-room-description-1">
            Are you sure you want to delete <b>{props.roomName}</b>?
          </DialogContentText>
          <DialogContentText id="delete-room-description-2">
            Static components will remain available for other rooms.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            color='secondary'
            onClick={handleClose}
          >
            Cancel
          </Button>
          <Button
            color='error'
            onClick={async () => {
              setDeleting(true);
              const res = await deleteRoom(props.roomId);

              if (!('error' in res)) {
                const idx = rooms.data.findIndex(x => x.id == props.roomId);
                if (idx !== -1)
                  setRooms({
                    data: [...rooms.data.slice(0, idx), ...rooms.data.slice(idx + 1)],
                    fetched: true
                  });
              } else {
                console.error(res); // Show error on UI?
              }
              setDeleting(false);
              if (pathName !== '/rooms')
                router.push('/rooms');
              handleClose();
            }}
            autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
