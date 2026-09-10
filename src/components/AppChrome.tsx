"use client";

import { Suspense } from "react";
import { usePathname } from "next/navigation";
import { AppShell } from "@astryxdesign/core/AppShell";
import { Button } from "@astryxdesign/core/Button";
import { Icon } from "@astryxdesign/core/Icon";
import { TopNav, TopNavHeading, TopNavItem } from "@astryxdesign/core/TopNav";
import { PlusIcon } from "@heroicons/react/24/outline";

export function AppChrome({ children }: { children: React.ReactNode }) {
  return (
    <AppShell
      variant="elevated"
      height="auto"
      contentPadding={0}
      mobileNav={false}
      topNav={
        <Suspense fallback={<ChromeNav selected={false} />}>
          <ChromeNavWithPath />
        </Suspense>
      }
    >
      {children}
    </AppShell>
  );
}

function ChromeNavWithPath() {
  const path = usePathname();
  return <ChromeNav selected={path === "/"} />;
}

function ChromeNav({ selected }: { selected: boolean }) {
  return (
    <TopNav
      label="Основная навигация"
      heading={
        <TopNavHeading
          heading="Сборная"
          superheading="сегодня"
          headingHref="/"
        />
      }
      startContent={
        <TopNavItem label="Сегодня" href="/" isSelected={selected} />
      }
      endContent={
        <Button
          href="/athletes/new"
          label="Новый атлет"
          size="lg"
          variant="ghost"
          className="min-h-11"
          icon={<Icon icon={PlusIcon} size="sm" />}
        />
      }
    />
  );
}
