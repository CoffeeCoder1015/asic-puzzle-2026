"use client";

import { useEffect, useState, type ReactNode } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export function Disclosure({
  title,
  children,
  className,
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  // Evidence is expanded in the server document, including when JavaScript is unavailable.
  const [value, setValue] = useState("evidence");
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setValue("");
    setMounted(true);
  }, []);

  return (
    <Accordion
      type="single"
      collapsible
      value={value}
      onValueChange={setValue}
      className={className}
    >
      <AccordionItem value="evidence">
        <AccordionTrigger disabled={!mounted}>{title}</AccordionTrigger>
        <AccordionContent forceMount>{children}</AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
