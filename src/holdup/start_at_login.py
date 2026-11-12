"""Start at login: the app launches when the User signs in. Windows calls it Start with Windows.

The Store owns the preference (on by default); the OS entry is made to match it at every launch,
so the two never disagree for long and the entry follows the app if it moves.
Each OS has its own per-user entry, none needing admin: the Run key on Windows, a LaunchAgent on macOS
and an XDG autostart file on Linux.
"""
import os
import plistlib
import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
BUNDLE_ID = "io.github.pablossena.holdup"


def app_executable() -> str:
    """The file that launches the packaged app. In an AppImage, sys.executable is inside a mount that vanishes on
    quit, so the AppImage file itself is what to register or relaunch."""
    return os.environ.get("APPIMAGE") or sys.executable


class RunKey:
    """Windows: one value in HKCU\\...\\Run."""

    def __init__(self, name: str = "Holdup"):
        self.name = name

    def set(self, exe: str) -> None:
        import winreg

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.SetValueEx(key, self.name, 0, winreg.REG_SZ, f'"{exe}"')

    def delete(self) -> None:
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, self.name)
        except FileNotFoundError:
            pass


class LaunchAgent:
    """macOS: a plist in ~/Library/LaunchAgents that launchd runs at login."""

    def __init__(self, folder: Path | None = None):
        self.path = (folder or Path.home() / "Library" / "LaunchAgents") / f"{BUNDLE_ID}.plist"

    def set(self, exe: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("wb") as file:
            plistlib.dump({"Label": BUNDLE_ID, "ProgramArguments": [exe], "RunAtLoad": True}, file)

    def delete(self) -> None:
        self.path.unlink(missing_ok=True)


class XdgAutostart:
    """Linux: a .desktop file in the XDG autostart folder, which desktop sessions launch at login."""

    def __init__(self, folder: Path | None = None):
        config = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
        self.path = (folder or Path(config) / "autostart") / "holdup.desktop"

    def set(self, exe: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        escaped = exe.replace("\\", "\\\\").replace('"', '\\"')
        self.path.write_text(
            "[Desktop Entry]\nType=Application\nName=Holdup\nComment=Stop leaning into your screen.\n"
            f'Exec="{escaped}"\nIcon=holdup\nTerminal=false\nX-GNOME-Autostart-enabled=true\n'
        )

    def delete(self) -> None:
        self.path.unlink(missing_ok=True)


def login_item(platform: str = sys.platform):
    """This OS's per-user start-at-login entry."""
    if platform == "win32":
        return RunKey()
    if platform == "darwin":
        return LaunchAgent()
    return XdgAutostart()


class StartAtLogin:
    def __init__(self, store, entry, exe: str):
        self._store = store
        self._entry = entry
        self._exe = exe

    @property
    def enabled(self) -> bool:
        return self._store.get("start_with_windows", True)  # the name predates macOS and Linux; kept for saved choices

    def set_enabled(self, on: bool) -> None:
        self._store.set("start_with_windows", on)
        self.apply()

    def apply(self) -> None:
        """Make the OS do what the saved preference says."""
        if self.enabled:
            self._entry.set(self._exe)
        else:
            self._entry.delete()
