import { Heading } from "@astryxdesign/core/Heading";
import { Text } from "@astryxdesign/core/Text";
import { VStack } from "@astryxdesign/core/VStack";
import { BackNav } from "@/components/BackNav";
import { NewAthleteForm } from "@/components/NewAthleteForm";

export default function NewAthletePage() {
  return (
    <div className="page-shell max-w-[720px]">
      <VStack gap={6}>
        <VStack gap={3} hAlign="start">
          <BackNav href="/" label="Состав" />
          <Heading level={1}>Новый атлет</Heading>
          <Text type="supporting" display="block">
            Карточка в составе. Дневные измерения — на следующем экране.
          </Text>
        </VStack>
        <NewAthleteForm />
      </VStack>
    </div>
  );
}
