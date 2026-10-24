import { DownloadButton } from "../DownloadButton";
import { useI18n, type Key } from "../i18n";
import { Media } from "../Media";
import { rich } from "../rich";

const STEPS = ["get.1", "get.2", "get.3", "get.4"] as const satisfies readonly Key[];

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
          <figure className="smartscreen">
            <Media file="smartscreen.png" alt={t("get.shot")} note="“Windows protected your PC” after More info" />
            <figcaption>{rich(t("get.caption"))}</figcaption>
          </figure>
        </div>
        <p className="requirements">{t("get.requirements")}</p>
      </div>
    </section>
  );
}
