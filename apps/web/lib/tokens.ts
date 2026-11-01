"use client";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export type Tokens = { ink: string; muted: string; edge: string; cyan: string; magenta: string; amber: string; violet: string; bg: string };

const FALLBACK: Tokens = { ink: "#eef0ff", muted: "#a7adc8", edge: "#2a2d40", cyan: "#67e8f9", magenta: "#f472b6", amber: "#fbbf24", violet: "#a78bfa", bg: "#070912" };

/** Resolved theme colours for canvas and SVG charts, which can't read CSS variables directly. */
export function useTokens(): Tokens {
  const { resolvedTheme } = useTheme();
  const [tokens, setTokens] = useState<Tokens>(FALLBACK);
  useEffect(() => {
    const read = () => {
      const style = getComputedStyle(document.documentElement);
      const get = (name: string) => style.getPropertyValue(`--${name}`).trim();
      setTokens({ ink: get("ink"), muted: get("muted"), edge: get("edge-strong"), cyan: get("cyan"), magenta: get("magenta"), amber: get("amber"), violet: get("violet"), bg: get("bg") });
    };
    read();
    // next-themes may flip data-theme after this effect; re-read whenever the attribute changes.
    const observer = new MutationObserver(read);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class", "style"] });
    return () => observer.disconnect();
  }, [resolvedTheme]);
  return tokens;
}

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(media.matches);
    const on = () => setReduced(media.matches);
    media.addEventListener("change", on);
    return () => media.removeEventListener("change", on);
  }, []);
  return reduced;
}

export function hasWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}
