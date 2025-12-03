import React from "react";
import Navbar from "./Navbar"; // We'll make this next

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />
      <main>{children}</main>
    </div>
  );
}
