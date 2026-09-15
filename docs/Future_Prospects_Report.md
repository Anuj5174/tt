# TIGERTRACE — FUTURE PROSPECTS

### Camera-trap intelligence for Pench Tiger Reserve

Team: [add your names here] · September 2026

---

## 1. Where we stand today

Rangers collect thousands of camera-trap photos every month. Most are empty frames, and telling one tiger from another by eye takes days. TigerTrace does that work on a single laptop, with no internet, using real data from Pench — 62 identified tigers across 295 camera locations.

> **[FIGURE 1 HERE]** — *From memory card to insight (prompt at the back of this document)*

What is already built and working:

| Capability | In plain words |
|---|---|
| Empty-frame filter | Removes 60–80% junk photos while keeping over 95% of animal photos |
| Privacy protection | Photos of people are blurred automatically |
| Species check | Separates tigers from leopards, deer, bear and cattle — 100% on our test set |
| Individual ID | Reads stripe patterns like a fingerprint; correct tiger found 99 times out of 100 |
| Human review queue | Unsure matches go to a ranger for a one-click decision |
| Territory maps | Home range, movement path and overlap for each tiger |
| Early warnings | Long absence, sudden territory shift, tiger near a village, first visit to a new area |
| Patrol planner | Ranks camera points by patrol urgency, with the reasons spelled out |
| Offline assistant | Questions answered in English, Hindi or Marathi — no internet, no external AI |
| Official exports | One-click report files for the forest department |

---

## 2. Next: a hub in every range office, the app in every ranger's pocket

Today the system lives on one machine. The next version installs a small hub computer at each range office. A ranger walks in, inserts the SD card, and TigerTrace processes it on the spot.

Around the hub, a mobile app for rangers works in two modes:

- **Offline mode (default).** The hub creates its own local network, like a router without internet. Ranger phones connect free of cost and get messaging with the control room, patrol tasks, tiger records and text alerts. We keep this mode to text on purpose — over short-range radio, a single photo can take minutes to send.
- **Online mode (only if the department permits internet).** The same app unlocks full sync — photos and video straight from the field, and direct upload from the phone camera, with no SD card needed at all.

The app is built offline-first: it queues whatever it cannot send and syncs the moment a connection appears. Nothing is lost in dead-signal zones, and no data ever leaves the forest unless the department chooses.

> **[FIGURE 2 HERE]** — *Hub at the range office, rangers connected on or off the internet*

---

## 3. Next: warning the people who live beside tigers

The system already raises an internal alert when a tiger is photographed near a village boundary. The next step delivers that warning to the people it matters to, within minutes:

1. A camera confirms a tiger at a village-adjacent point.
2. The system checks registered villages within a safety radius.
3. Registered residents receive an SMS or missed-call alert in Marathi or Hindi: *"Tiger active near the forest edge tonight — please avoid the area after dark."*

Two deliberate choices keep this safe. The alert never carries exact tiger coordinates, so it cannot be exploited by poachers. And the villager registry is managed by the forest department, not by us. Later versions can add village sirens, or plug into the department's existing WhatsApp and call channels, so families without smartphones are also covered.

> **[FIGURE 3 HERE]** — *Village warning in three steps*

---

## 4. Next: guarding the data like a bank vault

A tiger's location is among the most sensitive things a forest department owns — one leaked photograph can put a price on an animal's head. Our security plan works in layers, like a vault, so no single failure exposes anything:

1. **Locked away.** Hub machines sit in a secure room, and their storage is encrypted. A stolen laptop is an empty box.
2. **Encoded in transit.** Whenever data moves between hub, phones or server, it is scrambled so an intercepted message reads as noise.
3. **No open doors.** With internet permitted, the system is reachable only through the department's own private channel, never a public address. Offline, there is no outside connection at all.
4. **Named keys.** Every user logs in personally and sees only what their role allows. No shared passwords — every action has an owner.
5. **A ledger that cannot be edited.** Every login, export and change is recorded automatically. If someone tries to pull tiger data out, the trail shows who, what and when.
6. **Lost phone, dead data.** A lost ranger phone can be wiped remotely, and it keeps no sensitive copy of its own.
7. **Safe copies.** Encrypted backups are taken daily, and recovery is tested, not assumed.

