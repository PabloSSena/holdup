// The scroll-driven choreography from the Claude Design export (.scratch/website/design/Holdup Scroll Story.dc.html).
// Scroll position is the playhead: each tall "track" section has a sticky stage, and how far the track has been
// scrolled through (0..1) drives the CSS custom properties and SVG attributes below. Timings are the design's.
import Lenis from "lenis";
import type { Key } from "./i18n";

export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
/** Where v sits inside [a, b], as 0..1. */
export const seg = (v: number, a: number, b: number) => clamp((v - a) / (b - a));
const inOutCubic = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const outCubic = (t: number) => 1 - Math.pow(1 - t, 3);
const outExpo = (t: number) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t));
const inOutSine = (t: number) => -(Math.cos(Math.PI * t) - 1) / 2;
const outBack = (t: number) => 1 + 2.70158 * Math.pow(t - 1, 3) + 1.70158 * Math.pow(t - 1, 2);

/** How far a track has been scrolled through: 0 when its top meets the viewport top, 1 when its bottom meets the bottom. */
export function trackProgress(top: number, height: number, vh: number) {
  const travel = height - vh;
  return travel <= 1 ? (top <= 0 ? 1 : 0) : clamp(-top / travel);
}

/** Fills {name} placeholders in a translated string. */
export const word = (text: string, values: Record<string, string | number>) =>
  text.replace(/\{(\w+)\}/g, (_, k: string) => String(values[k]));

export type Step = 1 | 2 | 3 | 4;

// Track heights in viewport heights (the features track is sized from its row's width instead).
const TRACKS = { intro: 3.8, how: 3.8, privacy: 3, oss: 2.8 } as const;

