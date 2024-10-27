'use client'

import React, { createContext, useState, ReactNode } from 'react';
import { RoomDetailData } from '../types';

type RoomData = {
  data: RoomDetailData | undefined,
  fetched: boolean
}

interface RoomContextType {
  room: RoomData;
  setRoom: React.Dispatch<React.SetStateAction<RoomData>>;
}

export const RoomContext = createContext<RoomContextType>({
  room: {
    data: undefined,
    fetched: false
  },
  setRoom: () => { },
});

// RoomsProvider component to provide context
export const RoomsProvider = ({ children }: { children: ReactNode }) => {
  const [room, setRoom] = useState<RoomData>({
    data: undefined,
    fetched: false,
  });

  return (
    <RoomContext.Provider value={{ room, setRoom }}>
      {children}
    </RoomContext.Provider>
  );
};
