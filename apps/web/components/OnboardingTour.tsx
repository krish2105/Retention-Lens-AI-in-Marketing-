"use client";
import { useEffect, useState } from "react";
import { t } from "@/lib/i18n";

const STEPS = [
  { target: "queue", title: "Start with this week", body: "Each Monday the queue lists the accounts with the most spend at risk. A random fifth are held out so you can measure whether contacting accounts works." },
  { target: "accounts", title: "Check the evidence", body: "Open any account to see its lapse risk, expected spend with a range, and the plain-language reasons behind the score." },
  { target: "outreach", title: "Approve every message", body: "The local AI drafts a check-in from the account's facts only. Automatic checks and a consent rule run before you can approve. Nothing is sent from here." },
  { target: "upload", title: "Use your own invoices", body: "Upload a CSV or Excel export. You map the columns, see every rejected row, and get a scored queue in minutes." },
];
const KEY = "rl-tour-done";

/** A short, skippable, non-modal tour on the first visit. It never blocks the page. */
export function OnboardingTour() {
  const [step, setStep] = useState<number | null>(null);
  useEffect(() => {
    try {
      if (!window.localStorage.getItem(KEY)) setStep(0);
    } catch {}
  }, []);
  useEffect(() => {
    document.querySelectorAll("[data-tour-active]").forEach((el) => el.removeAttribute("data-tour-active"));
    if (step != null) document.querySelector(`[data-tour="${STEPS[step].target}"]`)?.setAttribute("data-tour-active", "true");
  }, [step]);
  if (step == null) return null;
  const finish = () => {
    try {
      window.localStorage.setItem(KEY, "1");
    } catch {}
    setStep(null);
  };
  const s = STEPS[step];
  return (
    <aside className="tour glass" role="dialog" aria-modal="false" aria-labelledby="tour-title">
      <p className="eyebrow">{t("Quick tour")} · {step + 1} / {STEPS.length}</p>
      <h2 id="tour-title">{s.title}</h2>
      <p>{s.body}</p>
      <div className="row" style={{ gap: 8, justifyContent: "space-between", alignItems: "center" }}>
        <button type="button" className="btn" onClick={finish}>{t("Skip tour")}</button>
        <div className="row" style={{ gap: 8 }}>
          {step > 0 && <button type="button" className="btn" onClick={() => setStep(step - 1)}>{t("Back")}</button>}
          <button type="button" className="btn primary" onClick={() => (step === STEPS.length - 1 ? finish() : setStep(step + 1))}>
            {step === STEPS.length - 1 ? t("Done") : t("Next")}
          </button>
        </div>
      </div>
    </aside>
  );
}

export function resetTour() {
  try {
    window.localStorage.removeItem(KEY);
  } catch {}
}
