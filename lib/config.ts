import { OmniTool, CategoryInfo, ToolCategory } from './types';

// ==========================================
// ⚡ OMNI TOOLS - Tool Registry
// ==========================================

export const CATEGORIES: CategoryInfo[] = [
  { id: 'ALL', label: 'Semua', emoji: '🌐' },
  { id: 'VIDEO', label: 'Video', emoji: '🎬' },
  { id: 'AUDIO', label: 'Audio', emoji: '🎵' },
  { id: 'IMAGE', label: 'Image', emoji: '🖼️' },
  { id: 'PDF', label: 'PDF', emoji: '📄' },
  { id: 'CONVERTER', label: 'Converter', emoji: '🔄' },
  { id: 'AI', label: 'AI', emoji: '✨' },
  { id: 'LLM', label: 'LLM', emoji: '🤖' },
  { id: 'SYSTEM', label: 'System', emoji: '⚙️' },
];

// All available tools - should match the backend engine tools
export const OMNI_TOOLS: OmniTool[] = [
  // VIDEO TOOLS
  { id: 'video_tool_01', name: 'Sync AV Timeline', description: 'Sinkronisasi frame video dan audio tingkat rendah', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/sync-timeline', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'video_tool_02', name: 'Video Compressor', description: 'Kompresi video dengan manipulasi CRF memori langsung', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/compressor', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'video_tool_03', name: 'Video Merger', description: 'Gabungkan beberapa video menjadi satu', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/merger', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'video_tool_04', name: 'Video Splitter', description: 'Pisahkan video menjadi beberapa bagian', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/splitter', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'video_tool_05', name: 'Video to GIF', description: 'Konversi video ke format GIF animasi', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/to-gif', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'video_tool_06', name: 'Extract Frames', description: 'Ekstrak semua frame dari video', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/extract-frames', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'video_tool_07', name: 'Audio Extractor', description: 'Ekstrak audio dari video', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/audio-extractor', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'video_tool_08', name: 'Speed Controller', description: 'Atur kecepatan video', category: 'VIDEO', emoji: '🎬', endpoint: '/api/v1/tools/video/speed', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  
  // AUDIO TOOLS
  { id: 'audio_tool_01', name: 'Audio Merger', description: 'Gabungkan beberapa file audio', category: 'AUDIO', emoji: '🎵', endpoint: '/api/v1/tools/audio/merger', method: 'POST', accepts: 'audio/*', delegateTo: 'C++' },
  { id: 'audio_tool_02', name: 'Audio Splitter', description: 'Pisahkan audio menjadi trek', category: 'AUDIO', emoji: '🎵', endpoint: '/api/v1/tools/audio/splitter', method: 'POST', accepts: 'audio/*', delegateTo: 'C++' },
  { id: 'audio_tool_03', name: 'Audio Normalizer', description: 'Normalisasi volume audio', category: 'AUDIO', emoji: '🎵', endpoint: '/api/v1/tools/audio/normalizer', method: 'POST', accepts: 'audio/*', delegateTo: 'C++' },
  { id: 'audio_tool_04', name: 'Noise Remover', description: 'Hapus noise dari audio', category: 'AUDIO', emoji: '🎵', endpoint: '/api/v1/tools/audio/noise-remover', method: 'POST', accepts: 'audio/*', delegateTo: 'C++' },
  { id: 'audio_tool_05', name: 'Pitch Shifter', description: 'Ubah pitch audio', category: 'AUDIO', emoji: '🎵', endpoint: '/api/v1/tools/audio/pitch', method: 'POST', accepts: 'audio/*', delegateTo: 'C++' },
  { id: 'audio_tool_06', name: 'Vocal Isolator', description: 'Pisahkan vokal dari instrumen', category: 'AUDIO', emoji: '🎵', endpoint: '/api/v1/tools/audio/vocal-isolator', method: 'POST', accepts: 'audio/*', delegateTo: 'Python' },
  
  // IMAGE TOOLS
  { id: 'image_tool_01', name: 'Image Resizer', description: 'Ubah ukuran gambar', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/resizer', method: 'POST', accepts: 'image/*', delegateTo: 'C++' },
  { id: 'image_tool_02', name: 'Image Compressor', description: 'Kompresi gambar', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/compressor', method: 'POST', accepts: 'image/*', delegateTo: 'C++' },
  { id: 'image_tool_03', name: 'Background Remover', description: 'Hapus background gambar AI', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/remove-bg', method: 'POST', accepts: 'image/*', delegateTo: 'Python' },
  { id: 'image_tool_04', name: 'Image Upscaler', description: 'Perbesar resolusi AI', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/upscaler', method: 'POST', accepts: 'image/*', delegateTo: 'Python' },
  { id: 'image_tool_05', name: 'Image Cropper', description: 'Potong gambar', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/cropper', method: 'POST', accepts: 'image/*', delegateTo: 'C++' },
  { id: 'image_tool_06', name: 'Image Rotator', description: 'Putar gambar', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/rotator', method: 'POST', accepts: 'image/*', delegateTo: 'C++' },
  { id: 'image_tool_07', name: 'Watermark', description: 'Tambah watermark', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/watermark', method: 'POST', accepts: 'image/*', delegateTo: 'C#' },
  { id: 'image_tool_08', name: 'Filter & Effects', description: 'Tambah filter dan efek', category: 'IMAGE', emoji: '🖼️', endpoint: '/api/v1/tools/image/filters', method: 'POST', accepts: 'image/*', delegateTo: 'C#' },
  
  // PDF TOOLS
  { id: 'pdf_tool_01', name: 'PDF Merger', description: 'Gabungkan beberapa PDF', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/merger', method: 'POST', accepts: 'application/pdf', delegateTo: 'C#' },
  { id: 'pdf_tool_02', name: 'PDF Splitter', description: 'Pisahkan PDF', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/splitter', method: 'POST', accepts: 'application/pdf', delegateTo: 'C#' },
  { id: 'pdf_tool_03', name: 'PDF Compressor', description: 'Kompresi PDF', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/compressor', method: 'POST', accepts: 'application/pdf', delegateTo: 'C#' },
  { id: 'pdf_tool_04', name: 'PDF to Image', description: 'Konversi PDF ke gambar', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/to-image', method: 'POST', accepts: 'application/pdf', delegateTo: 'C#' },
  { id: 'pdf_tool_05', name: 'Image to PDF', description: 'Konversi gambar ke PDF', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/from-image', method: 'POST', accepts: 'image/*', delegateTo: 'C#' },
  { id: 'pdf_tool_06', name: 'PDF OCR', description: 'OCR scanner untuk PDF', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/ocr', method: 'POST', accepts: 'application/pdf', delegateTo: 'Python' },
  { id: 'pdf_tool_07', name: 'PDF Watermark', description: 'Tambah watermark ke PDF', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/watermark', method: 'POST', accepts: 'application/pdf', delegateTo: 'C#' },
  { id: 'pdf_tool_08', name: 'PDF Encrypt', description: 'Enkripsi PDF', category: 'PDF', emoji: '📄', endpoint: '/api/v1/tools/pdf/encrypt', method: 'POST', accepts: 'application/pdf', delegateTo: 'Golang' },
  
  // CONVERTER TOOLS
  { id: 'converter_tool_01', name: 'Image Format Converter', description: 'Konversi format gambar', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/image', method: 'POST', accepts: 'image/*', delegateTo: 'C#' },
  { id: 'converter_tool_02', name: 'Audio Format Converter', description: 'Konversi format audio', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/audio', method: 'POST', accepts: 'audio/*', delegateTo: 'C++' },
  { id: 'converter_tool_03', name: 'Video Format Converter', description: 'Konversi format video', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/video', method: 'POST', accepts: 'video/*', delegateTo: 'C++' },
  { id: 'converter_tool_04', name: 'CSV to JSON', description: 'CSV ke JSON', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/csv-json', method: 'POST', accepts: 'text/csv', delegateTo: 'C#' },
  { id: 'converter_tool_05', name: 'JSON to CSV', description: 'JSON ke CSV', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/json-csv', method: 'POST', accepts: 'application/json', delegateTo: 'C#' },
  { id: 'converter_tool_06', name: 'JSON to XML', description: 'JSON ke XML', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/json-xml', method: 'POST', accepts: 'application/json', delegateTo: 'C#' },
  { id: 'converter_tool_07', name: 'XML to JSON', description: 'XML ke JSON', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/xml-json', method: 'POST', accepts: 'application/xml', delegateTo: 'C#' },
  { id: 'converter_tool_08', name: 'Base64 Encoder', description: 'Encode ke Base64', category: 'CONVERTER', emoji: '🔄', endpoint: '/api/v1/tools/converter/base64-encode', method: 'POST', accepts: '*/*', delegateTo: 'C#' },
  
  // AI TOOLS
  { id: 'ai_tool_01', name: 'Image Generator', description: '_generate_file_ Gambar dengan AI', category: 'AI', emoji: '✨', endpoint: '/api/v1/tools/ai/image-generator', method: 'POST', accepts: 'text/*', delegateTo: 'Python' },
  { id: 'ai_tool_02', name: 'Image Captioner', description: '生成文字描述 gambar', category: 'AI', emoji: '✨', endpoint: '/api/v1/tools/ai/image-captioner', method: 'POST', accepts: 'image/*', delegateTo: 'Python' },
  { id: 'ai_tool_03', name: 'Text Summarizer', description: 'Ringkas teks dengan AI', category: 'AI', emoji: '✨', endpoint: '/api/v1/tools/ai/summarizer', method: 'POST', accepts: 'text/*', delegateTo: 'Python' },
  { id: 'ai_tool_04', name: 'Translator', description: 'Terjemahkan bahasa', category: 'AI', emoji: '✨', endpoint: '/api/v1/tools/ai/translator', method: 'POST', accepts: 'text/*', delegateTo: 'Python' },
  { id: 'ai_tool_05', name: 'Code Reviewer', description: 'Review kode otomatis', category: 'AI', emoji: '✨', endpoint: '/api/v1/tools/ai/code-reviewer', method: 'POST', accepts: 'text/*', delegateTo: 'Python' },
  { id: 'ai_tool_06', name: 'Visual Generator', description: 'Buat visual dari teks', category: 'AI', emoji: '✨', endpoint: '/api/v1/tools/ai/visual-generator', method: 'POST', accepts: 'text/*', delegateTo: 'Python' },
  
  // LLM TOOLS
  { id: 'llm_tool_01', name: 'Chat Assistant', description: 'Obrolan dengan AI Assistant', category: 'LLM', emoji: '🤖', endpoint: '/api/v1/tools/llm/chat', method: 'POST', accepts: 'text/*', delegateTo: 'Golang' },
  { id: 'llm_tool_02', name: 'Code Writer', description: 'Tulis kode dengan AI', category: 'LLM', emoji: '🤖', endpoint: '/api/v1/tools/llm/code', method: 'POST', accepts: 'text/*', delegateTo: 'Golang' },
  { id: 'llm_tool_03', name: 'Explain Code', description: 'Jelaskan kode', category: 'LLM', emoji: '🤖', endpoint: '/api/v1/tools/llm/explain', method: 'POST', accepts: 'text/*', delegateTo: 'Golang' },
  { id: 'llm_tool_04', name: 'Ask Document', description: 'Tanya dokumen', category: 'LLM', emoji: '🤖', endpoint: '/api/v1/tools/llm/ask-doc', method: 'POST', accepts: '*/*', delegateTo: 'Golang' },
  
  // SYSTEM TOOLS
  { id: 'system_tool_01', name: 'Hash Generator', description: 'Generate SHA/MD5', category: 'SYSTEM', emoji: '⚙️', endpoint: '/api/v1/tools/system/hash', method: 'POST', accepts: '*/*', delegateTo: 'C#' },
  { id: 'system_tool_02', name: 'JWT Decoder', description: 'Decode JWT token', category: 'SYSTEM', emoji: '⚙️', endpoint: '/api/v1/tools/system/jwt-decode', method: 'POST', accepts: 'text/*', delegateTo: 'C#' },
  { id: 'system_tool_03', name: 'QR Generator', description: 'Generate QR Code', category: 'SYSTEM', emoji: '⚙️', endpoint: '/api/v1/tools/system/qr-generator', method: 'POST', accepts: 'text/*', delegateTo: 'C#' },
  { id: 'system_tool_04', name: 'Unit Converter', description: 'Konversi unit', category: 'SYSTEM', emoji: '⚙️', endpoint: '/api/v1/tools/system/unit', method: 'POST', accepts: 'text/*', delegateTo: 'C#' },
];

export function getToolsByCategory(category: ToolCategory | 'ALL'): OmniTool[] {
  if (category === 'ALL') return OMNI_TOOLS;
  return OMNI_TOOLS.filter(tool => tool.category === category);
}

export function getToolById(id: string): OmniTool | undefined {
  return OMNI_TOOLS.find(tool => tool.id === id);
}