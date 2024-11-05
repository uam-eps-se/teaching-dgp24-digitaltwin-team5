#!/usr/bin/sh

cd storm-ui
pnpm format
pnpm lint:fix || exit 0
