import { GitHubIcon } from "../GitHubIcon";
import { useI18n } from "../i18n";
import { REPO_URL } from "../links";

export function Header() {
  const { t, lang, setLang } = useI18n();
  return (
    <header className="header" data-header>
      <div className="header-bg" />
      <div className="header-row">
        <a href="#top" className="brand">
          <span className="mark mark-30" aria-hidden="true" />
          Holdup
        </a>
        <nav className="nav">
          <a href="#how">{t("nav.howItWorks")}</a>
          <a href="#privacy">{t("nav.privacy")}</a>
          <a href="#faq">{t("nav.faq")}</a>
        </nav>
        <div className="header-end">
          <div className="lang" role="group" aria-label="Language">
            <button type="button" lang="en" aria-pressed={lang === "en"} onClick={() => setLang("en")}>EN</button>
            <button type="button" lang="pt-BR" aria-pressed={lang === "pt-BR"} onClick={() => setLang("pt-BR")}>PT</button>
          </div>
          <a className="icon-link" href={REPO_URL} aria-label={t("nav.github")}>
            <GitHubIcon />
          </a>
          <a className="pill-button" href="#get">{t("download.short")}</a>
        </div>
      </div>
    </header>
  );
}
