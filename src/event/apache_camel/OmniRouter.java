// OMNI Framework - Apache Camel Router (Java)
// Enterprise Integration Pattern (EIP) routing for asynchronous AI events

package dev.omni.routing;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.stereotype.Component;

@Component
public class OmniEventRouter extends RouteBuilder {

    @Override
    public void configure() throws Exception {

        // Route: Incoming raw telemetry from Kafka -> Filter -> Save to DB & Alerting
        from("kafka:omni.telemetry.raw?brokers=omni-kafka:9092")
            .routeId("OmniTelemetryRouter")
            .log("OMNI Camel: Received telemetry event: ${body}")
            // Multicast to two different destinations
            .multicast()
                .to("direct:saveMetrics")
                .to("direct:checkAlerts");

        // Route: Save to Time-Series Database
        from("direct:saveMetrics")
            .routeId("OmniMetricsDB")
            // Transform JSON and insert into DB (Mock endpoint)
            .to("jdbc:omniDataSource?useHeadersAsParameters=true");

        // Route: Check for alerts (e.g., GPU overheated)
        from("direct:checkAlerts")
            .routeId("OmniAlerts")
            // Use JSONPath to check a condition
            .choice()
                .when().jsonpath("$[?(@.gpu_temp > 85)]")
                    .log("OMNI ALERT: High GPU Temperature detected!")
                    .to("slack:#omni-ops")
                .otherwise()
                    .log("OMNI Ops: GPU temps normal.");
    }
}
