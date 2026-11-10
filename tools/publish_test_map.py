"""Publish verified test maps on origin/main without touching the developer's index."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def git(directory, *args):
    return subprocess.check_output(["git", "-C", str(directory), *args], text=True).strip()


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
        maps.append((source, digest))

    remote = git(ROOT, "remote", "get-url", "origin")
    with TemporaryDirectory(dir=ROOT / "build") as temp:
        checkout = Path(temp)
        git(checkout, "clone", "--depth=1", "--branch=main", "--filter=blob:none",
            "--no-checkout", remote, ".")
        git(checkout, "read-tree", "HEAD")
        git(checkout, "checkout-index", "--", ".gitattributes")
        git(checkout, "lfs", "install", "--local")
        added = []
        for source, digest in maps:
            path = (Path("Test Maps") / family / source.name).as_posix()
            pointer = (f"version https://git-lfs.github.com/spec/v1\n"
                       f"oid sha256:{digest}\nsize {source.stat().st_size}")
            if git(checkout, "ls-tree", "HEAD", "--", path):
                if git(checkout, "show", f"HEAD:{path}") != pointer:
                    raise ValueError(f"Different map already published: {path}")
                continue
            dest = checkout / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            git(checkout, "add", "--", path)
            if git(checkout, "show", f":{path}") != pointer:
                raise RuntimeError(f"Git LFS pointer verification failed: {path}")
            added.append(source.name)
        if added:
            git(checkout, "commit", "-m", f"Archive {family} test maps: " + ", ".join(added))
            git(checkout, "push", "origin", "HEAD:main")
    print(f"Published {len(maps)} verified {family} map(s) on origin/main")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project", choices=["799x", "solo", "mini", "ffa"])
    parser.add_argument("names", nargs="+")
    args = parser.parse_args()
    publish(args.project, args.names)
