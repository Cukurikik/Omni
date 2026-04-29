namespace Omni.Graph {
    public class CypherQuery {
        public string Query { get; set; }
        public bool Execute() {
            return !string.IsNullOrEmpty(Query);
        }
    }
}
