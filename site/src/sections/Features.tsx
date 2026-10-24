import { useI18n } from "../i18n";
import { Media } from "../Media";

/** A horizontal conveyor of feature cards, moved by vertical scroll. */
export function Features() {
  const { t } = useI18n();
  return (
    <section className="track features" data-track="features" id="features">
      <div className="stage">
        <div className="wrap features-title">
          <h2 className="h2">{t("features.title")}</h2>
        </div>
        <div className="row" data-row>
          <article className="card" data-card>
            <span className="icon icon-target" aria-hidden="true"><span /></span>
            <h3>{t("features.baseline.title")}</h3>
            <p>{t("features.baseline.body")}</p>
          </article>
          <article className="card" data-card>
            <span className="icon icon-lean" aria-hidden="true"><span /><span /></span>
            <h3>{t("features.lean.title")}</h3>
            <p>{t("features.lean.body")}</p>
            <div className="lean-tags">
              <span className="tag-fw">{t("how.chip.forward")}</span>
              <span className="tag-sd">{t("features.lean.side")}</span>
            </div>
          </article>
          <article className="card" data-card>
            <span className="icon icon-slider" aria-hidden="true"><span /></span>
            <h3>{t("features.sensitivity.title")}</h3>
            <p>{t("features.sensitivity.body")}</p>
            <div className="segmented" aria-hidden="true">
              <span>{t("features.sensitivity.low")}</span>
              <span className="on">{t("features.sensitivity.medium")}</span>
              <span>{t("features.sensitivity.high")}</span>
            </div>
          </article>
          <article className="card" data-card>
            <span className="icon icon-pause" aria-hidden="true"><span /><span /></span>
            <h3>{t("features.pause.title")}</h3>
            <p>{t("features.pause.body")}</p>
          </article>
          <article className="card card-wide" data-card>
            <span className="icon icon-bars" aria-hidden="true">
              <span style={{ height: 9 }} /><span style={{ height: 16 }} /><span style={{ height: 12 }} /><span style={{ height: 18 }} />
            </span>
            <h3>{t("features.stats.title")}</h3>
            <p>{t("features.stats.body")}</p>
            <Media className="card-media" file="history.png" alt={t("features.stats.shot")} note="app window · 960×640" />
          </article>
          <article className="card card-wide" data-card>
            <span className="icon icon-tray" aria-hidden="true" />
            <h3>{t("features.quiet.title")}</h3>
            <p>{t("features.quiet.body")}</p>
            <Media className="card-media" file="today.png" alt={t("features.quiet.shot")} note="app window · 960×640" />
          </article>
        </div>
      </div>
    </section>
  );
}
