/** @type {import('next').NextConfig} */
const isStatic = process.env.NEXT_PUBLIC_STATIC === "1";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const nextConfig = {
  reactStrictMode: true,
  distDir: process.env.NEXT_DIST_DIR || ".next",
  ...(isStatic ? { output: "export", basePath, trailingSlash: true, images: { unoptimized: true } } : {}),
};
export default nextConfig;
