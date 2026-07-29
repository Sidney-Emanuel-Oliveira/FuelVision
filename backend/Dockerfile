FROM maven:3.9-eclipse-temurin-21-alpine AS builder

WORKDIR /build

COPY backend/pom.xml ./backend/pom.xml
COPY backend/src ./backend/src
RUN mvn -f backend/pom.xml package -DskipTests

FROM eclipse-temurin:25-jre-alpine

WORKDIR /app

RUN addgroup -S fuelvision \
    && adduser -S -G fuelvision -u 10001 fuelvision

COPY --from=builder \
    /build/backend/target/fuelvision-backend-0.0.1-SNAPSHOT.jar \
    /app/fuelvision-backend.jar

USER fuelvision

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=9 \
    CMD wget -q -O - http://127.0.0.1:8080/actuator/health | grep -q '"status":"UP"' \
        && wget -q -O /dev/null http://127.0.0.1:8080/api/predictions/model \
        || exit 1

ENTRYPOINT ["java", "-jar", "/app/fuelvision-backend.jar"]
