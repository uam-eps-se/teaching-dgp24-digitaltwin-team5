import type { Metadata } from 'next'

import RoomEdit from '@/components/RoomEdit'

export const metadata: Metadata = {
  title: 'Edit Room'
}

export default function Page({ params }: { params: { id: string } }) {
  return (
    <div>
      <RoomEdit roomId={params.id} />
    </div>
  )
}
