'use client'

import dynamic from 'next/dynamic'

//MUI Imports
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'

import type { ApexOptions } from 'apexcharts'

// Styled Component Imports
const AppReactApexCharts = dynamic(() => import('@/libs/styles/AppReactApexCharts'))

import { mdiDoorOpen, mdiFan, mdiLightbulbOn, mdiWindowClosedVariant } from '@mdi/js'
import Icon from '@mdi/react'
import type { BadgeProps } from '@mui/material'
import { Badge, Box, Grid, styled } from '@mui/material'

import type { RoomDetailData, RoomDevice } from '@core/types'
import { useSettings } from '@core/hooks/useSettings'

const RoomStructure = (props: { room: RoomDetailData }) => {
  const room = props.room
  const settings = useSettings()

  const StyledBadge = styled(Badge)<BadgeProps>(({ theme }) => ({
    '& .MuiBadge-badge': {
      right: -3,
      border: `2px solid ${theme.palette.background.paper}`,
      padding: '0 4px'
    }
  }))

  const getOptions = (chartId: string, trueLabel: string = 'Open', falseLabel: string = 'Closed'): ApexOptions => {
    let zoom: any[] | undefined = undefined

    return {
      chart: {
        id: chartId,
        parentHeightOffset: 0,
        toolbar: {
          show: true,
          offsetY: -25
        },
        animations: {
          enabled: true,
          easing: 'easeinout',
          dynamicAnimation: {
            speed: 500
          }
        },
        events: {
          beforeResetZoom: chart => {
            zoom = undefined
            chart.w.globals.lastXAxis.min = undefined
            chart.w.globals.lastXAxis.max = undefined

            return true
          },
          zoomed: (_, value) => {
            zoom = [value.xaxis.min, value.xaxis.max]
          },
          updated: (chart, options) => {
            // Make sure its a series update and not config
            if (zoom && options.config.xaxis.min !== zoom[0] && options.config.xaxis.max !== zoom[1]) {
              chart.updateOptions({
                chart: { animations: { dynamicAnimations: { enabled: false } } }
              })
              chart.zoomX(zoom[0], zoom[1])
              chart.updateOptions({
                chart: { animations: { dynamicAnimations: { enabled: true } } }
              })
            }
          }
        },
        zoom: {
          enabled: true,
          type: 'x'
        }
      },
      tooltip: {
        enabled: true,
        followCursor: true,
        shared: false,
        y: {
          formatter: (val: number) => (val === 1 ? trueLabel : falseLabel)
        },
        theme: settings.settings.mode
      },
      grid: {
        strokeDashArray: 6,
        borderColor: 'var(--mui-palette-divider)',
        xaxis: {
          lines: { show: true }
        },
        yaxis: {
          lines: { show: true }
        },
        padding: {
          top: -10,
          left: -7,
          right: 5,
          bottom: 5
        }
      },
      stroke: {
        width: 3,
        lineCap: 'butt',
        curve: 'stepline'
      },
      xaxis: {
        type: 'datetime',
        labels: {
          style: { colors: 'var(--mui-palette-text-primary)' },
          datetimeUTC: false
        }
      },
      yaxis: {
        labels: { show: false },
        tickAmount: 2,
        min: -0.01,
        max: 1.01
      },
      legend: {
        showForSingleSeries: true,
        labels: { colors: 'var(--mui-palette-text-main)' }
      }
    }
  }

  const getDeviceData = (records: Record<number, RoomDevice>, cutoffTimestamp?: number) => {
    return Object.entries(records).map(deviceData => {
      const roomDevice = deviceData[1]
      let data = roomDevice.values.map((v, idx) => [new Date(roomDevice.times[idx] * 1000).getTime(), Number(v)])

      if (cutoffTimestamp && data.length) {
        const lastTimestamp = data[0][0]
        const timeCutoff = lastTimestamp - cutoffTimestamp

        data = data.filter(metric => metric[0] >= timeCutoff)
      }

      return {
        name: roomDevice.name,
        data: data.toReversed()
      }
    })
  }

  // const cutoff = 3600000

  const doorData = getDeviceData(room.devices.doors)
  const windowData = getDeviceData(room.devices.windows)
  const lightData = getDeviceData(room.devices.lights)
  const coolingData = getDeviceData(room.devices.ventilators)

  return (
    <div>
      <Grid container rowSpacing={4} columnSpacing={{ xs: 1, sm: 2, md: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display='flex' alignItems='center'>
                <StyledBadge badgeContent={doorData.length} color='secondary' className='mr-5'>
                  <Icon path={mdiDoorOpen} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Doors</Typography>
              </Box>
              {doorData.length ? (
                <AppReactApexCharts
                  type='line'
                  height='140%'
                  width='100%'
                  options={getOptions('doors')}
                  series={doorData}
                />
              ) : (
                <Typography variant='h5' className='mt-4'>
                  No doors available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display='flex' alignItems='center'>
                <StyledBadge badgeContent={windowData.length} color='secondary' className='mr-5'>
                  <Icon path={mdiWindowClosedVariant} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Windows</Typography>
              </Box>
              {windowData.length ? (
                <AppReactApexCharts
                  type='line'
                  height='140%'
                  width='100%'
                  options={getOptions('windows')}
                  series={windowData}
                />
              ) : (
                <Typography variant='h5' className='mt-4'>
                  No windows available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display='flex' alignItems='center'>
                <StyledBadge badgeContent={lightData.length} color='secondary' className='mr-5'>
                  <Icon path={mdiLightbulbOn} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Lights</Typography>
              </Box>
              {lightData.length ? (
                <AppReactApexCharts
                  type='line'
                  height='140%'
                  width='100%'
                  options={getOptions('lights', 'On', 'Off')}
                  series={lightData}
                />
              ) : (
                <Typography variant='h5' className='mt-4'>
                  No lights available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display='flex' alignItems='center'>
                <StyledBadge badgeContent={coolingData.length} color='secondary' className='mr-5'>
                  <Icon path={mdiFan} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Cooling Devices</Typography>
              </Box>
              {coolingData.length ? (
                <AppReactApexCharts
                  type='line'
                  height='140%'
                  width='100%'
                  options={getOptions('cooling', 'On', 'Off')}
                  series={coolingData}
                />
              ) : (
                <Typography variant='h5' className='mt-4'>
                  No cooling devices available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  )
}

export default RoomStructure
