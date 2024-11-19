'use client'

import Link from 'next/link'

import type { AlertProps } from '@mui/material'
import { Alert as AlertComponent, AlertTitle, Typography } from '@mui/material'

import type { Alert } from '@core/types'
import { AlertType } from '@core/types'

const StormAlert = (
  props: AlertProps & {
    alert: Alert
    showTime?: boolean
    onDeleteAlert: () => void | undefined
  }
) => {
  const { alert, showTime, onDeleteAlert, ...rest } = props

  const getAlertSeverity = (type: AlertType) => {
    switch (type) {
      case AlertType.WARNING:
        return 'warning'
      case AlertType.DANGER:
        return 'error'
      default:
        return 'info'
    }
  }

  return (
    <AlertComponent
      {...rest}
      severity={getAlertSeverity(alert.type)}
      onClose={() => onDeleteAlert && onDeleteAlert()}
      className='max-w-full w-full break-words'
    >
      {rest.title !== undefined && (
        <AlertTitle>
          <Link href={`/rooms/${alert.roomId}`}>{rest.title}</Link>
        </AlertTitle>
      )}
      <div className='flex flex-col gap-2'>
        {alert.content}
        {(showTime === undefined || showTime) && (
          <Typography fontSize={'0.8rem'} color='inherit'>
            {new Date(alert.time).toLocaleString(undefined, {
              dateStyle: 'short',
              timeStyle: 'short'
            })}
          </Typography>
        )}
      </div>
    </AlertComponent>
  )
}

export default StormAlert
