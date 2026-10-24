export type Lang = "en" | "pt-BR";

const KEY = "holdup.lang";
const isLang = (value: unknown): value is Lang => value === "en" || value === "pt-BR";

// Reading `localStorage` itself can throw (blocked site data), so it's fetched lazily inside the try.
type GetStorage = () => Storage;
const local: GetStorage = () => localStorage;

/** The language to show: English on every first visit, or the toggle choice saved on an earlier one. */
export function storedLang(storage: GetStorage = local): Lang {
  try {
    const value = storage().getItem(KEY);
    return isLang(value) ? value : "en";
  } catch {
    return "en";
  }
}

export function saveLang(lang: Lang, storage: GetStorage = local): void {
  try {
    storage().setItem(KEY, lang);
  } catch {
    // Storage blocked: the choice lasts until the page is closed.
  }
}
