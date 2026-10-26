# XMPP for VOC

An Oberon-2 XMPP library using ooc-xml for XML streams and VOC's TCP/TLS modules
for connections. It handles Unicode JIDs and messages, STARTTLS or direct TLS,
SASL PLAIN authentication, resource binding and incoming/outgoing stanzas.

This continues the VOC port started here in 2019. The current implementation is
in `src/Xmpp*.Mod`; the earlier sources remain in `src/` under their original
names. The makefile builds the current modules.

## Status

Login, binding and a Unicode self-message round trip have been tested against a
live server with a UTF-8 (Armenian language) account and domain. The original
extension dispatch, roster, discovery, file transfers, scheduling and DIGEST-MD5
authentication still need porting. Applications currently drive the synchronous client with `Start`,
`Step`, `Send` and `Close`.

## Build

Use a matching VOC compiler/runtime installation, such as VOC 4.0.2, and an
updated [VOC checkout](https://github.com/vishapoberon/compiler) alongside this
repository. The source build supplies `XMLStream`, the shared ooc modules and
the TLS socket-upgrade API:

```sh
make test VOC="$PWD/../compiler/install/bin/voc"
make network-test tls-regression VOC="$PWD/../compiler/install/bin/voc"
make probe VOC="$PWD/../compiler/install/bin/voc"
```

Set `VOCSRC=/path/to/compiler` if the VOC checkout is elsewhere. Output goes into
`build/2`; `BUILD`, `VOC`, `CC` and `CFLAGS` can also be overridden. With no VOC
source checkout, the build uses installed dependencies, which must include
`XMLStream`, `IDNA` and `TLS13Live.Start` for the network target.

The offline target builds the portable library. Network targets require Linux,
libidn2 development files and `pkg-config`. Loopback tests need Python 3.13+ and
OpenSSL. Programs linking `XmppTCP` need
`LDLIBS="$(pkg-config --libs libidn2)"` when invoking VOC.

## Use

`XmppClient` negotiates a connection over `XmppWire.Transport`. `XmppTCP.Open`
provides the Linux transport; its dial host and service domain are separate.
The service domain is used for certificate verification. PLAIN must be enabled
explicitly and is sent only over verified TLS.

JIDs and message text use shared `oocUnicode.LONGCHAR` UTF-16 code units;
network buffers use UTF-8. `XmppItems.UTF8` and `UTF8Bytes` convert between them.
`XmppTypes` records the Component Pascal type widths and their VOC mappings.

Domains such as `ծոց.հայ` can be passed directly. XML stream identities remain
Unicode; DNS, TLS SNI and certificate matching use the corresponding A-labels.
This version uses libidn2 for domain normalization and validation.

`XmppProbe` reads a password from standard input and can send a test message
to its own bound resource. See [client setup](doc/Client.md), [test coverage](doc/Testing.md)
and [the port inventory](doc/PortStatus.md). XML framing is described in
[the ooc-xml streaming documentation](https://github.com/norayr/voc-ooc-xml/blob/main/doc/Streaming.md).

Offline, loopback and shared-TLS tests pass with GCC, Clang, TCC and ASan/UBSan.
Security review is ongoing; use trusted XML during development.

## Sources

The original BlackBox component is by Pyotr Mikhailovich Kushnir (Пётр
Михайлович Кушнир). OberonCore's [component page](https://oberoncore.ru/bbcc/subs/xmpp/start)
and [forum announcement](https://forum.oberoncore.ru/viewtopic.php?f=90&t=1104)
identify its author. The Git history contains the 15 recovered Mercurial
changesets from 2011–2015, followed by Norayr Chilingarian's five VOC porting
commits from 14 August 2019 and the current port. See [the history record](doc/History.md)
for the archived repository, conversion checks and original commit IDs.

`upstream/` preserves the supplied Component Pascal snapshot at revision
`a2cde5435bea63de16239c2c31e399ad0fd43ad2`: 88 files, including 31 paired
`.txt`/`.odc` modules. Its manifest records sizes and SHA-256 hashes. The `.odc`
documents retain Unicode text that was lost in some text exports. Original
notices are retained. Some headers refer to `Docu/BB-License`, but that document
is absent from the recovered history and supplied snapshot; licensing confirmation
is still needed.

VOC carries the native modules under `src/ports/xmpp/`; reusable Unicode,
strings, channels, URI and IDNA modules stay in VOC's shared ooc package.
