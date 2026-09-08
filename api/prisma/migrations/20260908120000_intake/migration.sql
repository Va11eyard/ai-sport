-- AlterTable
ALTER TABLE "DailySnapshot" ADD COLUMN "respRate" DOUBLE PRECISION,
ADD COLUMN "temperature" DOUBLE PRECISION,
ADD COLUMN "weightKg" DOUBLE PRECISION,
ADD COLUMN "bodyFatPct" DOUBLE PRECISION,
ADD COLUMN "muscleMassKg" DOUBLE PRECISION,
ADD COLUMN "sleepEfficiency" DOUBLE PRECISION,
ADD COLUMN "remHours" DOUBLE PRECISION,
ADD COLUMN "deepHours" DOUBLE PRECISION,
ADD COLUMN "awakenings" INTEGER,
ADD COLUMN "sleepLatencyMin" DOUBLE PRECISION,
ADD COLUMN "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- CreateTable
CREATE TABLE "LabPanel" (
    "id" SERIAL NOT NULL,
    "athleteId" TEXT NOT NULL,
    "date" TEXT NOT NULL,
    "hemoglobin" DOUBLE PRECISION,
    "vitaminD" DOUBLE PRECISION,
    "ferritin" DOUBLE PRECISION,
    "iron" DOUBLE PRECISION,
    "testosterone" DOUBLE PRECISION,
    "cortisol" DOUBLE PRECISION,
    "igf1" DOUBLE PRECISION,
    "ck" DOUBLE PRECISION,
    "crp" DOUBLE PRECISION,
    "lactate" DOUBLE PRECISION,
    "vo2max" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "LabPanel_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PsychCheckin" (
    "id" SERIAL NOT NULL,
    "athleteId" TEXT NOT NULL,
    "date" TEXT NOT NULL,
    "stress" INTEGER NOT NULL,
    "motivation" INTEGER NOT NULL,
    "anxiety" INTEGER NOT NULL,
    "burnout" INTEGER NOT NULL,
    "mood" INTEGER NOT NULL,
    "cognitive" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "PsychCheckin_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "NutritionDay" (
    "id" SERIAL NOT NULL,
    "athleteId" TEXT NOT NULL,
    "date" TEXT NOT NULL,
    "kcal" DOUBLE PRECISION NOT NULL,
    "proteinG" DOUBLE PRECISION NOT NULL,
    "carbsG" DOUBLE PRECISION NOT NULL,
    "fatG" DOUBLE PRECISION NOT NULL,
    "waterL" DOUBLE PRECISION NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "NutritionDay_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TrainingSession" (
    "id" SERIAL NOT NULL,
    "athleteId" TEXT NOT NULL,
    "date" TEXT NOT NULL,
    "distanceM" DOUBLE PRECISION,
    "speedAvg" DOUBLE PRECISION,
    "accelerations" INTEGER,
    "shots" INTEGER,
    "throwPower" DOUBLE PRECISION,
    "powerWatts" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "TrainingSession_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "LabPanel_athleteId_date_key" ON "LabPanel"("athleteId", "date");
CREATE INDEX "LabPanel_athleteId_idx" ON "LabPanel"("athleteId");
CREATE UNIQUE INDEX "PsychCheckin_athleteId_date_key" ON "PsychCheckin"("athleteId", "date");
CREATE INDEX "PsychCheckin_athleteId_idx" ON "PsychCheckin"("athleteId");
CREATE UNIQUE INDEX "NutritionDay_athleteId_date_key" ON "NutritionDay"("athleteId", "date");
CREATE INDEX "NutritionDay_athleteId_idx" ON "NutritionDay"("athleteId");
CREATE UNIQUE INDEX "TrainingSession_athleteId_date_key" ON "TrainingSession"("athleteId", "date");
CREATE INDEX "TrainingSession_athleteId_idx" ON "TrainingSession"("athleteId");

-- AddForeignKey
ALTER TABLE "LabPanel" ADD CONSTRAINT "LabPanel_athleteId_fkey" FOREIGN KEY ("athleteId") REFERENCES "Athlete"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "PsychCheckin" ADD CONSTRAINT "PsychCheckin_athleteId_fkey" FOREIGN KEY ("athleteId") REFERENCES "Athlete"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "NutritionDay" ADD CONSTRAINT "NutritionDay_athleteId_fkey" FOREIGN KEY ("athleteId") REFERENCES "Athlete"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "TrainingSession" ADD CONSTRAINT "TrainingSession_athleteId_fkey" FOREIGN KEY ("athleteId") REFERENCES "Athlete"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
