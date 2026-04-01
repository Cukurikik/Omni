using System;

namespace OmniEngine {
    class excel_to_json {
        static void PrintJson(bool success, string code, string msg, string data = "{}") {
            string status = success ? "true" : "false";
            Console.WriteLine($"\{\"success\": {status}, \"layer\": \"CSHARP_ENGINE\", \"code\": \"{code}\", \"message\": \"{msg}\", \"data\": {data}\}");
        }

        static void Main(string[] args) {
            // TODO: Implement Excel to JSON (conv_tool_12)
            
            // Dummy response
            PrintJson(true, "SUCCESS", "Excel to JSON processed successfully.");
        }
    }
}
