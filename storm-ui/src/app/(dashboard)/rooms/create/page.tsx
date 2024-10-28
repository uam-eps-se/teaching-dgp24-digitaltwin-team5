import RoomForm from '@views/dashboard/RoomForm'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Create Room'
}

export default function Page() {
  return (
    <div>
      <h1 className='mb-5'>Create Room</h1>
      <RoomForm />
    </div>
  )
}