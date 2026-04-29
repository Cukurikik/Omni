using System;
using System.Threading.Tasks;

namespace Omni.Business.Paperless
{
    public class OcrPipeline
    {
        // OMNI Engine: Paperless-ng document consumption and OCR routing logic
        public async Task<DocumentRecord> ConsumeDocumentAsync(byte[] fileData, string mimeType)
        {
            if (fileData == null || fileData.Length == 0)
                throw new ArgumentException("Empty file data provided.");

            string extractedText = string.Empty;

            // Route to specific extraction engine based on mime
            if (mimeType == "application/pdf")
            {
                extractedText = await RunPdfOcrAsync(fileData);
            }
            else if (mimeType.StartsWith("image/"))
            {
                extractedText = await RunTesseractOcrAsync(fileData);
            }
            else
            {
                throw new NotSupportedException($"MimeType {mimeType} not supported for OCR.");
            }

            return new DocumentRecord {
                Id = Guid.NewGuid(),
                Content = extractedText,
                AddedAt = DateTime.UtcNow
            };
        }

        private Task<string> RunPdfOcrAsync(byte[] data) => Task.FromResult("[PDF Extracted Text Stub]");
        private Task<string> RunTesseractOcrAsync(byte[] data) => Task.FromResult("[Image OCR Text Stub]");
    }

    public class DocumentRecord {
        public Guid Id { get; set; }
        public string Content { get; set; }
        public DateTime AddedAt { get; set; }
    }
}