Every layer uses standard, proven tools. Nothing exotic, nothing that needs a security team to maintain.

> **[FIGURE 4 HERE]** — *Layers of protection around tiger data*

---

## 5. The road ahead

TigerTrace already gives rangers their weeks back. The road ahead turns a single-laptop tool into a connected shield around the reserve — one that watches the forest, guides the patrol, warns the village and guards its own secrets.

---
---

## FIGURE GENERATION PROMPTS — *remove this page before printing*

All four figures share one style so the document looks uniform. Paste any single prompt below into your image generator.

**Shared style (already baked into each prompt):** flat vector infographic, white background, forest green + warm amber, rounded shapes, thick clean outlines, no gradients, simple line icons, generous white space.

**FIGURE 1 — From memory card to insight**

> Flat vector infographic, white background, horizontal 16:9, six rounded rectangles connected left to right by bold arrows, deep forest green and warm amber palette, thick outlines, simple line icons, short text labels. Panel 1: SD memory card icon, label "SD CARD". Panel 2: laptop with trash bin and grey empty photo frames, label "REMOVE EMPTY PHOTOS". Panel 3: tiger face icon with green check mark and deer icon with red cross, label "IS IT A TIGER?". Panel 4: tiger stripe pattern under a magnifying glass, label "MATCH STRIPES". Panel 5: ID badge card with tiger photo, label "WHICH TIGER". Panel 6: map pin and bell icon over a simple map, label "MAPS + ALERTS". Minimal corporate infographic style, no gradients, generous white space.

**FIGURE 2 — Hub at the range office, rangers connected**

> Flat vector infographic, white background, horizontal 16:9, split into two halves. Center: a small desktop computer with an SD card slot, labeled "RANGE OFFICE HUB", sitting on the dividing line so it belongs to both halves. Left half tinted pale green, heading "OFFLINE MODE": the hub emits local wifi arcs to three ranger smartphones, each phone showing a chat bubble icon; strip at the bottom reads "CHAT + ALERTS ONLY". Right half tinted pale amber, heading "ONLINE MODE (IF PERMITTED)": hub and phones connect upward to one cloud icon, phones show photo and video icons; strip at the bottom reads "PHOTOS + VIDEO + DIRECT UPLOAD". Forest green and amber palette, rounded shapes, thick outlines, simple line icons, no gradients.

**FIGURE 3 — Village warning in three steps**

> Flat vector infographic, white background, horizontal 16:9, three scenes connected by bold arrows, forest green and amber palette, simple line icons, small numbered circles 1 2 3. Scene 1: camera trap mounted on a tree photographing a walking tiger, label "CAMERA SEES A TIGER". Scene 2: laptop screen showing a simple map with a tiger paw print inside a dashed circle around small village huts, label "TOO CLOSE TO A VILLAGE?". Scene 3: an Indian villager holding a smartphone showing an SMS message bubble, next to a siren loudspeaker on a pole, label "SMS WARNING IN HINDI / MARATHI". Minimal, rounded, flat style, no gradients.

**FIGURE 4 — Layers of protection around tiger data**

> Flat vector infographic, white background, near-square layout, concentric rounded rings like an onion around a center icon. Center: a small round vault door with a tiger stripe pattern inside, label "TIGER DATA". Innermost ring: padlock icon, label "ENCRYPTED". Next ring: shield icon, label "PRIVATE NETWORK". Next ring: ID badge icon, label "PERSONAL LOGINS". Outermost ring: clipboard checklist icon, label "ACTIVITY LOG". A small key icon at the top left entering the outermost ring. Forest green rings getting lighter outward, amber accents, thick outlines, flat style, no gradients.

**Practical tip before printing:** AI image generators often misspell label text. Generate the artwork, then retype the labels yourself in Canva, PowerPoint or Google Slides, and use one font across all four figures. The diagrams will look far cleaner — and judges notice clean lettering.
