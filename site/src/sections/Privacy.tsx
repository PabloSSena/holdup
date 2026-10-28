import { useI18n } from "../i18n";

const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

/** The real calibration screen, looping beside the privacy promise. */
export function Privacy() {
  const { t } = useI18n();
  return (
    <section className="track privacy" id="privacy">
      <div className="stage">
        <div className="wrap privacy-grid">
          <div className="privacy-text">
            <h2 className="h2">{t("privacy.title")}</h2>
            <p className="privacy-body">{t("privacy.body")}</p>
            <p className="privacy-site">{t("privacy.site")}</p>
          </div>
          <video
            className="calibration"
            src={`${import.meta.env.BASE_URL}media/calibration.mp4`}
            aria-label={t("privacy.video")}
            autoPlay={!reduced}
            controls={reduced}
            muted
            loop
            playsInline
          />
        </div>
      </div>
    </section>
  );
}