/** Wires the story to `root` and returns a cleanup. `relayout` must be called when the text (and so the letters) changes. */
export function startStory(root: HTMLElement, getT: () => (key: Key) => string, onStep: (step: Step) => void) {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.toggle("reduced", reduced);
  const q = <E extends Element = HTMLElement>(s: string) => root.querySelector<E & HTMLElement>(s);
  const qa = <E extends Element = HTMLElement>(s: string) => [...root.querySelectorAll<E & HTMLElement>(s)];
  const set = (el: HTMLElement | null, k: string, v: number) => el?.style.setProperty(k, String(v));
  const prog = (el: HTMLElement | null) => {
    if (!el) return 0;
    if (reduced) return 1;
    const r = el.getBoundingClientRect();
    return trackProgress(r.top, r.height, innerHeight);
  };

  let laidOutWidth = 0;
  let laidOutHeight = 0;
  let travel = 0;
  let step: Step = 1;
  let letters: HTMLElement[] = [];
  let scatter: { dx: number; dy: number; rot: number; d: number }[] = [];

  function layout() {
    const vw = innerWidth, vh = innerHeight;
    if (!vw || !vh) return;
    laidOutWidth = vw;
    laidOutHeight = vh;
    if (!reduced) for (const [k, n] of Object.entries(TRACKS)) {
      const el = q(`[data-track="${k}"]`);
      if (el) el.style.height = vh * n + "px";
    }
    const row = q("[data-row]"), ft = q('[data-track="features"]');
    if (row && ft && !reduced) {
      const prev = row.style.transform;
      row.style.transform = "none";
      travel = Math.max(0, row.scrollWidth - vw);
      row.style.transform = prev;
      ft.style.height = vh + travel * 1.1 + "px";
    }
    letters = qa("[data-ch]");
    // Deterministic pseudo-random scatter per letter, so every visit breaks apart the same way.
    scatter = letters.map((_, i) => {
      const r = (k: number) => { const x = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453; return x - Math.floor(x); };
      return { dx: (r(1) - 0.5) * 180, dy: -(90 + r(2) * 240), rot: (r(3) - 0.5) * 40, d: r(4) * 0.08 };
    });
    update();
  }

  function update() {
    const vw = innerWidth, vh = innerHeight;
    if (!vh) return;
    // shortcut: ignore height-only changes under 150px (mobile URL bar showing/hiding), so tracks don't resize mid-scroll.
    if (vw !== laidOutWidth || Math.abs(vh - laidOutHeight) > 150) return layout();
    const t = getT();

    // 1 · intro: the question breaks apart, the hero resolves, the headline fills like liquid
    const a = prog(q('[data-track="intro"]'));
    const skew = q("[data-skew]");
    if (skew) skew.style.transform = `skewX(${-12 * (1 - outCubic(seg(a, 0, 0.14)))}deg)`;
    letters.forEach((el, i) => {
      const r = scatter[i];
      const e = reduced ? 1 : outCubic(seg(a, 0.12 + r.d, 0.42 + r.d));
      el.style.transform = `translate(${r.dx * e}px, ${r.dy * e}px) rotate(${r.rot * e}deg) scale(${1 - 0.3 * e})`;
      el.style.filter = e > 0.001 ? `blur(${e * 16}px)` : "none";
      el.style.opacity = String(1 - e);
    });
    qa("[data-part]").forEach((p, j) => set(p, "--f", outExpo(seg(a, 0.3 + j * 0.06, 0.64 + j * 0.06))));
    qa("[data-liq]").forEach((o, j) => {
      const lv = inOutSine(seg(a, 0.44 + j * 0.05, 0.86 + j * 0.06)), h = o.offsetHeight * 1.02;
      o.style.transform = `translateY(${(1 - lv) * h}px)`;
      (o.firstElementChild as HTMLElement | null)?.style.setProperty("transform", `translateY(${-(1 - lv) * h}px)`);
    });
    qa("[data-glow]").forEach((g, j) => {
      const s = outCubic(seg(a, 0.1, 0.9));
      g.style.transform = `translate(-50%,-50%) translate(${(j ? 1 : -1) * s * 40}px, ${(1 - s) * (j ? 80 : 50)}px) scale(${0.6 + s * (j ? 0.6 : 0.5)})`;
      g.style.opacity = String(j ? s * 0.9 : 0.3 + s * 0.7);
    });
    const hv = outCubic(seg(a, 0.6, 0.86));
    set(root, "--hv", hv);
    const header = q("[data-header]");
    if (header) {
      header.style.pointerEvents = hv > 0.5 ? "auto" : "none";
      header.style.filter = hv < 0.999 ? `blur(${(1 - hv) * 10}px)` : "none";
    }

    // 2 · how it works: the character calibrates, leans in, gets the Mirror, sits up
    const m = prog(q('[data-track="how"]'));
    const part = (k: string) => q<SVGElement>(`[data-sv="${k}"]`);
    const cal = seg(m, 0.03, 0.18);
    const lean = inOutCubic(seg(m, 0.34, 0.46)) * (1 - inOutCubic(seg(m, 0.76, 0.86)));
    const ang = 32 * lean, rr = (ang * Math.PI) / 180;
    // Leaning rotates the upper body around the hip at (100, 160).
    const rot = (x: number, y: number) => {
      const dx = x - 100, dy = y - 160;
      return [100 + dx * Math.cos(rr) - dy * Math.sin(rr), 160 + dx * Math.sin(rr) + dy * Math.cos(rr)];
    };
    const top = rot(103, 106), shoulder = rot(104, 112), headAt = rot(106, 80);
    const typing = m > 0.2 && m < 0.36 ? Math.sin(m * 900) * 1.6 : 0;
    const hand = [176, 145 + typing], elbow = [shoulder[0] + (hand[0] - shoulder[0]) * 0.3, hand[1] - 1];
    const f = (n: number) => n.toFixed(2);
    part("torso")?.setAttribute("d", `M99 158 L${f(top[0])} ${f(top[1])}`);
    part("head")?.setAttribute("transform", `translate(${f(headAt[0])} ${f(headAt[1])}) rotate(${f(ang * 0.8)})`);
    part("arm")?.setAttribute("d", `M${f(shoulder[0])} ${f(shoulder[1])} L${f(elbow[0])} ${f(elbow[1])} L${hand[0]} ${f(hand[1])}`);
    const ghostTorso = part("ghostT");
    if (ghostTorso) {
      const len = 52.1;
      ghostTorso.style.strokeDasharray = String(len);
      ghostTorso.style.strokeDashoffset = String(len * (1 - cal));
      ghostTorso.style.opacity = cal > 0 ? "0.2" : "0";
    }
    part("ghostH")?.style.setProperty("opacity", String(seg(cal, 0.5, 1)));
    part("ghostL")?.style.setProperty("opacity", String(seg(cal, 0.8, 1)));
    const scan = part("scan");
    if (scan) {
      scan.setAttribute("y", String(46 + 124 * cal));
      scan.style.opacity = cal > 0 && cal < 1 ? "1" : "0";
    }
    const mirrorScale = reduced ? 0 : Math.max(0, outBack(seg(m, 0.6, 0.67)) * (1 - inOutCubic(seg(m, 0.79, 0.84))));
    part("mirror")?.setAttribute("transform", `translate(202 127) scale(${mirrorScale.toFixed(3)}) translate(-202 -127)`);
    part("led")?.style.setProperty("fill", lean > 0.5 ? "var(--fw)" : "var(--ac)");
    const chip = q("[data-chip]");
    if (chip) {
      const [text, color] = m < 0.2 && !reduced
        ? [t("how.chip.calibration"), "var(--sd)"]
        : lean > 0.5 ? [t("how.chip.forward"), "var(--fw)"] : [t("how.chip.good"), "var(--ac)"];
      if (chip.textContent !== text) chip.textContent = text;
      chip.style.background = color;
    }
    const timer = q("[data-tmr]"), timerText = q("[data-tmr-t]"), timerBar = q("[data-tmr-b]");
    if (timer && timerText && timerBar) {
      const lt = seg(m, 0.44, 0.6);
      if (lean > 0.5 && m < 0.78) {
        timer.style.opacity = "1";
        timerText.textContent = word(t("how.timer"), { s: Math.max(1, Math.ceil(lt * 5)) });
        timerText.style.color = "var(--fw)";
        timerBar.style.transform = `scaleX(${lt})`;
        timerBar.parentElement!.style.display = "";
      } else if (m >= 0.84) {
        timer.style.opacity = "1";
        timerText.textContent = t("how.holding");
        timerText.style.color = "var(--ac)";
        timerBar.parentElement!.style.display = "none";
      } else timer.style.opacity = "0";
    }
    const nextStep: Step = reduced ? 4 : m < 0.2 ? 1 : m < 0.56 ? 2 : m < 0.79 ? 3 : 4;
    if (nextStep !== step) onStep((step = nextStep));

    // 3 · privacy: a frame is scanned, shredded, and the numbers count in
    const pv = prog(q('[data-track="privacy"]'));
    const sc = seg(pv, 0.05, 0.28), shred = seg(pv, 0.3, 0.6);
    const line = q("[data-scan]");
    if (line) {
      line.style.top = sc * 100 + "%";
      line.style.opacity = sc > 0 && sc < 1 ? "1" : "0";
    }
    qa("[data-kp]").forEach((el) => {
      const y = Number(el.dataset.kp);
      el.style.opacity = String(seg(sc, y - 0.08, y) * (1 - seg(shred, 0, 0.3)));
    });
    const label = q("[data-flabel]");
    if (label) {
      const state = t(shred > 0 ? "privacy.frame.discarded" : sc > 0 ? "privacy.frame.analysing" : "privacy.frame.memory");
      label.textContent = word(t("privacy.frame"), { n: 1042 + Math.floor(pv * 240), state });
      label.style.opacity = String(1 - seg(shred, 0.1, 0.4));
    }
    qa("[data-strip]").forEach((el, i) => {
      const l = inOutCubic(seg(shred, i * 0.05, i * 0.05 + 0.6)), dir = i % 2 ? 1 : -1;
      el.style.transform = `translate(${dir * l * (40 + i * 7)}%, ${l * (30 + i * 14)}px) rotate(${dir * l * (6 + i)}deg)`;
      el.style.opacity = String(1 - seg(l, 0.4, 1));
    });
    qa("[data-tile]").forEach((el, j) => set(el, "--t", outExpo(seg(pv, 0.5 + j * 0.08, 0.64 + j * 0.08))));
    const count = q("[data-count]");
    if (count) count.textContent = Math.round(100 * seg(pv, 0.58, 0.8)) + "%";

    // 4 · features: a horizontal conveyor; each card settles as it enters
    const ft = q('[data-track="features"]'), row = q("[data-row]");
    if (ft && row && !reduced) {
      row.style.transform = `translateX(${-prog(ft) * travel}px)`;
      qa("[data-card]").forEach((c) => set(c, "--k", outCubic(clamp((vw * 0.94 - c.getBoundingClientRect().left) / (vw * 0.32)))));
    }

    // 5 · open source: strike the catches, flood the card, raise the lines
    const os = q('[data-track="oss"]'), o = prog(os);
    for (const [k, x, y] of [["--s1", 0.05, 0.15], ["--s2", 0.15, 0.25], ["--s3", 0.25, 0.35], ["--fl", 0.38, 0.54], ["--l1", 0.54, 0.62],
      ["--l2", 0.6, 0.68], ["--l3", 0.66, 0.74], ["--ob", 0.72, 0.84], ["--obt", 0.78, 0.9]] as const) set(os, k, outCubic(seg(o, x, y)));

    // 6 · get: the step rail fills; 7 · FAQ rules draw in; 8 · the founder's words sit up straight
    const steps = q("[data-steps]");
    if (steps) { const r = steps.getBoundingClientRect(); set(steps, "--g", reduced ? 1 : clamp((vh * 0.7 - r.top) / r.height)); }
    qa("[data-faq]").forEach((el) => set(el, "--q", reduced ? 1 : inOutCubic(clamp((vh * 0.95 - el.getBoundingClientRect().top) / (vh * 0.3)))));
    const founder = q("[data-founder]");
    if (founder) set(founder, "--fl", reduced ? 0 : 1 - inOutCubic(clamp((vh * 0.92 - founder.getBoundingClientRect().top) / (vh * 0.5))));
  }

  const lenis = reduced ? null : new Lenis({ lerp: 0.08, smoothWheel: true, syncTouch: true, anchors: true, autoRaf: true });
  const onResize = () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(layout, 80); };
  let resizeTimer: ReturnType<typeof setTimeout> | undefined;
  addEventListener("scroll", update, { passive: true });
  addEventListener("resize", onResize);
  layout();
  document.fonts?.ready.then(layout);

  return {
    relayout: layout,
    stop() {
      removeEventListener("scroll", update);
      removeEventListener("resize", onResize);
      clearTimeout(resizeTimer);
      lenis?.destroy();
    },
  };
}
