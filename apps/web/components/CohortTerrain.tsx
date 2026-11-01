"use client";
import { Html, OrbitControls } from "@react-three/drei";
import { Canvas, useThree } from "@react-three/fiber";
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import type { Cohort } from "@/lib/api";
import { hasWebGL, type Tokens, useReducedMotion } from "@/lib/tokens";

type Cell = { cohort: string; size: number; month: number; retention: number; c: number };

function cellsFrom(cohorts: Cohort[]): Cell[] {
  // Month 0 is always 100%, so the terrain starts at month 1 to keep the shape readable.
  return cohorts.flatMap((co, c) => co.retention.slice(1).map((retention, i) => ({ cohort: co.cohort, size: co.size, month: i + 1, retention, c })));
}

function mix(tokens: Tokens, t: number): THREE.Color {
  const low = new THREE.Color(tokens.magenta), mid = new THREE.Color(tokens.amber), high = new THREE.Color(tokens.cyan);
  return t < 0.5 ? low.lerp(mid, t / 0.5) : mid.lerp(high, (t - 0.5) / 0.5);
}

function Bars({ cells, tokens, onHover }: { cells: Cell[]; tokens: Tokens; onHover: (c: Cell | null) => void }) {
  const ref = useRef<THREE.InstancedMesh>(null);
  const invalidate = useThree((s) => s.invalidate);
  const max = useMemo(() => Math.max(0.01, ...cells.map((c) => c.retention)), [cells]);
  const months = useMemo(() => Math.max(...cells.map((c) => c.month)), [cells]);
  const cohorts = useMemo(() => Math.max(...cells.map((c) => c.c)) + 1, [cells]);

  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const dummy = new THREE.Object3D();
    cells.forEach((cell, i) => {
      const t = cell.retention / max;
      const h = Math.max(0.05, t * 5);
      dummy.position.set(cell.month - months / 2, h / 2, cell.c - cohorts / 2);
      dummy.scale.set(0.84, h, 0.84);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
      mesh.setColorAt(i, mix(tokens, t));
    });
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    invalidate();
  }, [cells, tokens, max, months, cohorts, invalidate]);

  return (
    <>
      <instancedMesh
        ref={ref}
        args={[undefined, undefined, cells.length]}
        onPointerMove={(e) => {
          e.stopPropagation();
          if (e.instanceId != null) onHover(cells[e.instanceId]);
        }}
        onPointerOut={() => onHover(null)}
      >
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial roughness={0.32} metalness={0.15} />
      </instancedMesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0.5, -0.01, -0.5]}>
        <planeGeometry args={[months + 2, cohorts + 2]} />
        <meshBasicMaterial color={tokens.violet} transparent opacity={0.07} />
      </mesh>
      <Html position={[0, -0.2, cohorts / 2 + 1.6]} center style={{ color: tokens.muted, fontSize: 11, whiteSpace: "nowrap", fontFamily: "var(--font-mono)" }}>
        months since first order →
      </Html>
      <Html position={[-months / 2 - 1.8, -0.2, 0]} center style={{ color: tokens.muted, fontSize: 11, whiteSpace: "nowrap", fontFamily: "var(--font-mono)" }}>
        ← first-order month
      </Html>
    </>
  );
}

export default function CohortTerrain({ cohorts, tokens }: { cohorts: Cohort[]; tokens: Tokens }) {
  const cells = useMemo(() => cellsFrom(cohorts), [cohorts]);
  const [hover, setHover] = useState<Cell | null>(null);
  const [webgl, setWebgl] = useState(true);
  const reduced = useReducedMotion();
  useEffect(() => setWebgl(hasWebGL()), []);

  if (!webgl) {
    return <p className="state">3D needs WebGL, which this browser doesn&apos;t provide. The same data is in the table below.</p>;
  }
  return (
    <div className="scene" role="img" aria-label="3D chart of monthly repeat-purchase rate by first-order cohort. A table version follows.">
      <Canvas flat frameloop="demand" dpr={[1, 1.5]} camera={{ position: [18, 15, 24], fov: 36 }} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[10, 20, 12]} intensity={1.5} />
        <directionalLight position={[-12, 8, -10]} intensity={0.4} color={tokens.violet} />
        <Bars cells={cells} tokens={tokens} onHover={setHover} />
        <OrbitControls enablePan={false} minDistance={14} maxDistance={48} maxPolarAngle={Math.PI / 2.15} enableDamping={!reduced} />
      </Canvas>
      {hover && (
        <div className="scene-tip glass">
          <strong>{hover.cohort} cohort</strong> · {hover.size} customers
          <br />
          Month {hover.month}: <span className="mono">{(hover.retention * 100).toFixed(1)}%</span> bought again
        </div>
      )}
    </div>
  );
}
