import { useEffect, useRef, useState } from "react";
import { useI18n } from "./i18n";
import { Faq } from "./sections/Faq";
import { Features } from "./sections/Features";
import { Footer } from "./sections/Footer";
import { Founder } from "./sections/Founder";
import { Get } from "./sections/Get";
import { Header } from "./sections/Header";
import { How } from "./sections/How";
import { Intro } from "./sections/Intro";
import { OpenSource } from "./sections/OpenSource";
import { Privacy } from "./sections/Privacy";
import { startStory, type Step } from "./story";

export function App() {
  const { t, lang } = useI18n();
  const root = useRef<HTMLDivElement>(null);
  const story = useRef<ReturnType<typeof startStory>>(null);
  const tRef = useRef(t);
  tRef.current = t;
  const [step, setStep] = useState<Step>(1);

  useEffect(() => {
    story.current = startStory(root.current!, () => tRef.current, setStep);
    return () => story.current?.stop();
  }, []);

  // New language, new letters and widths: measure again.
  useEffect(() => story.current?.relayout(), [lang]);

  return (
    <div className="root" ref={root}>
      <Header />
      <main>
        <Intro />
        <How step={step} />
        <Privacy />
        <Features />
        <OpenSource />
        <Get />
        <Faq />
        <Founder />
      </main>
      <Footer />
    </div>
  );
}
