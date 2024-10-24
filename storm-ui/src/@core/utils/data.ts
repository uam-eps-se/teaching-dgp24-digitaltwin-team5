'use server'

import fs from 'fs/promises';

export async function fetchRooms() {
  try {
    const roomsJson = await fs.readFile('src/testdata/rooms/rooms-get.json');
    const rooms = JSON.parse(roomsJson.toString('utf-8'));
    return rooms;
  }
  catch (error) {
    console.error('Database Error: Failed to Get Rooms.');
    throw error
  }
}
