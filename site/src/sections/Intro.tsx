import type { CSSProperties } from "react";
import { DownloadButton } from "../DownloadButton";
import { useI18n } from "../i18n";
import { RELEASE_NOTES_URL } from "../links";

/** The opening: the question alone on screen, which breaks apart letter by letter to reveal the hero. */
export function Intro() {
  const { t } = useI18n();
  const question = t("hero.eyebrow");
  const headline = t("hero.headline");
  let n = 0;
  return (
    <section className="track" data-track="intro" id="top">
      <div className="stage">
        <div className="glow glow-0" data-glow />
        <div className="glow glow-1" data-glow />
        <div className="hero">
          <div className="part eyebrow" data-part>
            <span className="dot" />
            <span>{question}</span>
          </div>
          <h1 className="part headline" data-part>
            <span className="headline-outline">{headline}</span>
            <span className="liq liq-1" data-liq aria-hidden="true"><span>{headline}</span></span>
            <span className="liq liq-2" data-liq aria-hidden="true"><span>{headline}</span></span>
          </h1>
          <p className="part subhead" data-part>{t("hero.subhead")}</p>
          <div className="part" data-part style={{ "--rise": "32px" } as CSSProperties}>
            <DownloadButton />
          </div>
          <div className="part facts" data-part>
            <span>{t("download.facts")}</span>
            <a href={RELEASE_NOTES_URL}>{t("download.releaseNotes")}</a>
          </div>
        </div>
        <div className="skew-line-box" aria-hidden="true">
          <div className="skew-line" data-skew>
            {question.split(" ").map((w, i) => (
              <span key={i}>
                {[...w].map((ch, j) => (
                  <span key={j} data-ch={n++} className={ch === "?" ? "q" : undefined}>{ch}</span>
                ))}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
