export async function generateMetadata({ params }: { params: { id: string } }) {
  return {
    title: params.id,
  }
}

export default function Page({ params }: { params: { id: string } }) {
  return <div>Room ID: {params.id}</div>
}