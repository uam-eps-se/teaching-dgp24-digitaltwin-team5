import RoomEdit from '@/components/RoomEdit'
import { Metadata } from 'next'

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