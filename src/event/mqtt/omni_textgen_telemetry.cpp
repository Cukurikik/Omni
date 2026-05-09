// OMNI Framework - MQTT Publisher for TextGenerator.io Telemetry
#include <iostream>
#include <string>
#include <mqtt/async_client.h>

const std::string SERVER_ADDRESS { "tcp://omni-mqtt-broker:1883" };
const std::string CLIENT_ID { "omni_textgen_telemetry_cpp" };
const std::string TOPIC { "omni/telemetry/textgen" };

int main() {
    mqtt::async_client cli(SERVER_ADDRESS, CLIENT_ID);
    mqtt::connect_options connOpts;
    connOpts.set_keep_alive_interval(20);
    connOpts.set_clean_session(true);

    try {
        std::cout << "OMNI: Connecting to MQTT Broker..." << std::flush;
        cli.connect(connOpts)->wait();
        std::cout << "OK" << std::endl;

        std::string payload = "{\"api_calls\": 15420, \"avg_latency_ms\": 45.2, \"errors\": 0}";
        auto msg = mqtt::make_message(TOPIC, payload);
        msg->set_qos(1);

        cli.publish(msg)->wait();
        std::cout << "OMNI: Telemetry published." << std::endl;

        cli.disconnect()->wait();
    }
    catch (const mqtt::exception& exc) {
        std::cerr << "OMNI Error: " << exc.what() << std::endl;
        return 1;
    }
    return 0;
}
