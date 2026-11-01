import Link from "next/link";

const base = process.env.NEXT_PUBLIC_BASE_PATH || "";

export default function NotFound() {
  return (
    <section className="glass split" style={{ padding: 24 }}>
      <div>
        <img className="only-dark art" src={`${base}/img/aur-23-not-found.webp`} alt="" />
        <img className="only-light art" src={`${base}/img/aur-23-not-found-light.webp`} alt="" />
      </div>
      <div className="grid" style={{ gap: 12, alignContent: "center" }}>
        <p className="eyebrow">Error 404</p>
        <h1>This page has lapsed.</h1>
        <p className="lede">The link may be old, or the page moved when the app grew. Nothing you saved is lost.</p>
        <div className="row" style={{ gap: 8 }}>
          <Link className="btn primary" href="/overview">Go to the overview</Link>
          <Link className="btn" href="/">Back to the home page</Link>
        </div>
      </div>
    </section>
  );
}
