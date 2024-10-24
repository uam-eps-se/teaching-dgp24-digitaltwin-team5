import * as React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton
} from '@mui/material';

import { mdiTrashCan } from '@mdi/js';
import Icon from '@mdi/react';
import { deleteRoom } from '@core/utils/actions';

export default function DeleteRoomModal(props: { roomId: number, roomName: string }) {
  const [open, setOpen] = React.useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  return (
    <div>
      <IconButton color='error' onClick={handleOpen}><Icon path={mdiTrashCan} size={1} /></IconButton>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="delete-room-title"
        aria-describedby="delete-room-title-description"
        closeAfterTransition
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
          <Button color='secondary' onClick={handleClose}>Cancel</Button>
          <Button color='error' onClick={() => {
              deleteRoom(props.roomId);
              handleClose()
            }} 
            autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
