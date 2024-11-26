import type { Metadata } from 'next'

import RoomForm from '@views/dashboard/RoomForm'

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
