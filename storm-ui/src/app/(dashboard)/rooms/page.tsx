import type { Metadata } from 'next'

import RoomSummary from '@/components/RoomSummary'

export const metadata: Metadata = {
  title: 'Rooms Summary'
}

export default function Page() {
  return (
    <div>
      <h1 className='mb-5'>Rooms Summary</h1>
      <RoomSummary />
    </div>
  )
}