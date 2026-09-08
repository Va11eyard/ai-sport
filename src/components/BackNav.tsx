"use client";

import { Button } from "@astryxdesign/core/Button";
import { Icon } from "@astryxdesign/core/Icon";
import { ArrowLeftIcon } from "@heroicons/react/24/outline";

export function BackNav({ href, label }: { href: string; label: string }) {
  return (
    <Button
      href={href}
      variant="ghost"
      size="lg"
      className="min-h-11"
      label={label}
      icon={<Icon icon={ArrowLeftIcon} size="sm" />}
    />
  );
}
