FROM eclipse-temurin:17-jdk AS build
WORKDIR /app
COPY . .
RUN ./gradlew bootJar

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/build/libs/*-SNAPSHOT.jar app.jar
# кладём агента прямо в образ (можно скачать заранее или ADD)
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v1.33.6/opentelemetry-javaagent.jar /otel/opentelemetry-javaagent.jar
EXPOSE 8080
ENTRYPOINT ["java", "-javaagent:/otel/opentelemetry-javaagent.jar", "-jar", "app.jar"]
