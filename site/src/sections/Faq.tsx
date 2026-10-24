import { useI18n, type Key } from "../i18n";

const QUESTIONS = ["record", "internet", "warning", "others", "calls", "mac", "free", "uninstall"];

export function Faq() {
  const { t } = useI18n();
  return (
    <section className="faq" id="faq">
      <div className="narrow">
        <h2 className="h2">{t("faq.title")}</h2>
        {QUESTIONS.map((id, i) => (
          <div key={id} data-faq>
            <div className="faq-rule" />
            <details open={i === 0}>
              <summary>
                <span>{t(`faq.${id}.q` as Key)}</span>
                <span className="plus" aria-hidden="true">+</span>
              </summary>
              <p>{t(`faq.${id}.a` as Key)}</p>
            </details>
          </div>
        ))}
        <div className="faq-end" />
      </div>
    </section>
  );
}
