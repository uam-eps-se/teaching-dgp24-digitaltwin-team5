'use client'

import { useEffect, useState } from "react";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { useInterval } from "react-use";

import { Box, Chip, Fab } from "@mui/material";

import Icon from "@mdi/react";

import { mdiChartLine, mdiCog, mdiFloorPlan, mdiHomeOutline, mdiIdentifier } from "@mdi/js";

import { TabContext, TabPanel } from "@mui/lab";

import { useDebouncedCallback } from "use-debounce";

import { fetchRoom } from "@core/utils/data";
import type { RoomDetailData } from "@core/types";

import RoomDetailButtons from "./actionButtons/RoomDetailButtons";

import RoomStructure from "@views/dashboard/RoomStructure";
import RoomStatus from "@views/dashboard/RoomStatus";

export default function RoomDetail(props: { roomId: string }) {
  const [room, setRoom] = useState<RoomDetailData>();
  const [titleChanged, setTitleChanged] = useState<boolean>(false);
  const [tab, setTab] = useState("0");
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const intervalDelay = process.env.NEXT_PUBLIC_POLL_DELAY_MS || 2000;

  const updateRoomData = async () => {
    return fetchRoom(props.roomId).then(r => {
      if (r) setRoom(r);

      if (!titleChanged && r.name) {
        setTitleChanged(true);
        document.title = document.title.replace(`Room ${props.roomId}`, r.name);
      }
    });
  }

  useEffect(() => {
    updateRoomData().then(() => {
      const routeTab = searchParams.get('tab');

      if (routeTab) setTab(routeTab);
    });
  }, []);

  useInterval(
    () => updateRoomData(),
    intervalDelay as number
  )

  const setTabParam = useDebouncedCallback((tab: string) => {
    router.push(`${pathname}?tab=${tab}`);
  }, 2000);

  const handleTab = (tab: string) => {
    setTab(tab);
    setTabParam(tab);
  }

  const fabTabs = [
    {
      label: 'Room Structure',
      onKeyDown: (e: KeyboardEvent) => {
        if (e.key === "ArrowRight") {
          handleTab("1");
          document.getElementById('roomdetail-tab-1')?.focus()
        }
      },
      icon: mdiFloorPlan
    },
    {
      label: 'Real-time Status',
      onKeyDown: (e: KeyboardEvent) => {
        if (e.key === "ArrowLeft") {
          handleTab("0");
          document.getElementById('roomdetail-tab-0')?.focus()
        }

        if (e.key === "ArrowRight") {
          handleTab("2");
          document.getElementById('roomdetail-tab-2')?.focus()
        }
      },
      icon: mdiChartLine
    },
    {
      label: 'Control Panel',
      onKeyDown: (e: KeyboardEvent) => {
        if (e.key === "ArrowLeft") {
          handleTab("1");
          document.getElementById('roomdetail-tab-1')?.focus()
        }
      },
      icon: mdiCog
    }
  ]

  return (
    <div>
      {
        room ?
          <>
            <h1 className='mb-5 flex justify-between items-center'>
              {room.name}
              <div>
                <Chip
                  label={`${room.size} m²`}
                  icon={<Icon path={mdiHomeOutline} size={1} />}
                  className="mr-4"
                />
                <Chip
                  label={room.id}
                  icon={<Icon path={mdiIdentifier} size={1} />}
                />
              </div>
            </h1>
            <TabContext value={tab}>
              <TabPanel value="0"><RoomStructure room={room} /></TabPanel>
              <TabPanel value="1"><RoomStatus room={room} /></TabPanel>
              <TabPanel value="2"><h3>Control Panel Placeholder</h3></TabPanel>
              <Box
                sx={{
                  position: 'fixed',
                  left: 0,
                  right: 0,
                  display: 'flex',
                  gap: '5vw',
                  bottom: '80px',
                  marginX: 'auto',
                  width: 'fit-content'
                }}
              >
                {
                  fabTabs.map(({ label, onKeyDown, icon }, idx) => {
                    return (
                      <Fab
                        key={label}
                        id={`roomdetail-tab-${idx}`}
                        color={tab === idx.toString() ? 'primary' : 'secondary'}
                        variant="extended"
                        onClick={() => handleTab(idx.toString())}
                        onKeyDown={(e) => onKeyDown(e as unknown as KeyboardEvent)}
                      >
                        <Icon path={icon} size={1} style={{ marginRight: 10 }} />
                        {label}
                      </Fab>
                    )
                  })
                }
              </Box>
            </TabContext>
            <RoomDetailButtons room={room} />
          </> :
          <h1 className='mb-5 flex justify-between items-center'>
            Loading room...
          </h1>
      }
    </div>
  );
}
