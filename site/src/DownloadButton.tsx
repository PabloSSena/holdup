import { useState } from "react";
import { useI18n, type Key } from "./i18n";
import { DOWNLOADS } from "./links";
import { detectPlatform, type Platform } from "./platform";

export const PLATFORM = detectPlatform(navigator.userAgent, navigator.maxTouchPoints);

type Link = { href: string; label: Key; click: string };

/** Each OS's main download, and the other build for the same OS. Browsers don't tell Apple Silicon from Intel (Safari
 * says Intel on both), so Apple Silicon, nearly every Mac sold since 2020, is the main one. */
const CHOICES: Record<Platform, { main: Link; other?: Link }> = {
  windows: { main: { href: DOWNLOADS.windows, label: "download.windows", click: "download" } },
  mac: {
    main: { href: DOWNLOADS.macAppleSilicon, label: "download.mac", click: "download-mac" },
    other: { href: DOWNLOADS.macIntel, label: "download.macIntel", click: "download-mac-intel" },
  },
  linux: {
    main: { href: DOWNLOADS.appImage, label: "download.linux", click: "download-appimage" },
    other: { href: DOWNLOADS.deb, label: "download.deb", click: "download-deb" },
  },
};

export function DownloadIcon() {
  return (
    <svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true" style={{ fill: "none", stroke: "currentColor", strokeWidth: 2.2, strokeLinecap: "round", strokeLinejoin: "round" }}>
      <path d="M10 3v10M5.5 8.5 10 13l4.5-4.5M4 17h12" />
    </svg>
  );
}

/** "Download for Windows / Mac / Linux" for the visitor's OS (plus the other Mac or Linux build); on phones, tablets
 * and Chromebooks, a note to open the page on a computer, with a Copy link button. */
export function DownloadButton({ square = false }: { square?: boolean }) {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);

  if (PLATFORM) {
    const { main, other } = CHOICES[PLATFORM];
    return (
      <div className="download-group">
        <a className={`download${square ? " download-square" : ""}`} href={main.href} data-goatcounter-click={main.click}>
          <DownloadIcon />
          {t(main.label)}
        </a>
        {other && (
          <a className="download-other" href={other.href} data-goatcounter-click={other.click}>
            {t(other.label)}
          </a>
        )}
      </div>
    );
  }

  const copy = () => {
    navigator.clipboard?.writeText(location.href).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  };
  return (
    <div className={`not-desktop${square ? " not-desktop-square" : ""}`}>
      <p>{t("download.notDesktop")}</p>
      <button type="button" onClick={copy} aria-live="polite">
        {t(copied ? "download.linkCopied" : "download.copyLink")}
      </button>
    </div>
  );
}
