# J2ME Online on Render

Browser J2ME emulator with a same-origin WebSocket-to-TCP bridge for Ngọc Rồng game servers. Users select their own JAR locally; games, passwords and RMS saves are not stored on this server. The bridge relays game traffic to allowlisted game endpoints without recording packet contents.

Based on [zb3/freej2me-web](https://github.com/zb3/freej2me-web), pinned to c19416e75cbc15f9a27f7e967ee81cb108761e30, licensed GPL-3.0-or-later. Modified Java sources are served at `/source/`. The original emulator source at that pinned revision and these patch files constitute the corresponding source. CheerpJ is loaded from its vendor and is subject to its own non-commercial license.

Deploy the Dockerfile as a Render **Free Web Service**, region Singapore, port 10000, health check `/healthz`. Free hours and bandwidth apply across the workspace. Active game connections may be interrupted by service restarts; phone browsers may suspend when the screen is locked.

Open the HTTPS URL on a phone, select a JAR, then choose the mobile launch button. Do not distribute proprietary game JARs in this repository.

Compatibility requires testing with the chosen game JAR. Implemented: TCP sockets, HTTP/HTTPS game requests, input/output streams, mobile controls from upstream. Not implemented: UDP, incoming server sockets, TLS certificate metadata, generic arbitrary game-server access.
