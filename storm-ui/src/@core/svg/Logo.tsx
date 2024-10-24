// React Imports
import type { SVGAttributes } from 'react'
import Image from 'next/image';
import stormLogoLight from "/public/storm-logo-h.svg";
import stormLogoDark from "/public/storm-logo-h-dark.svg";

const StormLogo = (props: SVGAttributes<SVGElement>) => {
  return (
    <div>
      <Image
        priority
        width={0}
        height={0}
        style={{ width: '100%', height: 'auto' }}
        src={props.mode === 'light' ? stormLogoLight : stormLogoDark}
        alt="STORM Logo"
      />
    </div>
  )
};

export default StormLogo
