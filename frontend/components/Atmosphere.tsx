"use client";

import { useEffect, useState } from "react";

export function Atmosphere({ variant = "default" }: { variant?: "default" | "hero" | "quiet" }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const handleVisibility = () => setVisible(document.visibilityState === "visible");
    document.addEventListener("visibilitychange", handleVisibility);
    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, []);

  return (
    <div className={`atmosphere atmosphere-${variant} ${visible ? "" : "atmosphere-paused"}`} aria-hidden="true">
      <div className="atmosphere-glow atmosphere-glow-one" />
      <div className="atmosphere-glow atmosphere-glow-two" />
      <div className="atmosphere-orbit atmosphere-orbit-one" />
      <div className="atmosphere-orbit atmosphere-orbit-two" />
      <div className="atmosphere-sphere atmosphere-sphere-one" />
      <div className="atmosphere-sphere atmosphere-sphere-two" />
      <div className="atmosphere-sphere atmosphere-sphere-three" />
      <div className="atmosphere-particles" />
    </div>
  );
}
