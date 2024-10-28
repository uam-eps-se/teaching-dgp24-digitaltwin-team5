// React Imports
import type { SVGAttributes } from 'react'
import Image from 'next/image';

const StormLogo = (props: SVGAttributes<SVGElement>) => {
  return (
    <div>
      <Image
        priority
        width={0}
        height={0}
        sizes="100vw"
        style={{ width: '100%', height: 'auto' }}
        src={props.mode === 'light' ? '/storm-logo-h.png' : '/storm-logo-h-dark.png'}
        alt="STORM Logo"
      />
    </div>
  )
};

export default StormLogo
