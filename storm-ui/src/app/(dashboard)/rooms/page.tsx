import RoomSummary from '@/components/RoomSummary'

import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Rooms Summary'
}

export default function Page() {
  return (
    <div>
      <h2 className='mb-5'>Rooms Summary</h2>
      <RoomSummary />
    </div>
  )
}