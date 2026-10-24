// shortcut: user-agent sniffing (navigator.userAgentData is Chromium-only); upgrade if browsers stop sending "Windows NT".
export const isWindows = (userAgent: string) => /Windows NT/.test(userAgent);
