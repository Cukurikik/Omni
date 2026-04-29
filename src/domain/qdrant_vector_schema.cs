namespace Omni.Qdrant {
    public class VectorSchema {
        public string CollectionName { get; set; } = "default";
        public int Dimension { get; set; } = 1536;
        public bool IsOk() { return true; }
    }
}
