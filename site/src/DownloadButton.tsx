import { useState } from "react";
import { useI18n } from "./i18n";
import { DOWNLOAD_URL } from "./links";
import { isWindows } from "./platform";

const onWindows = isWindows(navigator.userAgent);

export function DownloadIcon() {
  return (
    <svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true" style={{ fill: "none", stroke: "currentColor", strokeWidth: 2.2, strokeLinecap: "round", strokeLinejoin: "round" }}>
      <path d="M10 3v10M5.5 8.5 10 13l4.5-4.5M4 17h12" />
    </svg>
  );
}

/** "Download for Windows" on Windows; elsewhere the Windows-only note with a Copy link button. */
export function DownloadButton({ square = false }: { square?: boolean }) {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);

  if (onWindows)
    return (
      <a className={`download${square ? " download-square" : ""}`} href={DOWNLOAD_URL} data-goatcounter-click="download">
        <DownloadIcon />
        {t("download.button")}
      </a>
    );

  const copy = () => {
    navigator.clipboard?.writeText(location.href).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  };
  return (
    <div className={`not-windows${square ? " not-windows-square" : ""}`}>
      <p>{t("download.notWindows")}</p>
      <button type="button" onClick={copy} aria-live="polite">
        {t(copied ? "download.linkCopied" : "download.copyLink")}
      </button>
    </div>
  );
}
