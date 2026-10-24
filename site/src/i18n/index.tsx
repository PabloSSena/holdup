import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { saveLang, storedLang, type Lang } from "../lang";
import en from "./en.json";
import ptBR from "./pt-BR.json";

export type Key = keyof typeof en;

const dictionaries: Record<Lang, Record<Key, string>> = { en, "pt-BR": ptBR };

type I18n = { lang: Lang; setLang: (lang: Lang) => void; t: (key: Key) => string };

const I18nContext = createContext<I18n | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState(() => storedLang());

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = (next: Lang) => {
    saveLang(next);
    setLangState(next);
  };

  return <I18nContext.Provider value={{ lang, setLang, t: (key) => dictionaries[lang][key] }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const i18n = useContext(I18nContext);
  if (!i18n) throw new Error("useI18n needs an <I18nProvider> above it");
  return i18n;
}
