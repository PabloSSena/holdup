"""Start with Windows keeps the Run key in line with the saved preference. The Run key is faked."""
from holdup.start_with_windows import StartWithWindows
from holdup.store import Store

EXE = r"C:\Users\u\AppData\Local\Programs\Holdup\Holdup.exe"


class FakeRunKey:
    def __init__(self, command=None):
        self.command = command

    def set(self, command):
        self.command = command

    def delete(self):
        self.command = None


def test_first_launch_registers_the_app_to_start_with_windows():
    run_key = FakeRunKey()
    start = StartWithWindows(Store(), run_key, EXE)

    start.apply()

    assert start.enabled
    assert run_key.command == f'"{EXE}"'


def test_turning_it_off_removes_the_entry_and_turning_it_on_restores_it(tmp_path):
    run_key = FakeRunKey()
    start = StartWithWindows(Store(tmp_path / "holdup.db"), run_key, EXE)
    start.apply()

    start.set_enabled(False)
    assert run_key.command is None
    assert not StartWithWindows(Store(tmp_path / "holdup.db"), FakeRunKey(), EXE).enabled

    start.set_enabled(True)
    assert run_key.command == f'"{EXE}"'


def test_a_saved_off_preference_wins_over_a_leftover_entry():
    store = Store()
    store.set("start_with_windows", False)
    run_key = FakeRunKey(f'"{EXE}"')

    StartWithWindows(store, run_key, EXE).apply()

    assert run_key.command is None


def test_the_entry_follows_the_exe_when_it_moves():
    run_key = FakeRunKey(r'"C:\old\Holdup.exe"')

    StartWithWindows(Store(), run_key, EXE).apply()

    assert run_key.command == f'"{EXE}"'
