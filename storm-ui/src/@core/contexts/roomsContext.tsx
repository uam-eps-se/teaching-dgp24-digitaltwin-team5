'use client'

import type { ReactNode, Dispatch, SetStateAction } from 'react';
import { createContext, useState } from 'react';

import type { RoomSummaryRow } from '../types';
import { fetchRooms } from '../utils/data';

type RoomsData = {
  data: RoomSummaryRow[],
  fetched: boolean
}

interface RoomsContextType {
  rooms: RoomsData;
  deleting: boolean;
  setRooms: Dispatch<SetStateAction<RoomsData>>;
  setDeleting: Dispatch<SetStateAction<boolean>>;
  updateRooms: () => Promise<void>;
}

export const RoomsContext = createContext<RoomsContextType>({
  rooms: {
    data: [],
    fetched: false
  },
  deleting: false,
  setRooms: () => { },
  setDeleting: () => { },
  updateRooms: async () => { }
});

// RoomsProvider component to provide context
export const RoomsProvider = ({ children }: { children: ReactNode }) => {
  const [rooms, setRooms] = useState<RoomsData>({
    data: [],
    fetched: false,
  });

  const [deleting, setDeleting] = useState(false);

  const updateRooms = async () => {
    return fetchRooms().then(rs => {
      if (rs && !deleting) setRooms({ data: rs, fetched: true });
    })
  }

  return (
    <RoomsContext.Provider value={{ rooms, deleting, setRooms, setDeleting, updateRooms }}>
      {children}
    </RoomsContext.Provider>
  );
};
