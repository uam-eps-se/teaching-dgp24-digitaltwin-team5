'use client'

import dynamic from 'next/dynamic'

//MUI Imports
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'

import type { ApexOptions } from 'apexcharts'

// Styled Component Imports
const AppReactApexCharts = dynamic(() => import('@/libs/styles/AppReactApexCharts'))

import { mdiAccountGroup, mdiMoleculeCo2, mdiThermometer } from '@mdi/js'
import Icon from '@mdi/react'
import type { BadgeProps } from '@mui/material'
import { Badge, Box, Grid, styled } from '@mui/material'

import type { RoomDetailData, RoomMetric } from '@core/types'
import { useSettings } from '@core/hooks/useSettings'

const RoomStatus = (props: { room: RoomDetailData }) => {
  const room = props.room
  const settings = useSettings()

  const StyledBadge = styled(Badge)<BadgeProps>(({ theme }) => ({
    '& .MuiBadge-badge': {
      right: -6,
      top: -3,
      border: `2px solid ${theme.palette.background.paper}`,
      padding: '0 5px'
    }
  }))

  const getOptions = (chartId: string, unit: string, color?: string): ApexOptions => {
    let zoom: any[] | undefined = undefined

    return {
      chart: {
        id: chartId,
        parentHeightOffset: 0,
        height: '100%',
        toolbar: {
          show: true,
          offsetY: -25
        },
        zoom: {
          enabled: true
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
        }
      },
      tooltip: {
        enabled: true,
        followCursor: false,
        shared: false,
        y: {
          formatter: (val: number) => `${val} ${unit}`
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
      colors: [color ? color : 'var(--mui-palette-primary-main)'],
      stroke: {
        width: 3,
        lineCap: 'butt',
        curve: 'smooth'
      },
      xaxis: {
        type: 'datetime',
        labels: {
          style: { colors: 'var(--mui-palette-text-primary)' },
          datetimeUTC: false
        }
      },
      yaxis: {
        labels: {
          style: { colors: 'var(--mui-palette-text-primary)' },
          offsetX: -16
        },
        tickAmount: 4
      },
      legend: {
        labels: { colors: 'var(--mui-palette-text-main)' }
      }
    }
  }

  const getMetricData = (metrics: RoomMetric, name: string, cutoffTimestamp?: number) => {
    let data = metrics.values
      .map((v, idx) => [new Date(metrics.times[idx] * 1000).getTime(), Number(v)])
      .toSorted((x, y) => x[0] - y[0])

    if (cutoffTimestamp && data.length) {
      const lastTimestamp = data.slice(-1)[0][0]
      const timeCutoff = lastTimestamp - cutoffTimestamp

      data = data.filter(metric => metric[0] >= timeCutoff)
    }

    return {
      name: name,
      data: data
    }
  }

  const cutoff = 3600000

  const peopleData = getMetricData(room.metrics.people, 'People', cutoff)
  const tempData = getMetricData(room.metrics.temperature, 'Temperature', cutoff)
  const co2Data = getMetricData(room.metrics.co2, 'CO₂', cutoff)

  return (
    <div>
      <Grid container rowSpacing={4} columnSpacing={{ xs: 1, sm: 2, md: 4 }}>
        <Grid item xs={12} md={12}>
          <Card>
            <CardContent>
              <Box display='flex' alignItems='center'>
                <StyledBadge
                  badgeContent={peopleData.data.length && peopleData.data.slice(-1)[0][1]}
                  color='primary'
                  className={peopleData.data.length ? 'mr-7' : 'mr-5'}
                  max={99999}
                  showZero
                >
                  <Icon path={mdiAccountGroup} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Number of People</Typography>
              </Box>
              {peopleData.data.length ? (
                <AppReactApexCharts
                  type='line'
                  height='140%'
                  width='100%'
                  options={getOptions('people', '')}
                  series={[peopleData]}
                />
              ) : (
                <Typography variant='h5' className='mt-4'>
                  People data unavailable
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display='flex' alignItems='center'>
                <StyledBadge
                  badgeContent={tempData.data.length && tempData.data.slice(-1)[0][1]}
                  color='warning'
                  className={tempData.data.length ? 'mr-7' : 'mr-5'}
                  max={99999}
                  showZero
                >
                  <Icon path={mdiThermometer} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Temperature (ºC)</Typography>
              </Box>
              {tempData.data.length ? (
                <AppReactApexCharts
                  type='line'
                  height='140%'
                  width='100%'
                  options={getOptions('temperature', 'ºC', 'var(--mui-palette-warning-main)')}
                  series={[tempData]}
                />
              ) : (
                <Typography variant='h5' className='mt-4'>
                  Temperature data unavailable
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display='flex' alignItems='center'>
                <StyledBadge
                  badgeContent={co2Data.data.length && co2Data.data.slice(-1)[0][1]}
                  color='success'
                  className={co2Data.data.length ? 'mr-7' : 'mr-5'}
                  max={99999}
                  showZero
                >
                  <Icon path={mdiMoleculeCo2} size={1} />
                </StyledBadge>
                <Typography variant='h4'>CO₂ (ppm)</Typography>
              </Box>
              {co2Data.data.length ? (
                <AppReactApexCharts
                  type='line'
                  height='140%'
                  width='100%'
                  options={getOptions('co2', 'ppm', 'var(--mui-palette-success-main)')}
                  series={[co2Data]}
                />
              ) : (
                <Typography variant='h5' className='mt-4'>
                  CO₂ data unavailable
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  )
}

export default RoomStatus
