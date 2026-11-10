import { useI18n, type Key } from "../i18n";
import type { Step } from "../story";

const STEPS = [1, 2, 3, 4] as const;

/** The character calibrates, works, leans in until the Mirror pops up, and sits up again; story.ts animates it. */
export function How({ step }: { step: Step }) {
  const { t } = useI18n();
  const mirror = t("how.chip.forward");
  // The Mirror's label pill grows with its text (Portuguese runs longer).
  const pill = Math.max(38, mirror.length * 2.9 + 8);
  return (
    <section className="track how" data-track="how" id="how">
      <div className="stage">
        <div className="wrap how-grid">
          <div className="scene">
            <div className="scene-bar">
              <span className="chip" data-chip>{t("how.chip.calibration")}</span>
              <span className="timer" data-tmr>
                <span data-tmr-t />
                <span className="timer-track"><span data-tmr-b /></span>
              </span>
            </div>
            <svg viewBox="0 0 320 230" role="img" aria-label={t("how.sceneLabel")}>
              <rect x="10" y="218" width="300" height="2" rx="1" fill="var(--soft)" />
              <rect x="54" y="94" width="9" height="80" rx="4.5" fill="var(--soft)" />
              <rect x="58" y="164" width="76" height="9" rx="4.5" fill="var(--soft)" />
              <rect x="92" y="173" width="7" height="38" fill="var(--soft)" />
              <rect x="70" y="210" width="52" height="6" rx="3" fill="var(--soft)" />
              <rect x="166" y="150" width="146" height="7" rx="3.5" fill="var(--soft)" />
              <rect x="296" y="157" width="7" height="61" fill="var(--soft)" />
              <rect x="194" y="58" width="100" height="84" rx="6" fill="var(--ink)" />
              <rect x="199" y="63" width="90" height="72" rx="2" fill="var(--cd)" />
              <rect x="207" y="70" width="46" height="4" rx="2" fill="var(--soft)" />
              <rect x="207" y="78" width="70" height="3" rx="1.5" fill="var(--soft)" />
              <rect x="207" y="85" width="62" height="3" rx="1.5" fill="var(--soft)" />
              <rect x="207" y="92" width="66" height="3" rx="1.5" fill="var(--soft)" />
              <rect x="199" y="129" width="90" height="6" fill="var(--soft)" />
              <circle data-sv="led" cx="283" cy="132" r="1.8" style={{ fill: "var(--ac)" }} />
              <g data-sv="mirror" transform="translate(202 127) scale(0) translate(-202 -127)">
                <rect x="202" y="100" width="36" height="27" rx="2" fill="var(--sb)" stroke="var(--fw)" strokeWidth="2" />
                <path d="M211 127 Q213 118 223 118 Q231 118 232 127 Z" fill="var(--ink)" />
                <circle cx="225" cy="111.5" r="4.5" fill="var(--skin)" />
                <rect x="202" y="91" width={pill} height="8" rx="4" fill="var(--fw)" />
                <text x={202 + pill / 2} y="97" fill="var(--aci)" textAnchor="middle" style={{ font: "700 5.4px Figtree, sans-serif" }}>{mirror}</text>
              </g>
              <rect x="182" y="142" width="124" height="6" rx="3" fill="var(--ink)" />
              <path data-sv="ghostT" d="M99 158 L103 106" fill="none" stroke="var(--sd)" strokeWidth="30" strokeLinecap="round" style={{ opacity: 0 }} />
              <circle data-sv="ghostH" cx="106" cy="80" r="18.5" fill="none" stroke="var(--sd)" strokeWidth="1.5" strokeDasharray="3 2.5" style={{ opacity: 0 }} />
              <text data-sv="ghostL" x="62" y="60" fill="var(--sd)" style={{ font: "600 8px Figtree, sans-serif", opacity: 0 }}>{t("how.baseline")}</text>
              <path d="M100 160 L160 166" fill="none" stroke="var(--leg)" strokeWidth="18" strokeLinecap="round" />
              <path d="M160 166 L163 208" fill="none" stroke="var(--leg)" strokeWidth="15" strokeLinecap="round" />
              <path d="M162 212 L180 212" fill="none" stroke="var(--leg)" strokeWidth="8" strokeLinecap="round" />
              <path data-sv="torso" d="M99 158 L103 106" fill="none" stroke="var(--ink)" strokeWidth="26" strokeLinecap="round" />
              <g data-sv="head" transform="translate(106 80)">
                <circle r="16" fill="var(--skin)" />
                <path d="M-15 4 A16 16 0 0 1 8 -14" fill="none" stroke="var(--ink)" strokeWidth="7" strokeLinecap="round" />
              </g>
              <path data-sv="arm" d="M104 112 L125 144 L176 145" fill="none" stroke="var(--arm)" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" />
              <rect data-sv="scan" x="58" y="46" width="96" height="1.6" fill="var(--sd)" style={{ opacity: 0 }} />
            </svg>
          </div>
          <div className="how-text">
            <h2 className="h2">{t("how.title")}</h2>
            <ol className="steps">
              {STEPS.map((i) => (
                <li key={i} className={step === i ? "current" : undefined} aria-current={step === i ? "step" : undefined}>
                  <span className="num">{i}</span>
                  <div>
                    <h3>{t(`how.${i}.title` as Key)}</h3>
                    <p>{t(`how.${i}.body` as Key)}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>
        <p className="scroll-hint">
          <span>{t("how.scrollHint")}</span>
          <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">
            <path d="M3.5 6 8 10.5 12.5 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </p>
      </div>
    </section>
  );
}
