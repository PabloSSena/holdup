import { expect, it } from "vitest";
import en from "./en.json";
import ptBR from "./pt-BR.json";

it("has every string in both languages", () => {
  expect(Object.keys(ptBR).sort()).toEqual(Object.keys(en).sort());
});

it("has no empty strings", () => {
  for (const dict of [en, ptBR]) expect(Object.values(dict).filter((s) => !s.trim())).toEqual([]);
});
