"""Builds Holdup for macOS (a .dmg holding Holdup.app) or Linux (a .deb and an AppImage). Windows uses build.ps1.

Run from the repo root after: .venv/bin/python -m pip install -e ".[build]"
    .venv/bin/python build.py
Linux also needs dpkg-deb, and appimagetool on PATH or in the APPIMAGETOOL environment variable.
Asset names carry no version, so releases/latest/download/<name> always serves the newest one.
"""
import os
import platform
import plistlib
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BUNDLE_ID = "io.github.pablossena.holdup"
SUMMARY = "Stop leaning into your screen."
CAMERA_REASON = ("Holdup watches your sitting posture through the camera. Frames are analysed in memory and "
                 "never saved or sent anywhere.")


def run(*command: str | Path, **kwargs) -> None:
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True, **kwargs)


def version() -> str:
    with open(ROOT / "pyproject.toml", "rb") as file:
        return tomllib.load(file)["project"]["version"]


def pyinstaller(*extra: str) -> None:
    run(sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--name", "Holdup",
        "--icon", ROOT / "assets" / "holdup.ico",
        "--paths", ROOT / "src",
        "--add-data", f"{ROOT / 'src/holdup/models'}{os.pathsep}holdup/models",
        "--add-data", f"{ROOT / 'src/holdup/fonts'}{os.pathsep}holdup/fonts",
        "--collect-binaries", "mediapipe",
        *extra,
        ROOT / "src" / "holdup" / "__main__.py", cwd=ROOT)


def build_macos() -> list[Path]:
    pyinstaller("--osx-bundle-identifier", BUNDLE_ID)
    app = DIST / "Holdup.app"
    info_path = app / "Contents" / "Info.plist"
    info = plistlib.loads(info_path.read_bytes())
    info.update({
        "NSCameraUsageDescription": CAMERA_REASON,  # without it macOS ends the app when it opens the camera
        "LSUIElement": True,  # a tray app: no Dock icon, no app menu
        "CFBundleShortVersionString": version(),
        "CFBundleVersion": version(),
        "LSMinimumSystemVersion": "11.0",
        "NSHighResolutionCapable": True,
    })
    info_path.write_bytes(plistlib.dumps(info))
    # Editing Info.plist breaks PyInstaller's ad-hoc signature; sign again (still ad-hoc: no Apple Developer ID).
    run("codesign", "--force", "--deep", "--sign", "-", app)

    arch = {"arm64": "AppleSilicon", "x86_64": "Intel"}[platform.machine()]
    dmg = DIST / f"Holdup-macOS-{arch}.dmg"
    staging = DIST / "dmg"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir()
    run("ditto", app, staging / "Holdup.app")  # ditto keeps the bundle's symlinks and signature intact
    (staging / "Applications").symlink_to("/Applications")  # drag-to-install
    dmg.unlink(missing_ok=True)
    run("hdiutil", "create", "-volname", "Holdup", "-srcfolder", staging, "-ov", "-format", "UDZO", dmg)
    shutil.rmtree(staging)
    return [dmg]


def desktop_entry(exec_line: str) -> str:
    return ("[Desktop Entry]\nType=Application\nName=Holdup\n"
            f"Comment={SUMMARY}\nExec={exec_line}\nIcon=holdup\nTerminal=false\nCategories=Utility;\n")


def write_icon(path: Path) -> None:
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    run(sys.executable, "-m", "holdup.icons", path, env=env, cwd=ROOT / "src")


def build_deb(onedir: Path, icon: Path) -> Path:
    root = DIST / "deb"
    shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(onedir, root / "opt" / "holdup", symlinks=True)
    (root / "usr" / "bin").mkdir(parents=True)
    (root / "usr" / "bin" / "holdup").symlink_to("/opt/holdup/Holdup")
    apps = root / "usr" / "share" / "applications"
    apps.mkdir(parents=True)
    (apps / "holdup.desktop").write_text(desktop_entry("/opt/holdup/Holdup"))
    icons = root / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    icons.mkdir(parents=True)
    shutil.copy(icon, icons / "holdup.png")
    (root / "DEBIAN").mkdir()
    size_kb = sum(f.stat().st_size for f in root.rglob("*") if f.is_file() and not f.is_symlink()) // 1024
    (root / "DEBIAN" / "control").write_text(
        "Package: holdup\n"
        f"Version: {version()}\n"
        "Section: utils\nPriority: optional\nArchitecture: amd64\n"
        # Qt's xcb platform plugin (the Mirror runs under X11/XWayland) needs these from the system.
        "Depends: libxcb-cursor0, libxkbcommon-x11-0, libegl1, libgl1\n"
        f"Installed-Size: {size_kb}\n"
        "Maintainer: Holdup <https://github.com/PabloSSena/holdup>\n"
        "Homepage: https://pablossena.github.io/holdup/\n"
        f"Description: {SUMMARY}\n"
        " A tray app that watches your sitting posture through your own camera and shows a small\n"
        " mirror of you when you lean in. Frames are analysed in memory and never stored.\n"
    )
    deb = DIST / "Holdup-linux-amd64.deb"
    run("dpkg-deb", "--build", "--root-owner-group", root, deb)
    shutil.rmtree(root)
    return deb


def build_appimage(onedir: Path, icon: Path) -> Path:
    appdir = DIST / "Holdup.AppDir"
    shutil.rmtree(appdir, ignore_errors=True)
    shutil.copytree(onedir, appdir / "usr" / "lib" / "holdup", symlinks=True)
    apprun = appdir / "AppRun"
    apprun.write_text('#!/bin/sh\nexec "$(dirname "$(readlink -f "$0")")/usr/lib/holdup/Holdup" "$@"\n')
    apprun.chmod(0o755)
    (appdir / "holdup.desktop").write_text(desktop_entry("Holdup"))
    shutil.copy(icon, appdir / "holdup.png")
    appimage = DIST / "Holdup-x86_64.AppImage"
    tool = os.environ.get("APPIMAGETOOL") or shutil.which("appimagetool")
    if not tool:
        sys.exit("appimagetool not found: put it on PATH or set APPIMAGETOOL")
    run(tool, appdir, appimage, env={**os.environ, "ARCH": "x86_64"})
    shutil.rmtree(appdir)
    return appimage


def build_linux() -> list[Path]:
    pyinstaller()
    onedir = DIST / "Holdup"
    icon = DIST / "holdup.png"
    write_icon(icon)
    return [build_deb(onedir, icon), build_appimage(onedir, icon)]


def main() -> None:
    if sys.platform == "darwin":
        built = build_macos()
    elif sys.platform.startswith("linux"):
        built = build_linux()
    else:
        sys.exit("On Windows, build with build.ps1")
    for path in built:
        print(f"Built {path.relative_to(ROOT)} ({path.stat().st_size // 2**20} MB)")


if __name__ == "__main__":
    main()
