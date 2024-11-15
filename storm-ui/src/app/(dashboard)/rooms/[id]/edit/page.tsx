import type { Metadata } from 'next'

import RoomEdit from '@views/dashboard/RoomEdit'

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
