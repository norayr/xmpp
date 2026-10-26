#!/usr/bin/env python3
"""Check the XMPP history import against its preserved repository bundles."""

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history"
ENV = dict(os.environ, HGPLAIN="1", HGRCPATH="/dev/null")


def run(*command):
    return subprocess.check_output(command, cwd=ROOT, env=ENV)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def object_id(kind, data):
    return hashlib.sha1(kind + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


def snapshot(repo, node):
    archive = run("hg", "-R", str(repo), "archive", "-r", node,
                  "-t", "tar", "-p", "tree", "-")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            if member.isdir() or member.name == "tree/.hg_archival.txt":
                continue
            assert member.name.startswith("tree/")
            path = member.name[len("tree/"):]
            if member.issym():
                mode, data = b"120000", member.linkname.encode()
            else:
                assert member.isfile()
                mode = b"100755" if member.mode & 0o111 else b"100644"
                data = tar.extractfile(member).read()
            result[path] = (mode, data)
    return result


def check():
    provenance = json.loads((HISTORY / "provenance.json").read_text())
    mapping = json.loads((HISTORY / "commits.json").read_text())
    for bundle in provenance["bundles"]:
        path = HISTORY / bundle["file"]
        assert path.stat().st_size == bundle["bytes"]
        assert sha256(path.read_bytes()) == bundle["sha256"], path
    run("git", "bundle", "verify", str(HISTORY / "voc-before-mercurial.bundle"))
    by_hg = {r["source"]: r["git"] for r in mapping if r["kind"] == "mercurial"}
    by_git = [r for r in mapping if r["kind"] == "git"]
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="history-check-", dir=build) as temp:
        repo = Path(temp) / "mercurial"
        run("hg", "init", str(repo))
        run("hg", "-R", str(repo), "unbundle", str(HISTORY / "oberoncore-xmpp.hg"))
        run("hg", "-R", str(repo), "verify")
        changes = json.loads(run("hg", "-R", str(repo), "log", "-r", "0:tip", "-T", "json"))
        assert len(changes) == len(by_hg) == 15
        assert changes[0]["node"] == provenance["first_revision"]
        assert changes[-1]["node"] == provenance["last_revision"]
        for c in changes:
            commit = by_hg[c["node"]]
            header, message = run("git", "cat-file", "commit", commit).split(b"\n\n", 1)
            expected_parents = [by_hg[p] for p in c["parents"] if p != "0" * 40]
            actual_parents = [f[7:].decode() for f in header.splitlines() if f.startswith(b"parent ")]
            assert actual_parents == expected_parents
            assert message == c["desc"].encode()
            seconds, west = c["date"]
            user = c["user"] if "<" in c["user"] else c["user"] + " <>"
            minutes = abs(west) // 60
            zone = ("-" if west > 0 else "+") + f"{minutes//60:02}{minutes%60:02}"
            identity = f"{user} {int(seconds)} {zone}".encode()
            assert b"author " + identity in header.splitlines()
            assert b"committer " + identity in header.splitlines()
            actual = {}
            for entry in run("git", "ls-tree", "-rz", commit).split(b"\0"):
                if entry:
                    fields, path = entry.split(b"\t", 1)
                    mode, kind, oid = fields.split()
                    assert kind == b"blob"
                    actual[path.decode()] = (mode, oid.decode())
            files = snapshot(repo, c["node"])
            expected = {path: (mode, object_id(b"blob", data)) for path, (mode, data) in files.items()}
            assert actual == expected, c["node"]
        differences = {}
        files = snapshot(repo, changes[-1]["node"])
        for path, (_, data) in files.items():
            supplied = (ROOT / "upstream" / path).read_bytes()
            if data != supplied:
                differences[path] = {"mercurial_sha256": sha256(data), "supplied_sha256": sha256(supplied)}
        assert differences == provenance["snapshot_differences"]
        assert len(files) - len(differences) == provenance["matching_snapshot_files"]
    old_parent = None
    new_parent = by_hg[provenance["last_revision"]]
    for entry in by_git:
        raw = run("git", "cat-file", "commit", entry["git"])
        header, message = raw.split(b"\n\n", 1)
        fields = header.split(b"\n")
        assert [f for f in fields if f.startswith(b"parent ")] == [b"parent " + new_parent.encode()]
        original = [f for f in fields if not f.startswith(b"parent ")]
        if old_parent is not None:
            original.insert(1, b"parent " + old_parent.encode())
        restored = b"\n".join(original) + b"\n\n" + message
        assert object_id(b"commit", restored) == entry["source"]
        old_parent, new_parent = entry["source"], entry["git"]
    assert len(by_git) == 5
    # Check that the original commits are still retrievable from the Git bundle.
    with tempfile.TemporaryDirectory(prefix="git-history-check-", dir=build) as temp:
        run("git", "clone", "--bare", "--quiet", str(HISTORY / "voc-before-mercurial.bundle"), temp)
        for entry in by_git:
            raw = run("git", "--git-dir=" + temp, "cat-file", "commit", entry["source"])
            assert object_id(b"commit", raw) == entry["source"]
    print("XMPP history checks passed: 15 Mercurial snapshots, five Git commits, two bundles")


if __name__ == "__main__":
    check()
