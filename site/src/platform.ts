export type Platform = "windows" | "mac" | "linux";

/** The desktop OS a download is for, or null on phones, tablets and Chromebooks, where Holdup does not run.
 * maxTouchPoints tells an iPad apart: iPadOS asks for desktop sites with a Mac user agent. */
// shortcut: user-agent sniffing (navigator.userAgentData is Chromium-only); upgrade if browsers change these tokens.
export function detectPlatform(userAgent: string, maxTouchPoints = 0): Platform | null {
  if (/Windows NT/.test(userAgent)) return "windows";
  if (/iPhone|iPad|iPod|Android|CrOS/.test(userAgent)) return null;
  if (/Macintosh/.test(userAgent)) return maxTouchPoints > 1 ? null : "mac";
  if (/X11|Linux/.test(userAgent)) return "linux";
  return null;
}
