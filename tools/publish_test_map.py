"""Publish verified test maps on origin/main without touching the developer's index."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
from map_archive import Archive
import shutil
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def git(directory, *args):
    return subprocess.check_output(["git", "-C", str(directory), *args], text=True).strip()


def commit_source(checkout, project, output, report):
    meta = report["project_metadata"]
    branch = meta["branch"]
    git(checkout, "fetch", "--depth=1", "origin", f"refs/heads/{branch}")
    parent = git(checkout, "rev-parse", "FETCH_HEAD")
    if parent != report["source_parent"]:
        raise RuntimeError(f"{branch} changed since the build started. Reconcile and rebuild.")
    folder = f"projects/{project}"
    baseline = git(checkout, "show", f"{parent}:{folder}/release/{meta['release']}")
    if f"oid sha256:{meta['sha256']}" not in baseline.splitlines():
        raise RuntimeError("The map branch does not contain the build's baseline release")

    git(checkout, "read-tree", parent)
    git(checkout, "checkout-index", "-f", "--", ".gitattributes")
    src = f"{folder}/src"
    git(checkout, "rm", "-rq", "--cached", "--", src)
    config_path = ROOT / "tools.local.json"
    config = json.loads(config_path.read_bytes()) if config_path.exists() else {}
    dll = os.environ.get("STORMLIB_DLL") or config["stormlib"]
    with Archive(dll, output) as packed:
        for entry in report["source_entries"]:
            rel = PureWindowsPath(entry)
            if rel.anchor or any(part.lower() in (".git", "..") for part in rel.parts):
                raise ValueError(f"Invalid archive path: {entry}")
            path = (checkout / src).joinpath(*rel.parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(packed.read(entry))
    (checkout / folder / "project.json").write_text(json.dumps(meta, indent=2) + "\n")
    git(checkout, "add", "-f", "--", src, f"{folder}/project.json")
    tree = git(checkout, "write-tree")
    commit = git(checkout, "commit-tree", tree, "-p", parent, "-m",
                 f"Editable source for {output.name} ({report['sha256']})")
    git(checkout, "read-tree", "HEAD")
    git(checkout, "checkout-index", "-f", "--", ".gitattributes")
    return commit


def publish(project, names):
    family = json.loads((ROOT / "projects" / project / "project.json").read_bytes())["map_type"]
    maps = []
    for name in names:
        if Path(name).name != name or not name.lower().endswith(".w3x"):
            raise ValueError(f"Invalid map name: {name}")
        source = ROOT / "build" / project / name
        report = json.loads(source.with_suffix(".verification.json").read_bytes())
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if report.get("verified") is not True or digest != report["sha256"]:
            raise ValueError(f"Map does not match its verification report: {name}")
        maps.append((source, digest, report))

    remote = git(ROOT, "remote", "get-url", "origin")
    with TemporaryDirectory(dir=ROOT / "build") as temp:
        checkout = Path(temp)
        git(checkout, "clone", "--depth=1", "--branch=main", "--filter=blob:none",
            "--no-checkout", remote, ".")
        git(checkout, "read-tree", "HEAD")
        git(checkout, "checkout-index", "--", ".gitattributes")
        git(checkout, "lfs", "install", "--local")
        added = []
        source_ref = None
        for source, digest, report in maps:
            path = (Path("Test Maps") / family / source.name).as_posix()
            pointer = (f"version https://git-lfs.github.com/spec/v1\n"
                       f"oid sha256:{digest}\nsize {source.stat().st_size}")
            if git(checkout, "ls-tree", "HEAD", "--", path):
                if git(checkout, "show", f"HEAD:{path}") != pointer:
                    raise ValueError(f"Different map already published: {path}")
                if "source_parent" in report:
                    record = json.loads(git(checkout, "show", f"HEAD:{path}.source.json"))
                    if record["sha256"] != digest or record["branch"] != report["project_metadata"]["branch"]:
                        raise RuntimeError(f"Invalid source record for {path}")
                continue
            dest = checkout / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            git(checkout, "add", "--", path)
            if git(checkout, "show", f":{path}") != pointer:
                raise RuntimeError(f"Git LFS pointer verification failed: {path}")
            if "source_parent" in report:
                if len(maps) != 1:
                    raise ValueError("Publish each source-tracked build individually")
                branch = report["project_metadata"]["branch"]
                commit = commit_source(checkout, project, source, report)
                source_ref = f"{commit}:refs/heads/{branch}"
                record = dict(branch=branch, commit=commit, sha256=digest)
                (checkout / (path + ".source.json")).write_text(json.dumps(record, indent=2) + "\n")
                git(checkout, "add", "--", path, path + ".source.json")
            added.append(source.name)
        if added:
            git(checkout, "commit", "-m", f"Archive {family} test maps: " + ", ".join(added))
            refs = ["HEAD:refs/heads/main"]
            if source_ref:
                refs.append(source_ref)
            git(checkout, "push", "--atomic", "origin", *refs)
    print(f"Published {len(maps)} verified {family} map(s) on origin/main")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project", choices=["casino", "799x", "solo", "mini", "ffa"])
    parser.add_argument("names", nargs="+")
    args = parser.parse_args()
    publish(args.project, args.names)
