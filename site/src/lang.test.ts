import { describe, expect, it } from "vitest";
import { saveLang, storedLang } from "./lang";

function memoryStorage(initial: Record<string, string> = {}) {
  const data = { ...initial };
  return {
    data,
    storage: () => ({ getItem: (k: string) => data[k] ?? null, setItem: (k: string, v: string) => void (data[k] = v) }) as Storage,
  };
}

const blocked = () => {
  throw new DOMException("blocked", "SecurityError");
};

describe("storedLang", () => {
  it("starts in English on a first visit", () => {
    expect(storedLang(memoryStorage().storage)).toBe("en");
  });

  it("keeps a choice saved on an earlier visit", () => {
    const { storage } = memoryStorage();
    saveLang("pt-BR", storage);
    expect(storedLang(storage)).toBe("pt-BR");
  });

  it("ignores a stored value that isn't a language", () => {
    expect(storedLang(memoryStorage({ "holdup.lang": "fr" }).storage)).toBe("en");
  });

  it("falls back to English when storage is blocked", () => {
    expect(storedLang(blocked)).toBe("en");
  });
});

describe("saveLang", () => {
  it("doesn't throw when storage is blocked", () => {
    expect(() => saveLang("pt-BR", blocked)).not.toThrow();
  });
});
