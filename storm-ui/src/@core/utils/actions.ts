'use server'

const jsonHeaders = {
  'Content-Type': 'application/json'
}

export async function deleteRoom(roomId: number) {
  const requestOptions = {
    method: 'DELETE',
    headers: jsonHeaders,
    body: JSON.stringify({
      id: roomId
    })
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/rooms`, requestOptions)
    .then(async () => {
      return { message: 'Deleted Room.' }
    })
    .catch(err => {
      return { message: 'API Error: Failed to Delete Room.', error: err }
    })
}

export async function importRooms(formData: FormData) {
  // Define the request options with method and body as FormData
  const requestOptions = {
    method: 'POST',
    body: formData
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/data`, requestOptions)
    .then(async res => {
      return { message: res.json() }
    })
    .catch(err => {
      return { message: 'API Error: Failed to Import Rooms.', error: err }
    })
}

async function manageDevice(roomId: number, type: string, deviceId?: number, name?: string, errorMsg?: string) {
  const requestOptions = {
    method: deviceId ? 'PUT' : 'POST',
    headers: jsonHeaders
  }

  const data: any = {
    room_id: roomId
  }

  if (deviceId) data.id = deviceId
  else if (name) data.name = name

  let endpoint = 'doors'

  if (type !== 'door') {
    endpoint = 'devices'
    data.type = type
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/${endpoint}`, {
    ...requestOptions,
    body: JSON.stringify(data)
  })
    .then(async res => {
      return { message: res.json() }
    })
    .catch(err => {
      return { message: `API Error: ${errorMsg}`, error: err }
    })
}

export async function createDevice(roomId: number, name: string, type: string) {
  return manageDevice(roomId, type, undefined, name, `Failed to Create Device (${type}).`)
}

export async function assignDevice(roomId: number, deviceId: number, type: string) {
  return manageDevice(roomId, type, deviceId, undefined, `Failed to Assign Device (${type}: ${deviceId}).`)
}

export async function createRoom(formData: FormData) {
  const requestOptions = {
    method: 'POST',
    body: formData
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/rooms`, requestOptions)
    .then(async res => {
      return { message: res.json() }
    })
    .catch(err => {
      return { message: 'API Error: Failed to Create Room.', error: err }
    })
}

export async function editRoom(roomId: string, formData: FormData) {
  const requestOptions = {
    method: 'PUT',
    body: formData
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/room/${roomId}/`, requestOptions)
    .then(async res => {
      return { message: res.json() }
    })
    .catch(err => {
      return { message: 'API Error: Failed to Edit Room.', error: err }
    })
}

export async function deleteDevice(deviceId: number, type: string) {
  const requestOptions = {
    method: 'DELETE',
    headers: jsonHeaders,
    body: JSON.stringify({
      id: deviceId,
      type: type
    })
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/devices`, requestOptions)
    .then(async () => {
      return { message: `Deleted ${type} (${deviceId}).` }
    })
    .catch(err => {
      return { message: 'API Error: Failed to Delete Device.', error: err }
    })
}

export async function deleteDoor(doorId: number, roomId: number) {
  const requestOptions = {
    method: 'DELETE',
    headers: jsonHeaders,
    body: JSON.stringify({
      id: doorId,
      room_id: roomId
    })
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/doors`, requestOptions)
    .then(async () => {
      return { message: `Deleted Door (${doorId} -> ${roomId}).` }
    })
    .catch(err => {
      return { message: 'API Error: Failed to Delete Door.', error: err }
    })
}

export async function updateDeviceAction(deviceId: number, type: string, action: boolean) {
  const requestOptions = {
    method: 'PATCH',
    headers: jsonHeaders
  }

  const data: any = {
    id: deviceId,
    action: action
  }

  let endpoint = 'doors'

  if (type !== 'door') {
    endpoint = 'devices'
    data.type = type
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/${endpoint}`, {
    ...requestOptions,
    body: JSON.stringify(data)
  })
    .then(async () => {
      return { message: `Set ${type} (ID ${deviceId}) Action to ${action}.` }
    })
    .catch(err => {
      return { message: `API Error: Failed to Set ${type} Action.`, error: err }
    })
}

export async function confirmAlerts(alertIds: number[]) {
  const requestOptions = {
    method: 'PUT',
    headers: jsonHeaders,
    body: JSON.stringify({
      ids: alertIds
    })
  }

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/context`, requestOptions)
    .then(async () => {
      return { message: `Confirmed Alerts: ${alertIds}.` }
    })
    .catch(err => {
      return { message: 'API Error: Failed to Confirm Alerts.', error: err }
    })
}
