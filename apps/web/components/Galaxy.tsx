"use client";
import { Html, OrbitControls } from "@react-three/drei";
import { Canvas, useThree } from "@react-three/fiber";
import { useRouter } from "next/navigation";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import * as THREE from "three";
import { hasWebGL, type Tokens, useReducedMotion } from "@/lib/tokens";

export type GalaxyPoint = { id: string; x: number; y: number; z: number; band: "high" | "watch" | "healthy"; segment: string; size: number };
export type ColourMode = "risk" | "segment";

export function segmentColours(tokens: Tokens): Record<string, string> {
  const light = new THREE.Color(tokens.bg).getHSL({ h: 0, s: 0, l: 0 }).l > 0.5;
  return {
    Champions: tokens.cyan,
    Loyal: tokens.violet,
    "Can't lose": tokens.amber,
    "At risk": tokens.magenta,
    New: light ? "#047857" : "#34d399",
    Promising: light ? "#1d4ed8" : "#60a5fa",
    Hibernating: tokens.muted,
    "Needs attention": light ? "#c2410c" : "#fb923c",
  };
}

function Points({ points, tokens, mode, onHover }: { points: GalaxyPoint[]; tokens: Tokens; mode: ColourMode; onHover: (p: GalaxyPoint | null) => void }) {
  const ref = useRef<THREE.InstancedMesh>(null);
  const invalidate = useThree((s) => s.invalidate);
  const router = useRouter();
  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const seg = segmentColours(tokens);
    const band = { high: tokens.magenta, watch: tokens.amber, healthy: tokens.cyan };
    const dummy = new THREE.Object3D();
    const colour = new THREE.Color();
    points.forEach((p, i) => {
      dummy.position.set(p.x * 6, p.y * 4, p.z * 6);
      dummy.scale.setScalar(0.085 * p.size);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
      mesh.setColorAt(i, colour.set(mode === "risk" ? band[p.band] : seg[p.segment] ?? tokens.muted));
    });
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    invalidate();
  }, [points, tokens, mode, invalidate]);
  return (
    <instancedMesh
      ref={ref}
      args={[undefined, undefined, points.length]}
      onPointerMove={(e) => { e.stopPropagation(); if (e.instanceId != null) onHover(points[e.instanceId]); }}
      onPointerOut={() => onHover(null)}
      onClick={(e) => { e.stopPropagation(); if (e.instanceId != null) router.push(`/accounts?id=${points[e.instanceId].id}`); }}
    >
      <icosahedronGeometry args={[1, 1]} />
      <meshStandardMaterial roughness={0.25} metalness={0.2} emissiveIntensity={0.25} />
    </instancedMesh>
  );
}

function Axes({ tokens }: { tokens: Tokens }) {
  const style = { color: tokens.muted, fontSize: 11, whiteSpace: "nowrap" as const, fontFamily: "var(--font-mono)" };
  return (
    <>
      <gridHelper args={[14, 14, tokens.edge, tokens.edge]} position={[0, -4.3, 0]} />
      <Html position={[6.6, -4.3, 0]} style={style}>more recent →</Html>
      <Html position={[-6.4, 4.4, 0]} style={style}>↑ more purchase days</Html>
      <Html position={[0, -4.3, 6.8]} style={style}>higher net spend →</Html>
    </>
  );
}

export default function Galaxy({ points, tokens, mode }: { points: GalaxyPoint[]; tokens: Tokens; mode: ColourMode }) {
  const [hover, setHover] = useState<GalaxyPoint | null>(null);
  const [webgl, setWebgl] = useState(true);
  const reduced = useReducedMotion();
  useEffect(() => setWebgl(hasWebGL()), []);
  if (!webgl) return <p className="state">3D needs WebGL, which this browser doesn&apos;t provide. Use the segment table below.</p>;
  return (
    <div className="scene" style={{ height: 520 }} role="img" aria-label={`3D scatter of ${points.length} accounts by recency, purchase days and net spend. The segment table below has the same information.`}>
      <Canvas flat frameloop={reduced ? "demand" : "always"} dpr={[1, 1.5]} camera={{ position: [11, 7, 13], fov: 42 }} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.8} />
        <pointLight position={[8, 10, 8]} intensity={60} />
        <Points points={points} tokens={tokens} mode={mode} onHover={setHover} />
        <Axes tokens={tokens} />
        <OrbitControls enablePan={false} minDistance={8} maxDistance={30} autoRotate={!reduced && !hover} autoRotateSpeed={0.35} />
      </Canvas>
      {hover && (
        <div className="scene-tip glass">
          <strong>Account {hover.id}</strong> · {hover.segment}
          <br />Risk: {hover.band} · click to open
        </div>
      )}
    </div>
  );
}
