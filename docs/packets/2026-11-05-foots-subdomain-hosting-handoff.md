# Handoff — publish Footmen Frenzy wiki at foots.northstarenergy.ca

**Prepared:** 2026-11-05  
**State:** Not deployed. No DNS, Cloudflare, NorthStar runtime, or canonical handoff changes were made.  
**Audience:** Next authorized coordinator/agent

## Request and decision

- User wants the recovered Footmen Frenzy wiki hosted at `https://foots.northstarenergy.ca`.
- User explicitly selected **public, no login**.
- Publish only the curated static Footmen Frenzy wiki. Do not expose NorthStar operator/worker data, the NorthStar project tree, or its backend.

## Current source and build

- Wiki source: `C:\Users\User\Documents\Footmen-Frenzy-Recovery-2026-11-05\wiki`
- Build command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\User\Documents\Footmen-Frenzy-Recovery-2026-11-05\wiki\build-wiki.ps1"`
- Latest build succeeded on 2026-11-05. `wiki/BUILD-INFO.txt` reports:
  - 91 799W heroes; 81 portraits mapped
  - 278 799W ability icons
  - 219/219 799X item-model icons, with provenance
  - 16 spell sections; 101 values resolved from cited 799W sources; 36 unsupported/ambiguous cells shown as em dashes
  - No literal `default` gameplay placeholders in spell tables
- 799W, 799X, and Solo data remain separate. No verified 799X/Solo hero icon set is integrated.
- Browser verification was performed at `http://127.0.0.1:8765/wiki/`: hero details, spell notes, item details and images loaded; no console errors. The page was left on `#spells`.
- Relevant files include `build-wiki.ps1`, `wiki-build-support.ps1`, `wiki.js`, `index.html`, `icons.css`, `README.md`, `wiki-data.js`, `BUILD-INFO.txt`, `source-docs/`, `source-data/`, and the edition-scoped `assets/icons/` directories.

## Public-release review required

Do not publish by copying the whole recovery/project directory. Make a dedicated static release containing only the needed wiki runtime, generated data, approved source documents, and referenced images.

- Current wiki source links include paths outside `wiki/`, including `../extracted/FF-Wiki-Files/...` and `../files/Documents/...`; hero-detail links also point outside the wiki folder. Bundle approved referenced material into the release or revise/remove links so the hosted UI has no broken or accidental parent-directory links.
- `wiki/README.md` warns that captured match results contain player handles and says identities/statistics need review before publication. Review the FFA event/match data before public release; redact or omit any records that are not cleared for publication.
- Inspect the final deploy tree for credentials, personal data, build scripts, source archives not intended for public release, and unrelated files. Everything in a public static deployment is public by URL, even if not linked from the UI.

## NorthStar / hosting constraints

- The current session directory was `C:\Users\User\AppData\Local\Temp\opencode\NorthStar-Switching-Simulator\northstar-app`. It has no `.git`; `git` was unavailable in this shell.
- The canonical project path stated in its `AGENTS.md`, `C:\Users\Ryan1\Documents\Work Projects\control-room-dashboard`, was not present in this environment. The canonical `.cursor` coordinator rule and agent file were also unavailable.
- `docs/CHANGE-COORDINATION.md` was read. This file is a **private, uniquely named packet in the temporary copy**, not the canonical/shared handoff. No queue, lock, shared handoff, or runtime file was changed. The next agent must use the canonical checkout and follow its coordination procedure before integration: inspect queue/inbox/current handoff/worktrees; create a unique request packet; acquire the integration lock atomically; only the lock owner updates shared queue/handoff/runtime; release only its own lock.
- `DEPLOY-RUNBOOK.md` says the current `checkin.` and `ops.` hostnames route through a remotely managed Cloudflare Tunnel; DNS is auto-created by the Cloudflare Zero Trust Public Hostname configuration. No Cloudflare account/session was available here.
- `checkin.northstarenergy.ca` is the worker-only public surface and `ops.northstarenergy.ca` is Access-protected. Do not add `foots.` to the check-in allowlist, weaken operator gating, widen the web root, or point the new host at `localhost:4180` without a separately reviewed design.
- Preferred isolation: a dedicated static Cloudflare Pages project/custom domain for the curated export, or a separately isolated static origin behind its own tunnel route. Do not serve the NorthStar repository root or reuse the operator backend as a generic file server.

## Next actions

1. Open the canonical NorthStar checkout (or establish its actual mounted path) and inspect its coordination queue, lock, active worktrees, and current handoff. Do not start a competing coordinator if a lock is held.
2. Create/coordinate a uniquely named request for the new public hostname. Confirm the deployment mechanism with the domain owner; the public/no-login policy is already confirmed by the user.
3. Prepare a self-contained, allowlisted static export from the wiki source above. Review/redact match handles and resolve external source links before deployment.
4. Configure `foots.northstarenergy.ca` to the isolated static host in Cloudflare. Do not change `checkin.`/`ops.` routing or expose port 4180 as the wiki origin.
5. Verify over the public HTTPS hostname: representative hero/spell/item pages, all assets and approved source links return successfully; no console errors or `default` placeholders; no unapproved files or personal/operational data are exposed.
6. Record deployment evidence separately from source integration/live verification, update the canonical handoff only as lock owner, and release only the owned lock.

## Credentials and actions

- No Cloudflare credentials, tokens, passwords, or private keys are included in this packet.
- No public URL was created or verified. The site is not yet live at `foots.northstarenergy.ca`.
