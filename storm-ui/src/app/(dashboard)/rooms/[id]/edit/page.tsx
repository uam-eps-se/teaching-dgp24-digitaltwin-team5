import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Edit Room'
}

export default function Page({ params }: { params: { id: string } }) {
  // Fetch room data and pre-populate Form component
  return (
    <div>
      <h1 className='mb-5'>Edit Room</h1>
      ID: {params.id}
    </div>
  )
}