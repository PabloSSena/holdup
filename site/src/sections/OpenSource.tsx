import { GitHubIcon } from "../GitHubIcon";
import { useI18n } from "../i18n";
import { REPO_URL } from "../links";

/** Subscription, account and ads get struck through; then "Free. Open source. No catch." rises in. */
export function OpenSource() {
  const { t } = useI18n();
  return (
    <section className="track oss" data-track="oss">
      <div className="stage">
        <div className="oss-box">
          <ul className="catches" aria-hidden="true">
            <li>{t("open.strike.1")}</li>
            <li>{t("open.strike.2")}</li>
            <li>{t("open.strike.3")}</li>
          </ul>
          <div className="oss-card">
            <span className="badge">{t("footer.license")}</span>
            <h2 className="oss-title">
              <span><span>{t("open.line1")}</span></span>
              <span><span>{t("open.line2")}</span></span>
              <span><span>{t("open.line3")}</span></span>
            </h2>
            <div className="oss-foot">
              <p>{t("open.body")}</p>
              <a className="gh-button" href={REPO_URL}>
                <GitHubIcon />
                {t("open.button")}
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
