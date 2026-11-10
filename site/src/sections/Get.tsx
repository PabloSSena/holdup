import { DownloadButton, PLATFORM } from "../DownloadButton";
import { useI18n, type Key } from "../i18n";
import { rich } from "../rich";

// The visitor's OS's steps; on a phone or tablet the Windows ones, the most common computer.
const OS = PLATFORM ?? "windows";
const STEPS = [`get.${OS}.1`, `get.${OS}.2`, `get.${OS}.3`, "get.done"] as const satisfies readonly Key[];

export function Get() {
  const { t } = useI18n();
  return (
    <section className="get" id="get">
      <div className="wrap">
        <div className="get-head">
          <h2>{t("get.title")}</h2>
          <DownloadButton square />
        </div>
        <div className="get-grid">
          <ol className="rail" data-steps>
            {STEPS.map((key, i) => (
              <li key={key}>
                <span className="n">{i + 1}</span>
                <span>{rich(t(key))}</span>
              </li>
            ))}
          </ol>

        </div>
        <p className="requirements">{t(`get.${OS}.requirements`)}</p>
      </div>
    </section>
  );
}
