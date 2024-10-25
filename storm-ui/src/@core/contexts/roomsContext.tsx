'use client'

import React, { createContext, useState, ReactNode } from 'react';
import { RoomSummaryRow } from '../types';

type RoomData = {
  data: RoomSummaryRow[],
  fetched: boolean
}

interface RoomsContextType {
  rooms: RoomData;
  deleting: boolean;
  setRooms: React.Dispatch<React.SetStateAction<RoomData>>;
  setDeleting: React.Dispatch<React.SetStateAction<boolean>>;
}

export const RoomsContext = createContext<RoomsContextType>({
  rooms: {
    data: [],
    fetched: false
  },
  deleting: false,
  setRooms: () => { },
  setDeleting: () => { }
});

// RoomsProvider component to provide context
export const RoomsProvider = ({ children }: { children: ReactNode }) => {
  const [rooms, setRooms] = useState<RoomData>({
    data: [],
    fetched: false,
  });

  const [deleting, setDeleting] = useState(false);

  return (
    <RoomsContext.Provider value={{ rooms, deleting, setRooms, setDeleting }}>
      {children}
    </RoomsContext.Provider>
  );
};
