'use client'

// Next Imports
import Link from 'next/link'

// Third-party Imports
import classnames from 'classnames'

// Util Imports
import { verticalLayoutClasses } from '@layouts/utils/layoutClasses'

const FooterContent = () => {
  return (
    <div
      className={classnames(verticalLayoutClasses.footerContent, 'flex items-center justify-between flex-wrap gap-4')}
    >
      <p>
        <span>{`© ${new Date().getFullYear()} | Made `}</span>
        <span>{` by `}</span>
        <Link href='https://github.com/TomasDanielExpositoTorre' target='_blank' className='text-primary'>
          Tomás Expósito
        </Link>
        <span> & </span>
        <Link href='https://github.com/Acervans' target='_blank' className='text-primary'>
          Javier Wang
        </Link>
      </p>
    </div>
  )
}

export default FooterContent
