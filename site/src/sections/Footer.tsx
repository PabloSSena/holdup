import { useI18n } from "../i18n";
import { RELEASE_NOTES_URL, REPO_URL } from "../links";

export function Footer() {
  const { t } = useI18n();
  return (
    <footer className="footer">
      <div className="footer-row">
        <div className="footer-links">
          <span className="brand"><span className="mark mark-22" aria-hidden="true" />Holdup</span>
          <a href={`${REPO_URL}/blob/main/LICENSE`}>{t("footer.license")}</a>
          <a href={REPO_URL}>GitHub</a>
          <a href={RELEASE_NOTES_URL}>{t("download.releaseNotes")}</a>
        </div>
        <span className="signoff">{t("footer.signoff")}</span>
      </div>
    </footer>
  );
}
