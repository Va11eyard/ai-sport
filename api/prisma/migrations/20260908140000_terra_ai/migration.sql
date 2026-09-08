-- AlterTable
ALTER TABLE "Athlete" ADD COLUMN "terraUserId" TEXT,
ADD COLUMN "terraProvider" TEXT;

CREATE UNIQUE INDEX "Athlete_terraUserId_key" ON "Athlete"("terraUserId");

-- CreateTable
CREATE TABLE "AiAnalysis" (
    "id" SERIAL NOT NULL,
    "athleteId" TEXT NOT NULL,
    "date" TEXT NOT NULL,
    "bullets" TEXT NOT NULL,
    "model" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "AiAnalysis_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "AiAnalysis_athleteId_date_key" ON "AiAnalysis"("athleteId", "date");
CREATE INDEX "AiAnalysis_athleteId_idx" ON "AiAnalysis"("athleteId");

ALTER TABLE "AiAnalysis" ADD CONSTRAINT "AiAnalysis_athleteId_fkey" FOREIGN KEY ("athleteId") REFERENCES "Athlete"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
