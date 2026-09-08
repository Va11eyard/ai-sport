-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateTable
CREATE TABLE "Athlete" (
    "id" TEXT NOT NULL,
    "lastName" TEXT NOT NULL,
    "firstName" TEXT NOT NULL,
    "position" TEXT NOT NULL,
    "previousInjury" BOOLEAN NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Athlete_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DailySnapshot" (
    "id" SERIAL NOT NULL,
    "athleteId" TEXT NOT NULL,
    "date" TEXT NOT NULL,
    "sleepHours" DOUBLE PRECISION NOT NULL,
    "restingHr" DOUBLE PRECISION NOT NULL,
    "hrvRmssd" DOUBLE PRECISION NOT NULL,
    "workload" DOUBLE PRECISION NOT NULL,
    "recovery" INTEGER NOT NULL,
    "readiness" INTEGER NOT NULL,
    "injuryRisk" INTEGER NOT NULL,
    "missedSession" BOOLEAN NOT NULL,

    CONSTRAINT "DailySnapshot_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Meta" (
    "id" INTEGER NOT NULL DEFAULT 1,
    "asOf" TEXT NOT NULL,
    "seedKey" TEXT NOT NULL,

    CONSTRAINT "Meta_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Athlete_position_idx" ON "Athlete"("position");

-- CreateIndex
CREATE INDEX "DailySnapshot_athleteId_idx" ON "DailySnapshot"("athleteId");

-- CreateIndex
CREATE INDEX "DailySnapshot_date_idx" ON "DailySnapshot"("date");

-- CreateIndex
CREATE UNIQUE INDEX "DailySnapshot_athleteId_date_key" ON "DailySnapshot"("athleteId", "date");

-- AddForeignKey
ALTER TABLE "DailySnapshot" ADD CONSTRAINT "DailySnapshot_athleteId_fkey" FOREIGN KEY ("athleteId") REFERENCES "Athlete"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
