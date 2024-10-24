'use client'

// Component Imports
import StormLogo from '@core/svg/Logo'

// // Config Imports
import { useSettings } from '@core/hooks/useSettings'

const Logo = () => {
  const { settings } = useSettings();

  return (
    <div className='flex items-center min-bs-[24px]'>
      <StormLogo className='text-[22px] text-primary' mode={settings.mode} />
    </div>
  )
}

export default Logo
