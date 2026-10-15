"""Start with Windows: the app launches at User login through the per-user Run key.

The Store owns the preference (on by default); the Run key is made to match it at every launch,
so the two never disagree for long and the entry follows the exe if it moves.
"""
import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


class RunKey:
    """One value in HKCU\\...\\Run. No admin needed."""

    def __init__(self, name: str = "Holdup"):
        self.name = name

    def set(self, command: str) -> None:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.SetValueEx(key, self.name, 0, winreg.REG_SZ, command)

    def delete(self) -> None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, self.name)
        except FileNotFoundError:
            pass


class StartWithWindows:
    def __init__(self, store, run_key, exe: str):
        self._store = store
        self._run_key = run_key
        self._exe = exe

    @property
    def enabled(self) -> bool:
        return self._store.get("start_with_windows", True)

    def set_enabled(self, on: bool) -> None:
        self._store.set("start_with_windows", on)
        self.apply()

    def apply(self) -> None:
        """Make Windows do what the saved preference says."""
        if self.enabled:
            self._run_key.set(f'"{self._exe}"')
        else:
            self._run_key.delete()
