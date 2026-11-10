# Footmen Frenzy public wiki

Live: https://foots.northstarenergy.ca/ — public, no login. Cloudflare Pages project: `footmen-frenzy-wiki`.

The self-contained, curated site lives in `wiki/site`. It was imported from the recovered November 5 field guide. The original recovery archive is preserved; future builds depend only on this repository.

Run `node wiki/build.mjs` from the repository root. This validates the public file allowlist, embedded links, referenced images, edition data, and privacy markers, then copies the reviewed tree into ignored `build/wiki`. Its SHA256 inventory is written to `build/wiki-manifest.json`. Run `node wiki/preview.mjs` for a loopback-only preview on port 8766.

Deploy **only `build/wiki`** to a dedicated Cloudflare Pages project, then bind `foots.northstarenergy.ca`. Do not upload the repository, recovery archive, build scripts, or manifest. No NorthStar service, tunnel, operator access policy, or backend route is required or modified by this static package.

The public dataset excludes raw match records, player identifiers, replay files, and recovered HTML pages with dependencies outside the release. Anonymous purchase aggregates retain their original unconfirmed-build labels. The 799W, 799X, and Solo datasets remain separate historical snapshots; this is not current-build gameplay verification.

Images retain their recovered edition/provenance fields. No ownership or new license over Warcraft III or inherited third-party assets is asserted. Binary images use repository Git LFS rules.
