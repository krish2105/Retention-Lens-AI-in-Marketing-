
/**
 * Arabic for the shell and the weekly-review screens (R8). Drafted by AI and marked for review by a
 * native speaker before any UAE pilot; untranslated strings fall back to English.
 */
const AR: Record<string, string> = {
  Overview: "نظرة عامة",
  "This week": "هذا الأسبوع",
  Accounts: "الحسابات",
  Segments: "الشرائح",
  Signals: "الإشارات",
  "Outreach studio": "استوديو التواصل",
  "Product lab": "مختبر المنتجات",
  "Model lab": "مختبر النماذج",
  Data: "البيانات",
  "Upload data": "رفع البيانات",
  "Course evidence": "أدلة المقرر",
  Workspace: "مساحة العمل",
  Team: "الفريق",
  "Privacy & data": "الخصوصية والبيانات",
  "Plan & billing": "الخطة والفوترة",
  Settings: "الإعدادات",
  "Skip to content": "انتقل إلى المحتوى",
  "Sign out": "تسجيل الخروج",
  "Decision support only. Nothing is sent without your approval.": "أداة لدعم القرار فقط. لا يُرسل أي شيء دون موافقتك.",
  Light: "فاتح",
  Dark: "داكن",
  System: "النظام",
  "This week's review queue.": "قائمة مراجعة هذا الأسبوع.",
  "The accounts with the most spend at risk, in order. Open each one, read the evidence and record a decision. A random share is held out each week so the effect of contacting accounts can be measured.":
    "الحسابات الأكثر عرضة لخسارة الإنفاق، مرتبة. افتح كل حساب واقرأ الأدلة وسجّل قرارك. تُستبعد نسبة عشوائية كل أسبوع لقياس أثر التواصل مع الحسابات.",
  reviewed: "تمت مراجعتها",
  "at risk": "معرّض للخطر",
  "Is outreach working?": "هل يُجدي التواصل؟",
  "Score your own invoices.": "قيّم فواتيرك بنفسك.",
  "Drop a .csv or .xlsx file here": "أفلت ملف ‎.csv أو ‎.xlsx هنا",
  "Choose a file": "اختر ملفًا",
  "Quick tour": "جولة سريعة",
  "Skip tour": "تخطي الجولة",
  Next: "التالي",
  Back: "السابق",
  Done: "تم",
};

/** Translates only after the shell has set <html lang> on the client, so server and first client render match. */
export function t(text: string): string {
  return typeof document !== "undefined" && document.documentElement.lang === "ar-AE" ? AR[text] ?? text : text;
}
