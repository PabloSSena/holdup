import { useState } from "react";

type Props = { file: string; alt: string; note: string; className?: string };

/** A capture from site/public/media/; until the file is dropped in, the design's striped placeholder shows instead. */
export function Media({ file, alt, note, className = "" }: Props) {
  const [missing, setMissing] = useState(false);
  if (missing)
    return (
      <div className={`placeholder ${className}`} role="img" aria-label={alt}>
        <strong>{file}</strong>
        <span>{note}</span>
      </div>
    );
  return <img className={`shot ${className}`} src={`${import.meta.env.BASE_URL}media/${file}`} alt={alt} loading="lazy" onError={() => setMissing(true)} />;
}
