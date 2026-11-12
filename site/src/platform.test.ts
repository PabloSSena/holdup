import { describe, expect, it } from "vitest";
import { detectPlatform, type Platform } from "./platform";

const browsers: Record<string, [ua: string, platform: Platform | null, maxTouchPoints?: number]> = {
  "Chrome on Windows": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", "windows"],
  "Edge on Windows": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0", "windows"],
  "Firefox on Windows": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0", "windows"],
  "Firefox on Windows ARM": ["Mozilla/5.0 (Windows NT 10.0; ARM64; rv:131.0) Gecko/20100101 Firefox/131.0", "windows"],
  "Safari on macOS": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15", "mac"],
  "Chrome on macOS": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", "mac"],
  "Chrome on Linux": ["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", "linux"],
  "Firefox on Ubuntu": ["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0", "linux"],
  "Chrome on ChromeOS": ["Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", null],
  "Chrome on Android": ["Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36", null],
  "Safari on iPhone": ["Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", null],
  "Safari on iPad": ["Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", null],
  "Safari on iPad, desktop site": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15", null, 5],
};

describe("detectPlatform", () => {
  it.each(Object.entries(browsers))("reads %s", (_, [ua, platform, touch]) => expect(detectPlatform(ua, touch)).toBe(platform));
});
