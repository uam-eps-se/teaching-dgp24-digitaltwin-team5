'use client'

import { useContext, useEffect, useState } from 'react'

import { useRouter } from 'next/navigation'

import { Box, Grid, TextField, Divider, Button, Typography, Autocomplete, Chip } from '@mui/material'

import { mdiDoorOpen, mdiFan, mdiLightbulbOn, mdiTrashCan, mdiWindowClosedVariant } from '@mdi/js'

import Icon from '@mdi/react'

import { useInterval } from 'react-use'

import { z } from 'zod'

import type { AvailableDevices, Device, Door, RoomDetailData, RoomDevice } from '@core/types'

import CreateDevicesDial from '@components/actionButtons/CreateDevicesButtons'

import { fetchFreeDevices, fetchFreeDoors } from '@/@core/utils/data'

import { assignDevice, createDevice, createRoom, deleteDevice, deleteDoor, editRoom } from '@core/utils/actions'
import { RoomsContext } from '@core/contexts/roomsContext'
import DeleteRoomModal from '@/components/actionButtons/DeleteRoomModal'

const RoomFormSchema = z.object({
  name: z.string().min(1, 'Room name is required'),
  size: z.coerce.number().nonnegative('Room size must be a positive value'),
  devices: z.string().optional()
})

function RoomForm(props: { room?: RoomDetailData }) {
  const isEdit = props.room !== undefined
  const router = useRouter()
  const [open, setOpen] = useState(false)

  const [name, setName] = useState('')
  const [size, setSize] = useState('')

  const [doors, setDoors] = useState<Array<Door>>([])
  const [windows, setWindows] = useState<Array<Device>>([])
  const [lights, setLights] = useState<Array<Device>>([])
  const [ventilators, setVentilators] = useState<Array<Device>>([])

  const [inputDoors, setInputDoors] = useState<Array<Door>>([])
  const [inputWindows, setInputWindows] = useState<Array<Device>>([])
  const [inputLights, setInputLights] = useState<Array<Device>>([])
  const [inputVentilators, setInputVentilators] = useState<Array<Device>>([])

  const { rooms, updateRooms } = useContext(RoomsContext)

  const [newDevices, setNewDevices] = useState<{
    doors: Array<Door>
    windows: Array<Device>
    lights: Array<Device>
    ventilators: Array<Device>
  }>({
    doors: [],
    windows: [],
    lights: [],
    ventilators: []
  })

  const [oldDevices, setOldDevices] = useState<{
    doors: Array<Door>
    windows: Array<Device>
    lights: Array<Device>
    ventilators: Array<Device>
  }>({
    doors: [],
    windows: [],
    lights: [],
    ventilators: []
  })

  const intervalDelay = 10000

  const sortFreeDevices = (x: Device, y: Device) => (y.id as number) - (x.id as number)

  const updateDoorsData = async () => {
    const doors: Array<Door> = await fetchFreeDoors()

    if (doors) setDoors(doors.toSorted(sortFreeDevices))
  }

  const updateDevicesData = async () => {
    const devices: AvailableDevices = await fetchFreeDevices()

    if (devices) {
      if (devices.windows) setWindows(devices.windows.toSorted(sortFreeDevices))
      if (devices.lights) setLights(devices.lights.toSorted(sortFreeDevices))
      if (devices.ventilators) setVentilators(devices.ventilators.toSorted(sortFreeDevices))
    }

    updateDoorsData()
  }

  const getDeviceData = (devices: Record<number, RoomDevice>) => {
    return Object.entries(devices).map(value => {
      return {
        id: Number(value[0]),
        name: value[1].name
      }
    })
  }

  useEffect(() => {
    updateDevicesData().then(() => {
      if (isEdit) {
        const r = props.room as RoomDetailData

        setName(r.name)
        setSize(r.size.toString())

        const oldDoors = Object.entries(r.devices.doors).map(value => {
          return {
            id: Number(value[0]),
            name: value[1].name,
            rooms: [r.id]
          }
        })

        const oldWindows = getDeviceData(r.devices.windows)
        const oldLights = getDeviceData(r.devices.lights)
        const oldVentilators = getDeviceData(r.devices.ventilators)

        setOldDevices({
          doors: oldDoors,
          windows: oldWindows,
          lights: oldLights,
          ventilators: oldVentilators
        })

        setInputDoors(oldDoors)
        setInputWindows(oldWindows)
        setInputLights(oldLights)
        setInputVentilators(oldVentilators)
      }
    })
    // eslint-disable-next-line
  }, [])

  useInterval(() => updateDevicesData(), intervalDelay)

  const handleCreateDevice = (name: string, type: string) => {
    const finalType = type === 'cooling device' ? 'ventilator' : type
    const tempDevices = { ...newDevices }

    switch (finalType) {
      case 'door':
        tempDevices.doors.unshift({
          name: name,
          id: -(tempDevices.doors.length + 1),
          rooms: []
        })
        break
      case 'window':
        tempDevices.windows.unshift({
          name: name,
          id: -(tempDevices.windows.length + 1)
        })
        break
      case 'light':
        tempDevices.lights.unshift({
          name: name,
          id: -(tempDevices.lights.length + 1)
        })
        break
      case 'ventilator':
        tempDevices.ventilators.unshift({
          name: name,
          id: -(tempDevices.ventilators.length + 1)
        })
        break
    }

    setNewDevices(tempDevices)
  }

  const getFinalDevices = () => {
    // Filter old devices
    const getDeviceParameters = (inputValues: Array<Door | Device>, olds: Array<Door | Device>) => {
      return inputValues
        .filter(v => {
          return olds.findIndex(o => o.id === v.id) === -1
        })
        .map(v => ((v.id as number) <= 0 ? { name: v.name } : { id: v.id }))
    }

    return {
      doors: getDeviceParameters(inputDoors, oldDevices.doors),
      windows: getDeviceParameters(inputWindows, oldDevices.windows),
      lights: getDeviceParameters(inputLights, oldDevices.lights),
      ventilators: getDeviceParameters(inputVentilators, oldDevices.ventilators)
    }
  }

  const manageDeviceRequests = (
    type: string,
    data: Array<{ name: string; id?: undefined } | { id: number | undefined; name?: undefined }>
  ) => {
    if (props.room) {
      data.forEach(v => {
        let res

        if (v.id) res = assignDevice(props.room?.id as number, v.id as number, type)
        else res = createDevice(props.room?.id as number, v.name as string, type)
        if ('error' in res) console.error(res)
      })
    }
  }

  const handleSubmitForm = () => {
    const formData = new FormData()
    const devices = getFinalDevices()

    formData.append('name', name)
    formData.append('size', size)

    if (isEdit) {
      // Creamos o asignamos cada dispositivo seleccionado
      manageDeviceRequests('door', devices.doors)
      manageDeviceRequests('window', devices.windows)
      manageDeviceRequests('light', devices.lights)
      manageDeviceRequests('ventilator', devices.ventilators)

      return formData
    }

    formData.append('devices', JSON.stringify(devices))

    return formData
  }

  const renderDeviceOption = (props: any, v: Device) => {
    const { key, ...rest } = props

    return (
      <li key={key} {...rest} className={rest.className + ' flex justify-between'}>
        <div>{v.name}</div>
        <Typography color='var(--mui-palette-text-secondary)'>{(v.id as number) >= 0 ? v.id : 'New'}</Typography>
      </li>
    )
  }

  return (
    <Box display='flex' justifyContent='center' alignItems='center' marginTop={10}>
      <Box
        component='form'
        action={async () => {
          const formData = handleSubmitForm()
          const parseRes = RoomFormSchema.safeParse(Object.fromEntries(formData.entries()))

          // Form validation
          if (!parseRes.success) return console.error(parseRes.error.format())

          let res

          if (isEdit) {
            const roomId = (props.room as RoomDetailData).id.toString()

            res = await editRoom(roomId, formData)
          } else {
            res = await createRoom(formData)
          }

          if ('error' in res) console.error(res.error)
          else {
            await updateRooms()
            if (isEdit) router.back()
            else router.push('/rooms')
          }
        }}
        sx={{
          width: '100%',
          padding: 3,
          borderRadius: 2,
          boxShadow: 3,
          bgcolor: 'background.paper'
        }}
      >
        <Grid container columnSpacing={10} rowSpacing={10} padding={5} paddingX={10}>
          <Grid item md={12}>
            <Divider>Basic Information</Divider>
          </Grid>

          {/* Row 1 */}
          <></>
          <Grid item xs={12} md={6}>
            <TextField
              id='room-name'
              label='Room Name'
              value={name}
              onChange={e => setName(e.target.value)}
              required
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              id='room-size'
              label='Size (m²)'
              value={size}
              onChange={e => setSize(e.target.value)}
              type='number'
              onInput={(e: any) => {
                const input = e.target as HTMLInputElement

                input.value = input.value.replace(/[^0-9]/g, '') // Keep only numbers
              }}
              InputProps={{
                inputProps: {
                  min: 0,
                  inputMode: 'numeric',
                  pattern: '[0-9]*'
                },
                type: 'number'
              }}
              required
              fullWidth
            />
          </Grid>

          <Grid item md={12}>
            <Divider>Room Components</Divider>
          </Grid>

          {/* Row 2 */}
          <Grid item xs={12} md={6}>
            <Autocomplete
              fullWidth
              multiple
              disableCloseOnSelect
              filterSelectedOptions
              id='doors-selection'
              value={inputDoors}
              options={newDevices.doors.concat(doors).concat(oldDevices.doors)}
              getOptionLabel={v => v.name}
              getOptionKey={option => `${option.id}-${option.name}`}
              onChange={(_, v, reason) => {
                if (reason === 'clear' && props.room) v = oldDevices.doors
                setInputDoors(v)
              }}
              renderInput={params => (
                <TextField
                  {...params}
                  label={
                    <div className='flex items-center'>
                      <Icon path={mdiDoorOpen} size={1} className='mr-3' />
                      Doors
                    </div>
                  }
                />
              )}
              renderOption={(props, v) => {
                const connectedRoom = rooms.data.find(o => o.id === v.rooms[0])
                const { key, ...rest } = props

                return (
                  <li key={key} {...rest} className={rest.className + ' flex justify-between'}>
                    <div>{v.name}</div>
                    {connectedRoom && (
                      <Typography color='var(--mui-palette-text-secondary)'>
                        <em>(connects {connectedRoom.name})</em>
                      </Typography>
                    )}
                    <Typography color='var(--mui-palette-text-secondary)'>
                      {(v.id as number) >= 0 ? v.id : 'New'}
                    </Typography>
                  </li>
                )
              }}
              renderTags={(values, getTagProps) => {
                return values.map((v, idx) => {
                  const oldIdx = oldDevices.doors.findIndex(o => o.id === v.id)
                  const isOld = oldIdx !== -1

                  return (
                    <Chip
                      size='small'
                      key={v.id}
                      label={v.name}
                      deleteIcon={
                        isOld ? <Icon path={mdiTrashCan} color='var(--mui-palette-error-main)' size={0.8} /> : undefined
                      }
                      onDelete={async e => {
                        getTagProps({ index: idx }).onDelete(e)

                        if (props.room && isOld) {
                          const tempDevices = { ...oldDevices }

                          tempDevices.doors.splice(oldIdx, 1)
                          setOldDevices(tempDevices)
                          await deleteDoor(v.id as number, props.room.id)
                          updateDoorsData()
                        }
                      }}
                      className='m-0.5'
                    />
                  )
                })
              }}
              isOptionEqualToValue={(o, v) => o.id === v.id}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Autocomplete
              fullWidth
              multiple
              disableCloseOnSelect
              filterSelectedOptions
              id='windows-selection'
              value={inputWindows}
              options={newDevices.windows.concat(windows).concat(oldDevices.windows)}
              getOptionLabel={v => v.name}
              getOptionKey={option => `${option.id}-${option.name}`}
              onChange={(_, v, reason) => {
                if (reason === 'clear' && props.room) v = oldDevices.windows
                setInputWindows(v)
              }}
              renderInput={params => (
                <TextField
                  {...params}
                  label={
                    <div className='flex items-center'>
                      <Icon path={mdiWindowClosedVariant} size={1} className='mr-3' />
                      Windows
                    </div>
                  }
                />
              )}
              renderOption={renderDeviceOption}
              renderTags={(values, getTagProps) => {
                return values.map((v, idx) => {
                  const oldIdx = oldDevices.windows.findIndex(o => o.id === v.id)
                  const isOld = oldIdx !== -1

                  return (
                    <Chip
                      size='small'
                      key={v.id}
                      label={v.name}
                      deleteIcon={
                        isOld ? <Icon path={mdiTrashCan} color='var(--mui-palette-error-main)' size={0.8} /> : undefined
                      }
                      onDelete={e => {
                        getTagProps({ index: idx }).onDelete(e)

                        if (props.room && isOld) {
                          const tempDevices = { ...oldDevices }

                          tempDevices.windows.splice(oldIdx, 1)
                          setOldDevices(tempDevices)
                          deleteDevice(v.id as number, 'window')
                        }
                      }}
                      className='m-0.5'
                    />
                  )
                })
              }}
              isOptionEqualToValue={(o, v) => o.id === v.id}
            />
          </Grid>

          {/* Row 3 */}
          <Grid item xs={12} md={6}>
            <Autocomplete
              fullWidth
              multiple
              disableCloseOnSelect
              filterSelectedOptions
              id='lights-selection'
              value={inputLights}
              options={newDevices.lights.concat(lights).concat(oldDevices.lights)}
              getOptionLabel={v => v.name}
              getOptionKey={option => `${option.id}-${option.name}`}
              onChange={(_, v, reason) => {
                if (reason === 'clear' && props.room) v = oldDevices.lights
                setInputLights(v)
              }}
              renderInput={params => (
                <TextField
                  {...params}
                  label={
                    <div className='flex items-center'>
                      <Icon path={mdiLightbulbOn} size={1} className='mr-3' />
                      Lights
                    </div>
                  }
                />
              )}
              renderOption={renderDeviceOption}
              renderTags={(values, getTagProps) => {
                return values.map((v, idx) => {
                  const oldIdx = oldDevices.lights.findIndex(o => o.id === v.id)
                  const isOld = oldIdx !== -1

                  return (
                    <Chip
                      size='small'
                      key={v.id}
                      label={v.name}
                      deleteIcon={
                        isOld ? <Icon path={mdiTrashCan} color='var(--mui-palette-error-main)' size={0.8} /> : undefined
                      }
                      onDelete={e => {
                        getTagProps({ index: idx }).onDelete(e)

                        if (props.room && isOld) {
                          const tempDevices = { ...oldDevices }

                          tempDevices.lights.splice(oldIdx, 1)
                          setOldDevices(tempDevices)
                          deleteDevice(v.id as number, 'light')
                        }
                      }}
                      className='m-0.5'
                    />
                  )
                })
              }}
              isOptionEqualToValue={(o, v) => o.id === v.id}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Autocomplete
              fullWidth
              multiple
              disableCloseOnSelect
              filterSelectedOptions
              id='ventilators-selection'
              value={inputVentilators}
              options={newDevices.ventilators.concat(ventilators).concat(oldDevices.ventilators)}
              getOptionLabel={v => v.name}
              getOptionKey={option => `${option.id}-${option.name}`}
              onChange={(_, v, reason) => {
                if (reason === 'clear' && props.room) v = oldDevices.ventilators
                setInputVentilators(v)
              }}
              renderInput={params => (
                <TextField
                  {...params}
                  label={
                    <div className='flex items-center'>
                      <Icon path={mdiFan} size={1} className='mr-3' />
                      Cooling Devices
                    </div>
                  }
                />
              )}
              renderOption={renderDeviceOption}
              renderTags={(values, getTagProps) => {
                return values.map((v, idx) => {
                  const oldIdx = oldDevices.ventilators.findIndex(o => o.id === v.id)
                  const isOld = oldIdx !== -1

                  return (
                    <Chip
                      size='small'
                      key={v.id}
                      label={v.name}
                      deleteIcon={
                        isOld ? <Icon path={mdiTrashCan} color='var(--mui-palette-error-main)' size={0.8} /> : undefined
                      }
                      onDelete={e => {
                        getTagProps({ index: idx }).onDelete(e)

                        if (props.room && isOld) {
                          const tempDevices = { ...oldDevices }

                          tempDevices.ventilators.splice(oldIdx, 1)
                          setOldDevices(tempDevices)
                          deleteDevice(v.id as number, 'ventilator')
                        }
                      }}
                      className='m-0.5'
                    />
                  )
                })
              }}
              isOptionEqualToValue={(o, v) => o.id === v.id}
            />
          </Grid>

          {/* Button Row */}
          <Grid item container columnSpacing={10} className='flex justify-between'>
            <Grid item>
              <Grid container>
                <Grid item className='mr-10'>
                  <Button
                    color='secondary'
                    onClick={() => {
                      router.back()
                    }}
                  >
                    Cancel
                  </Button>
                </Grid>
                <Grid item>
                  <Button type='submit' color='primary' variant='contained'>
                    {isEdit ? 'Edit' : 'Create'}
                  </Button>
                </Grid>
              </Grid>
            </Grid>
            {props.room && (
              <Grid item>
                <Button color='error' onClick={() => setOpen(true)}>
                  <Icon path={mdiTrashCan} size={1} className='mr-4' />
                  Delete Room
                </Button>
              </Grid>
            )}
          </Grid>
        </Grid>
      </Box>
      {props.room && (
        <DeleteRoomModal roomId={props.room.id} roomName={props.room.name} open={open} setOpen={setOpen} />
      )}
      <CreateDevicesDial onCreateDevice={handleCreateDevice} />
    </Box>
  )
}

export default RoomForm
