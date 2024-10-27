import RoomDetail from "@components/RoomDetail"

export async function generateMetadata({ params }: { params: { id: string } }) {
  return {
    title: `Room ${params.id}`,
  };
}

export default function Page({ params }: { params: { id: string } }) {
  return (
    <RoomDetail roomId={params.id} />
  )
}