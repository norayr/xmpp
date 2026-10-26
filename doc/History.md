# XMPP source history

The BlackBox XMPP component was written by Pyotr Mikhailovich Kushnir (Пётр
Михайлович Кушнир). He announced it on the
[OberonCore forum](https://forum.oberoncore.ru/viewtopic.php?f=90&t=1104) on
29 July 2008. The [component page](https://oberoncore.ru/bbcc/subs/xmpp/start)
also identifies him as the author. The forum discussion ends on 12 April 2012.

## Recovered Mercurial repository

`https://bitbucket.org/oberoncore/xmpp` was archived before Bitbucket removed
Mercurial hosting. The Internet Archive retained a
[clone response from 15 June 2020](https://web.archive.org/web/20200615162225id_/https://bitbucket.org/oberoncore/xmpp?cmd=getbundle).
Its decompressed payload is preserved in `history/oberoncore-xmpp.hg`.

The bundle restores all 15 changesets, from 2 August 2011 through 3 March 2015:

- First: `ea78c0bcd2ad58d8d89c6be89fc0420a2da85524`.
- Last: `a2cde5435bea63de16239c2c31e399ad0fd43ad2`.
- Authors: `TemirgaleevEE`, `KushnirPM` and `kpmy`.
- One named branch, `default`, and no release tags. Mercurial's `tip` is a
  moving revision name.

`hg verify` checks 15 changesets, 146 file revisions and 114 file paths.
The first changeset records an import from `https://bitbucket.org/petryxa/xmpp`.
That earlier repository's history has not been recovered. No changes newer
than March 2015 occur in the recovered archive.

The Git conversion preserves every tracked path, file byte, executable/link
flag, parent relationship, author name, timestamp, timezone and commit message.
Mercurial has one commit identity and date; these supply both the Git author
and committer fields. Names without an email address retain an empty email
field. Original source identifiers and their Git counterparts are recorded in
`history/commits.json`.

## VOC porting history

Norayr Chilingarian started the VOC port on 14 August 2019. All five commits
retain their original author and committer identities, timestamps, timezones,
messages and complete file trees. Only parent references changed to place these
commits after the Mercurial history; Git commit IDs therefore changed.

| Original 2019 commit | Commit after the Mercurial import |
| --- | --- |
| `790072d` | `ccc8851` |
| `b34f70b` | `7f66817` |
| `c751ca3` | `4333fdb` |
| `b2287d9` | `6fc5e15` |
| `0141aba` | `c5ec3fe` |

The first 2019 commit imports the text-only source layout. The binary documents
remain available in its Mercurial ancestors; the 2026 port also retains the
supplied documents in `upstream/`.

`history/voc-before-mercurial.bundle` preserves the five original Git commits
under their original IDs. The Git and Mercurial bundles have SHA-256 checksums
in `history/provenance.json`.

Of the 56 tracked files at the Mercurial tip, 55 match the supplied snapshot
byte-for-byte. `Mod/Basic.odc` differs in its final 99 bytes; both versions are
retained unchanged. The Mercurial version is in the imported history and bundle;
the supplied version is in `upstream/Mod/Basic.odc`. Their hashes are recorded
in the provenance file. The supplied text exports and archive metadata are also
retained.

## Checking the import

From this checkout, with Git, Mercurial and Python 3 installed:

```sh
make history-test
```

This restores the bundled Mercurial repository in a temporary build directory,
runs `hg verify`, compares all 15 snapshots and commit metadata against Git,
checks both bundle hashes and the supplied snapshot, and verifies the five
2019 commits against their original Git objects. It leaves the working tree
and branch references unchanged.

To inspect the original Mercurial repository separately:

```sh
hg init /path/to/xmpp-hg
hg -R /path/to/xmpp-hg unbundle "$PWD/history/oberoncore-xmpp.hg"
hg -R /path/to/xmpp-hg verify
hg -R /path/to/xmpp-hg log
```

Some original source headers refer to `Docu/BB-License`. No such file is present
in the recovered changesets or supplied snapshot. The author notices are
retained; licensing confirmation remains pending.
