'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

import { z } from 'zod'

const FormSchema = z.object({
  id: z.string(),
  customerId: z.string({
    invalid_type_error: 'Please select a customer.'
  }),
  amount: z.coerce.number().gt(0, { message: 'Please enter an amount greater than $0.' }),
  status: z.enum(['pending', 'paid'], {
    invalid_type_error: 'Please select an invoice status.'
  }),
  date: z.string()
})

const CreateInvoice = FormSchema.omit({ id: true, date: true })
const UpdateInvoice = FormSchema.omit({ id: true, date: true })

export type State = {
  errors?: {
    customerId?: string[]
    amount?: string[]
    status?: string[]
  }
  message?: string | null
}

export async function createInvoice(prevState: State, formData: FormData) {
  // Validate form using Zod
  const validatedFields = CreateInvoice.safeParse({
    customerId: formData.get('customerId'),
    amount: formData.get('amount'),
    status: formData.get('status')
  })

  // If form validation fails, return errors early. Otherwise, continue.
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: 'Missing Fields. Failed to Create Invoice.'
    }
  }

  // Prepare data for insertion into the database
  const { customerId, amount, status } = validatedFields.data
  const amountInCents = amount * 100
  const date = new Date().toISOString().split('T')[0]

  // Insert data into the database
  try {
    ///////////////
  } catch (error) {
    // If a database error occurs, return a more specific error.
    return {
      message: 'Database Error: Failed to Create Invoice.'
    }
  }

  // Revalidate the cache for the invoices page and redirect the user.
  revalidatePath('/dashboard/invoices')
  redirect('/dashboard/invoices')
}

export async function updateInvoice(id: string, prevState: State, formData: FormData) {
  const validatedFields = UpdateInvoice.safeParse({
    customerId: formData.get('customerId'),
    amount: formData.get('amount'),
    status: formData.get('status')
  })

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: 'Missing Fields. Failed to Update Invoice.'
    }
  }

  const { customerId, amount, status } = validatedFields.data
  const amountInCents = amount * 100

  try {
    /////////////////
  } catch (error) {
    return { message: 'Database Error: Failed to Update Invoice.' }
  }

  revalidatePath('/dashboard/invoices')
  redirect('/dashboard/invoices')
}

export async function deleteRoom(roomId: number) {
  const requestOptions = {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
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
    headers: { 'Content-Type': 'application/json' }
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
    headers: { 'Content-Type': 'application/json' },
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
    headers: { 'Content-Type': 'application/json' },
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
    headers: { 'Content-Type': 'application/json' }
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

  console.log('Placeholder', data)

  return { message: `Set ${type} (ID ${deviceId}) Action to ${action}.` }

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
