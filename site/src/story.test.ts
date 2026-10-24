import { describe, expect, it } from "vitest";
import { seg, trackProgress, word } from "./story";

describe("trackProgress", () => {
  const vh = 800;

  it("is 0 before the track reaches the top of the viewport", () => {
    expect(trackProgress(300, 3000, vh)).toBe(0);
  });

  it("runs from 0 to 1 while the track scrolls past", () => {
    expect(trackProgress(0, 3000, vh)).toBe(0);
    expect(trackProgress(-1100, 3000, vh)).toBe(0.5);
    expect(trackProgress(-2200, 3000, vh)).toBe(1);
  });

  it("stays at 1 once the track has scrolled away", () => {
    expect(trackProgress(-5000, 3000, vh)).toBe(1);
  });

  it("jumps from 0 to 1 for a track no taller than the viewport", () => {
    expect(trackProgress(10, vh, vh)).toBe(0);
    expect(trackProgress(0, vh, vh)).toBe(1);
  });
});

describe("seg", () => {
  it("maps a slice of progress onto 0..1 and clamps outside it", () => {
    expect(seg(0.1, 0.2, 0.6)).toBe(0);
    expect(seg(0.4, 0.2, 0.6)).toBeCloseTo(0.5);
    expect(seg(0.9, 0.2, 0.6)).toBe(1);
  });
});

describe("word", () => {
  it("fills {placeholders} in a translated string", () => {
    expect(word("Leaning in · {s}s", { s: 3 })).toBe("Leaning in · 3s");
    expect(word("frame {n} · {state}", { n: 1042, state: "discarded" })).toBe("frame 1042 · discarded");
  });
});
