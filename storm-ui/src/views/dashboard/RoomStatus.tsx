'use client'

import dynamic from 'next/dynamic'

import { useSettings } from '@core/hooks/useSettings'

//MUI Imports
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'

import type { ApexOptions } from 'apexcharts'
import { RoomDetailData, RoomMetric } from '@core/types'

// Styled Component Imports
const AppReactApexCharts = dynamic(() => import('@/libs/styles/AppReactApexCharts'))

import { mdiAccountGroup, mdiMoleculeCo2, mdiThermometer } from '@mdi/js';
import Icon from '@mdi/react';
import { Badge, BadgeProps, Box, Grid, styled } from '@mui/material'

const RoomStatus = (props: { room: RoomDetailData }) => {
  const room = props.room;
  const settings = useSettings();

  const StyledBadge = styled(Badge)<BadgeProps>(({ theme }) => ({
    '& .MuiBadge-badge': {
      right: -6,
      top: -3,
      border: `2px solid ${theme.palette.background.paper}`,
      padding: '0 5px',
    },
  }));

  const getOptions = (chartId: string, unit: string): ApexOptions => {
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
          enabled: true,
        },
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
      colors: ['var(--mui-palette-primary-main)'],
      stroke: {
        width: 3,
        lineCap: 'butt',
        curve: 'smooth'
      },
      xaxis: {
        type: 'datetime',
        labels: {
          style: { colors: 'var(--mui-palette-text-primary)' },
          datetimeUTC: false,
        },
      },
      yaxis: {
        labels: {
          style: { colors: 'var(--mui-palette-text-primary)' },
          offsetX: -16
        },
        tickAmount: 4,
      },
      legend: {
        labels: { colors: 'var(--mui-palette-text-main)' }
      }
    }
  }

  const getMetricData = (metrics: RoomMetric, name: string, cutoffTimestamp?: number) => {
    var data = metrics.values.map((v, idx) =>
      [new Date(metrics.times[idx] * 1000).getTime(), Number(v)]
    ).toSorted((x, y) => x[0] - y[0]);

    if (cutoffTimestamp) {
      const timeCutoff = Date.now() - cutoffTimestamp;
      data = data.filter((metric) =>
        metric[0] >= timeCutoff
      )
    }

    return {
      name: name,
      data: data
    }
  }

  const cutoff = 3600000;

  const peopleData = getMetricData(room.metrics.people, 'People', cutoff);
  const tempData = getMetricData(room.metrics.temperature, 'Temperature', cutoff);
  const co2Data = getMetricData(room.metrics.co2, 'CO₂', cutoff);

  return (
    <div>
      <Grid container rowSpacing={4} columnSpacing={{ xs: 1, sm: 2, md: 4 }}>
        <Grid item xs={12} md={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <StyledBadge
                  badgeContent={peopleData.data.slice(-1)[0][1] || 0}
                  color='primary'
                  className='mr-7'
                  max={99999}
                >
                  <Icon path={mdiAccountGroup} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Number of People</Typography>
              </Box>
              {
                peopleData.data.length ?
                  <AppReactApexCharts
                    type='line'
                    height='140%'
                    width='100%'
                    options={getOptions('people', '')}
                    series={[peopleData]}
                  />
                  :
                  <Typography variant='h4' className='mt-4'>People data unavailable</Typography>
              }
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <StyledBadge
                  badgeContent={tempData.data.slice(-1)[0][1] || 0}
                  color='primary'
                  className='mr-7'
                  max={99999}
                >
                  <Icon path={mdiThermometer} size={1} />
                </StyledBadge>
                <Typography variant='h4'>Temperature (ºC)</Typography>
              </Box>
              {
                tempData.data.length ?
                  <AppReactApexCharts
                    type='line'
                    height='140%'
                    width='100%'
                    options={getOptions('temperature', 'ºC')}
                    series={[tempData]}
                  />
                  :
                  <Typography variant='h4' className='mt-4'>Temperature data unavailable</Typography>
              }
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <StyledBadge
                  badgeContent={co2Data.data.slice(-1)[0][1] || 0}
                  color='primary'
                  className='mr-7'
                  max={99999}
                >
                  <Icon path={mdiMoleculeCo2} size={1} />
                </StyledBadge>
                <Typography variant='h4'>CO₂ (ppm)</Typography>
              </Box>
              {
                co2Data.data.length ?
                  <AppReactApexCharts
                    type='line'
                    height='140%'
                    width='100%'
                    options={getOptions('co2', 'ppm')}
                    series={[co2Data]}
                  />
                  :
                  <Typography variant='h5' className='mt-4'>CO₂ data unavailable</Typography>
              }
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  )
}

export default RoomStatus
