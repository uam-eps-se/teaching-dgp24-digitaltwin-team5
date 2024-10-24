import { usePathname } from "next/navigation"
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Edit Room'
}

export default function Page({ params }: { params: { id: string } }) {
  // Fetch room data and pre-populate Form component
  return (
    <div>
      <h2 className='mb-10'>Edit Room</h2>
      ID: {params.id}
    </div>
  )
}