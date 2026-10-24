import { useI18n } from "../i18n";

const STRIPS = [0, 1, 2, 3, 4, 5, 6, 7];

/** A camera frame is scanned for posture points, shredded, and the privacy numbers count in behind it. */
export function Privacy() {
  const { t } = useI18n();
  return (
    <section className="track privacy" data-track="privacy" id="privacy">
      <div className="stage">
        <div className="wrap privacy-grid">
          <div className="privacy-text">
            <h2 className="h2">{t("privacy.title")}</h2>
            <p className="privacy-body">{t("privacy.body")}</p>
            <p className="privacy-site">{t("privacy.site")}</p>
          </div>
          <div className="vault">
            <div className="tiles">
              <div className="tile" data-tile><b>0</b><span>{t("privacy.stat.images")}</span></div>
              <div className="tile" data-tile><b data-count>100%</b><span>{t("privacy.stat.local")}</span></div>
              <div className="tile" data-tile><b>0</b><span>{t("privacy.stat.accounts")}</span></div>
              <div className="tile" data-tile><b>{t("privacy.stat.offlineValue")}</b><span>{t("privacy.stat.offline")}</span></div>
            </div>
            <div className="frame" aria-hidden="true">
              {STRIPS.map((i) => (
                <div key={i} className="strip" data-strip style={{ top: `${i * 12.5}%` }}>
                  <div style={{ top: `${-i * 100}%` }}>
                    <span className="face" />
                    <span className="body" />
                  </div>
                </div>
              ))}
              <div className="frame-label" data-flabel />
              <span className="kp" data-kp="0.34" style={{ left: "50%", top: "34%" }} />
              <span className="kp" data-kp="0.64" style={{ left: "31%", top: "64%" }} />
              <span className="kp" data-kp="0.64" style={{ left: "69%", top: "64%" }} />
              <span className="kp-line" data-kp="0.66" />
              <div className="scan-line" data-scan />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
