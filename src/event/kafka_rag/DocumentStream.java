package omni.kafka;

public class DocumentStream {
    public boolean processDocument(String doc) throws Exception {
        if (doc == null || doc.isEmpty()) {
            throw new Exception("Document cannot be null");
        }
        return true;
    }
}
