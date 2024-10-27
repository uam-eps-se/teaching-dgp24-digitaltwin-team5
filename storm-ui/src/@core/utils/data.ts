'use client'

export async function fetchRooms() {
  const requestOptions = {
    method: "GET",
  };

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/rooms`, requestOptions)
    .then(async (res) => res.json())
    .catch(err => {
      console.error('Database Error: Failed to Get Rooms.');
      console.error(err)
    })
}

export async function fetchRoom(roomId: string) {
  const requestOptions = {
    method: "GET",
  };

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/room/${roomId}`, requestOptions)
    .then(async (res) => res.json())
    .catch(err => {
      console.error(`Database Error: Failed to Get Room with ID ${roomId}.`);
      console.error(err)
    })
}
