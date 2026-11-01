import Link from "next/link";

export const metadata = { title: "Privacy notice · RetentionLens" };

export default function PrivacyNotice() {
  return (
    <article className="glass panel prose">
      <p className="eyebrow">Draft for the pilot · last updated 1 November 2026 · not legal advice</p>
      <h1>Privacy notice</h1>
      <p>RetentionLens is a student project (MAIB AI 208) being prepared for a pilot. This notice explains what personal data it handles. It is written for UK GDPR, the UK Privacy and Electronic Communications Regulations (PECR) and the UAE Personal Data Protection Law (PDPL). It will be reviewed by a qualified person before any paid service starts.</p>
      <h2>Who is responsible</h2>
      <ul>
        <li><strong>Waitlist and accounts:</strong> the RetentionLens project is the controller for the email, name, company and role you give us.</li>
        <li><strong>Your invoice data:</strong> your company is the controller. RetentionLens processes it only on your instructions, under a data processing agreement (template in the repository).</li>
      </ul>
      <h2>What we collect and why</h2>
      <ul>
        <li><strong>Waitlist:</strong> work email, company, role, size band and the time you agreed. Lawful basis: consent. Used only to contact you about the pilot.</li>
        <li><strong>Sign-in:</strong> name, email, a scrypt hash of your password and session records. Lawful basis: contract.</li>
        <li><strong>Uploaded invoices:</strong> customer account IDs, invoice lines, dates and countries. Used only to score your accounts inside your workspace.</li>
        <li><strong>Server logs:</strong> request time, route, status and duration, with no request bodies. Kept for security and reliability.</li>
      </ul>
      <h2>What we do not do</h2>
      <ul>
        <li>We do not sell data or use it for advertising.</li>
        <li>We do not train shared models on your data. Models are fitted per upload, inside your workspace.</li>
        <li>We do not send emails to your customers. Drafts are approved by your team and exported to your own systems, so your consent records and unsubscribe handling stay with you.</li>
        <li>Prompts to the AI model contain structured account facts only, and run on our server rather than a third-party chat service.</li>
      </ul>
      <h2>How long we keep it</h2>
      <p>Until you delete the upload or the workspace, or one year after your last sign-in, whichever is sooner. Waitlist entries are deleted 12 months after the pilot launches or when you ask.</p>
      <h2>Your rights</h2>
      <p>You can access, correct, export and erase your data. Workspace owners can export everything and delete the whole workspace from <Link href="/privacy">Privacy and data</Link>. For anything else, contact the project owner through the GitHub repository. You may complain to the UK ICO or, in the UAE, the UAE Data Office.</p>
      <h2>Where data is stored</h2>
      <p>In the pilot, data is stored in the region of the hosting provider chosen for that pilot and named in its data processing agreement. Cross-border transfers are covered by that agreement.</p>
    </article>
  );
}
