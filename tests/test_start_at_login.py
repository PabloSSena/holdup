"""Start at login keeps the OS entry in line with the saved preference. The entry is faked, except where the
macOS and Linux entries are checked as files."""
import plistlib

from holdup.start_at_login import LaunchAgent, RunKey, StartAtLogin, XdgAutostart, app_executable, login_item
from holdup.store import Store

EXE = r"C:\Users\u\AppData\Local\Programs\Holdup\Holdup.exe"


class FakeEntry:
    def __init__(self, exe=None):
        self.exe = exe

    def set(self, exe):
        self.exe = exe

    def delete(self):
        self.exe = None


def test_first_launch_registers_the_app_to_start_at_login():
    entry = FakeEntry()
    start = StartAtLogin(Store(), entry, EXE)

    start.apply()

    assert start.enabled
    assert entry.exe == EXE


def test_turning_it_off_removes_the_entry_and_turning_it_on_restores_it(tmp_path):
    entry = FakeEntry()
    start = StartAtLogin(Store(tmp_path / "holdup.db"), entry, EXE)
    start.apply()

    start.set_enabled(False)
    assert entry.exe is None
    assert not StartAtLogin(Store(tmp_path / "holdup.db"), FakeEntry(), EXE).enabled

    start.set_enabled(True)
    assert entry.exe == EXE


def test_a_saved_off_preference_wins_over_a_leftover_entry():
    store = Store()
    store.set("start_with_windows", False)
    entry = FakeEntry(EXE)

    StartAtLogin(store, entry, EXE).apply()

    assert entry.exe is None


def test_the_entry_follows_the_exe_when_it_moves():
    entry = FakeEntry(r"C:\old\Holdup.exe")

    StartAtLogin(Store(), entry, EXE).apply()

    assert entry.exe == EXE


def test_each_os_gets_its_own_entry():
    assert isinstance(login_item("win32"), RunKey)
    assert isinstance(login_item("darwin"), LaunchAgent)
    assert isinstance(login_item("linux"), XdgAutostart)


def test_the_macos_launch_agent_runs_the_app_at_login(tmp_path):
    agent = LaunchAgent(tmp_path)
    exe = "/Applications/Holdup.app/Contents/MacOS/Holdup"

    agent.set(exe)

    plist = plistlib.loads(agent.path.read_bytes())
    assert plist["ProgramArguments"] == [exe]
    assert plist["RunAtLoad"] is True
    agent.delete()
    assert not agent.path.exists()
    agent.delete()  # already gone is fine


def test_the_linux_autostart_file_runs_the_app_at_login(tmp_path):
    autostart = XdgAutostart(tmp_path)

    autostart.set("/home/u/Apps/Holdup x86_64.AppImage")

    text = autostart.path.read_text()
    assert text.startswith("[Desktop Entry]\n")
    assert 'Exec="/home/u/Apps/Holdup x86_64.AppImage"\n' in text
    autostart.delete()
    assert not autostart.path.exists()
    autostart.delete()


def test_an_appimage_registers_the_appimage_file_not_its_temporary_mount(monkeypatch):
    monkeypatch.setenv("APPIMAGE", "/home/u/Holdup-x86_64.AppImage")
    assert app_executable() == "/home/u/Holdup-x86_64.AppImage"
    monkeypatch.delenv("APPIMAGE")
    assert app_executable() != "/home/u/Holdup-x86_64.AppImage"
