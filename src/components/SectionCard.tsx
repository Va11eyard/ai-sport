import { Card } from "@astryxdesign/core/Card";
import { Heading } from "@astryxdesign/core/Heading";
import { Layout, LayoutContent, LayoutHeader } from "@astryxdesign/core/Layout";
import type { ReactNode } from "react";

export function SectionCard({
  title,
  children,
  className,
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Card elevation="low" className={className}>
      <Layout
        height="auto"
        header={
          <LayoutHeader hasDivider>
            <Heading level={3}>{title}</Heading>
          </LayoutHeader>
        }
        content={<LayoutContent>{children}</LayoutContent>}
      />
    </Card>
  );
}
