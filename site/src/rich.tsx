import { Fragment } from "react";

/** Renders **bold** spans in a translated string, so the dictionaries stay plain text. */
export const rich = (text: string) =>
  text.split("**").map((part, i) => (i % 2 ? <strong key={i}>{part}</strong> : <Fragment key={i}>{part}</Fragment>));
