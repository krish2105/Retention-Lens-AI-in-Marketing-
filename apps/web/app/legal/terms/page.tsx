export const metadata = { title: "Terms · RetentionLens" };

export default function Terms() {
  return (
    <article className="glass panel prose">
      <p className="eyebrow">Draft pilot terms · last updated 1 November 2026 · not legal advice</p>
      <h1>Terms of use</h1>
      <p>These draft terms describe how the RetentionLens pilot works. They will be reviewed by a qualified person before any paid service starts.</p>
      <h2>The service</h2>
      <ul>
        <li>RetentionLens is decision support. Scores are estimates with stated uncertainty; your team decides what to do.</li>
        <li>The pilot is free for four weeks and is provided as-is, without warranties of fitness for a particular purpose.</li>
        <li>Paid plans shown on the pricing page are a hypothesis. Checkout runs in Stripe test mode; no real payment is taken in this build.</li>
      </ul>
      <h2>Your responsibilities</h2>
      <ul>
        <li>Only upload data you are allowed to process, and keep your customers&apos; consent and opt-out records.</li>
        <li>Review every message before it is used. Do not use RetentionLens to send unsolicited marketing that breaks PECR or local law.</li>
        <li>Keep your password private and remove people who should no longer have access.</li>
      </ul>
      <h2>Our responsibilities</h2>
      <ul>
        <li>Keep each company&apos;s data separate from every other company&apos;s data.</li>
        <li>Let workspace owners export and delete their data at any time.</li>
        <li>Tell pilot customers promptly about any security incident affecting their data.</li>
      </ul>
      <h2>Ending the pilot</h2>
      <p>Either side can end the pilot at any time. On ending, you can export your data; we delete the workspace within 30 days unless you ask us to keep it.</p>
    </article>
  );
}
