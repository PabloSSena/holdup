import { useState, type CSSProperties } from "react";
import { useI18n } from "../i18n";

// How far each word slumps before the card scrolls in (the design's weights, repeated for longer quotes).
const SLUMP = [0.5, 0.9, 0.6, 1, 0.7, 1, 0.8, 0.5, 0.9, 0.6, 1, 0.7, 0.5, 0.9, 0.6, 1, 0.8, 0.6, 0.9, 0.5, 1, 0.7, 0.9, 0.6, 0.8, 1, 0.9, 0.5, 0.7, 1, 0.6, 0.9, 0.7, 0.5, 1, 0.8];

export function Founder() {
  const { t } = useI18n();
  const [avatar, setAvatar] = useState(true);
  const words = `“${t("why.quote")}”`.split(" ");
  return (
    <section className="founder">
      <div className="narrow">
        <h2>{t("why.title")}</h2>
        <figure data-founder>
          <blockquote>
            {words.map((w, i) => (
              <span key={i} style={{ "--w": SLUMP[i % SLUMP.length] } as CSSProperties}>{w}</span>
            ))}
          </blockquote>
          <figcaption>
            {avatar ? (
              <span className="avatar"><img src={`${import.meta.env.BASE_URL}media/avatar.jpg`} alt="" onError={() => setAvatar(false)} /></span>
            ) : (
              <span className="avatar placeholder" aria-hidden="true">avatar</span>
            )}
            {t("why.author")}
          </figcaption>
        </figure>
      </div>
    </section>
  );
}
