import { Suspense } from "react";
import { Dashboard } from "../components/dashboard";

export default function Home() {
  return <Suspense fallback={<main className="shell"><p>Loading Coinwise…</p></main>}><Dashboard /></Suspense>;
}

