import { useContext, useState } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Tooltip
} from '@mui/material';

import { mdiTrashCan } from '@mdi/js';
import Icon from '@mdi/react';
import { deleteRoom } from '@core/utils/actions';
import { RoomsContext } from '@core/contexts/roomsContext';

export default function DeleteRoomModal(props: { roomId: number, roomName: string }) {
  const [open, setOpen] = useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);
  const { setDeleting, rooms, setRooms } = useContext(RoomsContext);

  return (
    <div>
      <Tooltip title={`Delete ${props.roomName}`}>
        <IconButton color='error' onClick={handleOpen}><Icon path={mdiTrashCan} size={1} /></IconButton>
      </Tooltip>
      <Dialog
        open={open}
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
          <DialogContentText id="delete-room-description">
            Are you sure you want to delete {props.roomName}?
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
