import type { Metadata } from "next";
import { AmbientField } from "@/components/ambient-field";
import { AmbientMotionProvider } from "@/components/ambient-motion";
import "./globals.css";

export const metadata: Metadata = {
  title: "How to reverse engineer an ASIC without understanding the circuit",
  description:
    "Recovering a circuit from its physical layout, then using output-prefix search to solve Jane Street's ASIC puzzle.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        {/* Reserve the opening before hydration; without JavaScript, show the article. */}
        <script dangerouslySetInnerHTML={{ __html: `
          if ((!location.hash || location.hash === '#top') && window.scrollY <= 64 &&
              matchMedia('(min-height: 600px) and (prefers-reduced-motion: no-preference)').matches) {
            document.documentElement.setAttribute('data-entry-pending', '');
            document.documentElement.style.setProperty('--entry-page-width', document.documentElement.clientWidth + 'px');
          }
        ` }} />
      </head>
      <body>
        <AmbientMotionProvider>
          <AmbientField />
          {children}
        </AmbientMotionProvider>
      </body>
    </html>
  );
}
