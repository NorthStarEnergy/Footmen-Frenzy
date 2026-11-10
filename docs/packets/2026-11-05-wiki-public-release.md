# Footmen Frenzy wiki public release

## Source and scope

Located the requested hosting handoff in the temporary OpenCode NorthStar checkout and preserved it alongside this report. Imported the reviewed wiki into `wiki/site`; the original recovery archive remains untouched. Rebuilds use repository-relative paths and Node's standard library.

Dedicated Cloudflare Pages project created: `footmen-frenzy-wiki`, in the existing account managing `northstarenergy.ca`. Intended custom domain: `foots.northstarenergy.ca`. No NorthStar runtime, check-in/operator route, tunnel, Access policy, queue, lock, or shared handoff was modified. Read the available NorthStar coordination policy: integration locking applies to changes to its shared checkout; this release is isolated in the Footmen repository and a separate Pages project.

## Public content review

- Retained separate 799W, 799X, and Solo hero datasets, 16 spell sections, 219 modeled items, units, shops, and mechanics guides.
- Retained anonymous aggregate item/hero purchase observations with original unconfirmed-build caveats; no raw player identities or match records were included.
- Removed match/replay section and metadata, parent-directory links, and recovered hero-page links whose dependencies were outside the release.
- Copied only referenced images and the eight cited source files plus ten guide documents (overlaps deduplicated). No recovery folders or NorthStar files enter the deployment tree.
- Preserved image provenance and unofficial/archival status. Binary images are covered by Git LFS attributes.
- Added keyboard activation for hero/item rows, safe hash navigation, edition-specific roster headings, and rounded display of modeled floating-point values.

## Verification

`node wiki/build.mjs` passed: 536 allowlisted files, 535 local references resolved, three hero editions, 16 spell sections, 219 modeled items. JavaScript syntax check passed. All 536 files returned HTTP 200 from the loopback preview.

Chrome interaction checks passed for navigation, Mountain King search and keyboard-opened spell details, Solo roster selection, Claws item filtering/details, Thunder Clap spell filtering, and Solo Footman unit filtering. A navigation error found during initial QA was corrected; no further console errors were observed after rebuilding and reloading. Desktop layout visually inspected. Mobile layout and public HTTPS verification remain pending.

No maps changed; no live Warcraft gameplay testing was performed.

## Deployment state

**Deployed and verified November 5, 2026 (America/Toronto).** After the user enabled Chrome extension file access, Cloudflare accepted all 536 files and reported successful deployment. Public URL: https://foots.northstarenergy.ca/ . Alternate Pages URL: https://footmen-frenzy-wiki.pages.dev/ .

Cloudflare created the proxied CNAME `foots` → `footmen-frenzy-wiki.pages.dev`, TTL Auto. Custom-domain status is **Active**, **SSL enabled**. An initial 522 during provisioning cleared without changes to other DNS records or NorthStar services.

All 536 deployed files returned HTTP 200 and matched their release SHA256 on both hostnames. On the custom hostname, Chrome verified Mountain King search and keyboard-opened details, Thunder Clap spell search, and Claws of Ultimate Devastation item details, with no console errors. No login is required. Live screenshot: ignored `build/wiki-live.png`. Full public verification evidence: `build/wiki-public-check.json` and `build/wiki-custom-domain-check.json`.

Upload artifact: `build/footmen-frenzy-wiki-2026-11-05.zip`, containing only `build/wiki`. SHA256 inventory: `build/wiki-manifest.json`. These are ignored build outputs, not repository source.

Release ZIP SHA256: `3C9C72772DDBBDA5AD87493F1A6A0808C478275C89C5D7314125F67FE9D73D98`.

For subsequent releases, use the existing `footmen-frenzy-wiki` Pages project's Create deployment action. Do not create a duplicate project. Rebuild and validate from `wiki/site`, upload only the curated build, and verify the production hostname against the new manifest.
