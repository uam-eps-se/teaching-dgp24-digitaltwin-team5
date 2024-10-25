'use client'

import React, { createContext, useState, ReactNode } from 'react';
import { RoomSummaryRow } from '../types';

type RoomData = {
  data: RoomSummaryRow[],
  fetched: boolean
}

interface RoomsContextType {
  rooms: RoomData;
  setRooms: React.Dispatch<React.SetStateAction<RoomData>>;
}

export const RoomsContext = createContext<RoomsContextType>({
  rooms: {
    data: [],
    fetched: false
  },
  setRooms: () => { }
});

// RoomsProvider component to provide context
export const RoomsProvider = ({ children }: { children: ReactNode }) => {
  const [rooms, setRooms] = useState<RoomData>({
    data: [],
    fetched: false,
  });

  return (
    <RoomsContext.Provider value={{ rooms, setRooms }}>
      {children}
    </RoomsContext.Provider>
  );
};
