#!/usr/bin/sh

if ! git diff --cached --quiet --exit-code storm-ui; then
    cd storm-ui
    pnpm format
    pnpm lint:fix || exit 0
fi
