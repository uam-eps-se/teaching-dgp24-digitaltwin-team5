'use client'

const requestOptions = {
  method: 'GET'
}

export async function fetchRooms() {
  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/rooms`, requestOptions)
    .then(async res => res.json())
    .catch(err => {
      console.error('API Error: Failed to Get Rooms.')
      console.error(err)
    })
}

export async function fetchRoom(roomId: string) {
  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/room/${roomId}`, requestOptions)
    .then(async res => res.json())
    .catch(err => {
      console.error(`API Error: Failed to Get Room with ID ${roomId}.`)
      console.error(err)
    })
}

export async function fetchFreeDevices() {
  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/devices`, requestOptions)
    .then(async res => res.json())
    .catch(err => {
      console.error(`API Error: Failed to Get Available Devices.`)
      console.error(err)
    })
}

export async function fetchFreeDoors() {
  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/doors`, requestOptions)
    .then(async res => res.json())
    .catch(err => {
      console.error(`API Error: Failed to Get Available Doors.`)
      console.error(err)
    })
}

export async function fetchContext() {
  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/context`, requestOptions)
    .then(async res => res.json())
    .catch(err => {
      console.error(`API Error: Failed to Get Context.`)
      console.error(err)
    })
}
