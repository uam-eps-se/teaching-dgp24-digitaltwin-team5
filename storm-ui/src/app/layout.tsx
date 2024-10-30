// Third-party Imports
import 'react-perfect-scrollbar/dist/css/styles.css'

// Type Imports
import type { Metadata } from 'next';

import type { ChildrenType } from '@core/types'

// Style Imports
import '@/app/globals.css'

// Generated Icon CSS Imports
import '@assets/iconify-icons/generated-icons.css'

export const metadata: Metadata = {
  title: {
    template: '%s | STORM',
    default: 'STORM: Smart Tracking & Optimization for Room Monitoring'
  },
  description:
    'User Interface for STORM: Smart Tracking & Optimization for Room Monitoring'
}

const RootLayout = ({ children }: ChildrenType) => {
  // Vars
  const direction = 'ltr'

  return (
    <html id='__next' dir={direction}>
      <body className='flex is-full min-bs-full flex-auto flex-col'>{children}</body>
    </html>
  )
}

export default RootLayout
