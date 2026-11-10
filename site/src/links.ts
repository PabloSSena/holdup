const repo = "https://github.com/PabloSSena/holdup";
// The release workflow publishes exactly these asset names; `latest` always serves the newest release.
const latest = `${repo}/releases/latest/download`;

export const REPO_URL = repo;
export const DOWNLOADS = {
  windows: `${latest}/HoldupSetup.exe`,
  macAppleSilicon: `${latest}/Holdup-macOS-AppleSilicon.dmg`,
  macIntel: `${latest}/Holdup-macOS-Intel.dmg`,
  appImage: `${latest}/Holdup-x86_64.AppImage`,
  deb: `${latest}/Holdup-linux-amd64.deb`,
};
export const RELEASE_NOTES_URL = `${repo}/releases/latest`;
