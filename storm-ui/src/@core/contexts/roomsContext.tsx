'use client'

import React, { createContext, useState, ReactNode } from 'react';
import { RoomSummaryRow } from '../types';

type RoomsData = {
  data: RoomSummaryRow[],
  fetched: boolean
}

interface RoomsContextType {
  rooms: RoomsData;
  deleting: boolean;
  setRooms: React.Dispatch<React.SetStateAction<RoomsData>>;
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
  const [rooms, setRooms] = useState<RoomsData>({
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
