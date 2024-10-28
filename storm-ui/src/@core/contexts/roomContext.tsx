'use client'

import React, { createContext, useState, ReactNode } from 'react';
import { RoomDetailData } from '../types';

interface RoomContextType {
  room: RoomDetailData | undefined;
  setRoom: React.Dispatch<React.SetStateAction<RoomDetailData | undefined>>;
}

export const RoomContext = createContext<RoomContextType>({
  room: undefined,
  setRoom: () => { },
});

// RoomsProvider component to provide context
export const RoomsProvider = ({ children }: { children: ReactNode }) => {
  const [room, setRoom] = useState<RoomDetailData>();

  return (
    <RoomContext.Provider value={{ room, setRoom }}>
      {children}
    </RoomContext.Provider>
  );
};
