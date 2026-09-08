FROM node:22-alpine
RUN apk add --no-cache openssl libc6-compat
WORKDIR /app
COPY api/package.json api/package-lock.json ./api/
RUN cd api && npm ci
COPY src ./src
COPY api ./api
WORKDIR /app/api
RUN npx prisma generate
EXPOSE 8080
CMD ["sh", "-c", "npx prisma migrate deploy && npx tsx seed.ts && npx tsx server.ts"]
