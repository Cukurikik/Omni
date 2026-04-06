// 🧬 GENERATED & HEALED BY OMNI SYSTEM (Do not edit manually)
import { LucideIcon, Video, Mic, Image, FileText, ArrowRightLeft, Sparkles, Box, Bot } from 'lucide-react';

export type OmniCategory = 'VIDEO' | 'AUDIO' | 'IMAGE' | 'PDF' | 'CONVERTER' | 'AI' | 'LLM' | 'SYSTEM';
export interface OmniToolUI {
    id: string;
    name: string;
    description: string;
    category: OmniCategory;
    accepts: string;
    icon?: LucideIcon;
    requiresInput?: { key: string; label: string; type: 'text' | 'password' }[];
    endpoint?: string;
    extraInputs?: any[];
}

export const OMNI_TOOLS_UI: OmniToolUI[] = [
  {
    id: 'video_to_mp4',
    name: 'Video To Mp4',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_to_mkv',
    name: 'Video To Mkv',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_to_avi',
    name: 'Video To Avi',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_to_webm',
    name: 'Video To Webm',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_to_gif',
    name: 'Video To Gif',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_compress_1080p',
    name: 'Video Compress 1080p',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_compress_720p',
    name: 'Video Compress 720p',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_compress_480p',
    name: 'Video Compress 480p',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_compress_360p',
    name: 'Video Compress 360p',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_extract_audio_mp3',
    name: 'Video Extract Audio Mp3',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_extract_audio_wav',
    name: 'Video Extract Audio Wav',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_remove_audio',
    name: 'Video Remove Audio',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_speed_0.5x',
    name: 'Video Speed 0.5x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_speed_0.75x',
    name: 'Video Speed 0.75x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_speed_1.25x',
    name: 'Video Speed 1.25x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_speed_1.5x',
    name: 'Video Speed 1.5x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_speed_2.0x',
    name: 'Video Speed 2.0x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_reverse',
    name: 'Video Reverse',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_grayscale',
    name: 'Video Grayscale',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_sepia',
    name: 'Video Sepia',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_blur',
    name: 'Video Blur',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_crop_1_1',
    name: 'Video Crop 1 1',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_crop_16_9',
    name: 'Video Crop 16 9',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_crop_9_16',
    name: 'Video Crop 9 16',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_extract_frame_1s',
    name: 'Video Extract Frame 1s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_extract_frame_10s',
    name: 'Video Extract Frame 10s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_extract_frame_30s',
    name: 'Video Extract Frame 30s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_extract_frame_60s',
    name: 'Video Extract Frame 60s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_rotate_90_cw',
    name: 'Video Rotate 90 Cw',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_rotate_90_ccw',
    name: 'Video Rotate 90 Ccw',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'audio_to_mp3',
    name: 'Audio To Mp3',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_to_wav',
    name: 'Audio To Wav',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_to_ogg',
    name: 'Audio To Ogg',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_to_flac',
    name: 'Audio To Flac',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_compress_320k',
    name: 'Audio Compress 320k',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_compress_256k',
    name: 'Audio Compress 256k',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_compress_192k',
    name: 'Audio Compress 192k',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_compress_128k',
    name: 'Audio Compress 128k',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_compress_64k',
    name: 'Audio Compress 64k',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_vol_up_150',
    name: 'Audio Vol Up 150',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_vol_up_200',
    name: 'Audio Vol Up 200',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_vol_down_50',
    name: 'Audio Vol Down 50',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_vol_down_25',
    name: 'Audio Vol Down 25',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_bass_boost_low',
    name: 'Audio Bass Boost Low',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_bass_boost_med',
    name: 'Audio Bass Boost Med',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_bass_boost_high',
    name: 'Audio Bass Boost High',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_treble_boost',
    name: 'Audio Treble Boost',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_treble_cut',
    name: 'Audio Treble Cut',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_fade_in_3s',
    name: 'Audio Fade In 3s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_fade_in_5s',
    name: 'Audio Fade In 5s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_fade_out_3s',
    name: 'Audio Fade Out 3s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_fade_out_5s',
    name: 'Audio Fade Out 5s',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_speed_0.5x',
    name: 'Audio Speed 0.5x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_speed_1.5x',
    name: 'Audio Speed 1.5x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_speed_2.0x',
    name: 'Audio Speed 2.0x',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_reverse',
    name: 'Audio Reverse',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_8d_surround',
    name: 'Audio 8d Surround',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_mono_to_stereo',
    name: 'Audio Mono To Stereo',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_stereo_to_mono',
    name: 'Audio Stereo To Mono',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'audio_remove_silence',
    name: 'Audio Remove Silence',
    description: 'Auto-generated interface for ffmpeg',
    category: 'AUDIO',
    accepts: 'audio/*'
  },
  {
    id: 'image_to_png',
    name: 'Image To Png',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_to_jpg',
    name: 'Image To Jpg',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_to_webp',
    name: 'Image To Webp',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_to_bmp',
    name: 'Image To Bmp',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_to_tiff',
    name: 'Image To Tiff',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_compress_high',
    name: 'Image Compress High',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_compress_med',
    name: 'Image Compress Med',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_compress_low',
    name: 'Image Compress Low',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_resize_4k',
    name: 'Image Resize 4k',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_resize_1080p',
    name: 'Image Resize 1080p',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_resize_720p',
    name: 'Image Resize 720p',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_resize_480p',
    name: 'Image Resize 480p',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_grayscale',
    name: 'Image Grayscale',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_sepia',
    name: 'Image Sepia',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_invert',
    name: 'Image Invert',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_blur_light',
    name: 'Image Blur Light',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_blur_heavy',
    name: 'Image Blur Heavy',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_sharpen_light',
    name: 'Image Sharpen Light',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_sharpen_heavy',
    name: 'Image Sharpen Heavy',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_rotate_90',
    name: 'Image Rotate 90',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_rotate_180',
    name: 'Image Rotate 180',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_rotate_270',
    name: 'Image Rotate 270',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_flip_horizontal',
    name: 'Image Flip Horizontal',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_flip_vertical',
    name: 'Image Flip Vertical',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_auto_orient',
    name: 'Image Auto Orient',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_edge_detect',
    name: 'Image Edge Detect',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_charcoal',
    name: 'Image Charcoal',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_noise_reduce',
    name: 'Image Noise Reduce',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_contrast_boost',
    name: 'Image Contrast Boost',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'image_brightness_boost',
    name: 'Image Brightness Boost',
    description: 'Auto-generated interface for magick',
    category: 'IMAGE',
    accepts: 'image/*'
  },
  {
    id: 'pdf_compress_screen',
    name: 'Pdf Compress Screen',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_compress_ebook',
    name: 'Pdf Compress Ebook',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_compress_printer',
    name: 'Pdf Compress Printer',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_compress_prepress',
    name: 'Pdf Compress Prepress',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_protect_pass',
    name: 'Pdf Protect Pass',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_decrypt_pass',
    name: 'Pdf Decrypt Pass',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_merge_generic',
    name: 'Pdf Merge Generic',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_burst_pages',
    name: 'Pdf Burst Pages',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_rotate_90_cw',
    name: 'Pdf Rotate 90 Cw',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_rotate_90_ccw',
    name: 'Pdf Rotate 90 Ccw',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_rotate_180',
    name: 'Pdf Rotate 180',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_allow_printing',
    name: 'Pdf Allow Printing',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_allow_copying',
    name: 'Pdf Allow Copying',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_linearize_web',
    name: 'Pdf Linearize Web',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_to_images_jpg',
    name: 'Pdf To Images Jpg',
    description: 'Auto-generated interface for pdftoppm',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_to_images_png',
    name: 'Pdf To Images Png',
    description: 'Auto-generated interface for pdftoppm',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_extract_text',
    name: 'Pdf Extract Text',
    description: 'Auto-generated interface for pdftotext',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_remove_pass_unsec',
    name: 'Pdf Remove Pass Unsec',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_watermark_draft',
    name: 'Pdf Watermark Draft',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_watermark_confidential',
    name: 'Pdf Watermark Confidential',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_grayscale',
    name: 'Pdf Grayscale',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_repair_corrupt',
    name: 'Pdf Repair Corrupt',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_attach_file',
    name: 'Pdf Attach File',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_extract_attachments',
    name: 'Pdf Extract Attachments',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_metadata_clear',
    name: 'Pdf Metadata Clear',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_scale_a4',
    name: 'Pdf Scale A4',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_scale_letter',
    name: 'Pdf Scale Letter',
    description: 'Auto-generated interface for gs',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_uncompress_streams',
    name: 'Pdf Uncompress Streams',
    description: 'Auto-generated interface for qpdf',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_flatten',
    name: 'Pdf Flatten',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_reverse_pages',
    name: 'Pdf Reverse Pages',
    description: 'Auto-generated interface for pdftk',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'docx_to_pdf',
    name: 'Docx To Pdf',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'pptx_to_pdf',
    name: 'Pptx To Pdf',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'xlsx_to_pdf',
    name: 'Xlsx To Pdf',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'html_to_pdf',
    name: 'Html To Pdf',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'md_to_pdf',
    name: 'Md To Pdf',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'txt_to_pdf',
    name: 'Txt To Pdf',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'rtf_to_pdf',
    name: 'Rtf To Pdf',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'odt_to_pdf',
    name: 'Odt To Pdf',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'odp_to_pdf',
    name: 'Odp To Pdf',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'ods_to_pdf',
    name: 'Ods To Pdf',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'md_to_html',
    name: 'Md To Html',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'html_to_md',
    name: 'Html To Md',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'docx_to_md',
    name: 'Docx To Md',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'docx_to_html',
    name: 'Docx To Html',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'html_to_docx',
    name: 'Html To Docx',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'csv_to_html',
    name: 'Csv To Html',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'csv_to_pdf',
    name: 'Csv To Pdf',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'epub_to_pdf',
    name: 'Epub To Pdf',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'pdf_to_html',
    name: 'Pdf To Html',
    description: 'Auto-generated interface for pdftohtml',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'pdf_to_txt',
    name: 'Pdf To Txt',
    description: 'Auto-generated interface for pdftotext',
    category: 'PDF',
    accepts: 'pdf/*'
  },
  {
    id: 'rtf_to_docx',
    name: 'Rtf To Docx',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'docx_to_odt',
    name: 'Docx To Odt',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'pptx_to_odp',
    name: 'Pptx To Odp',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'xlsx_to_ods',
    name: 'Xlsx To Ods',
    description: 'Auto-generated interface for soffice',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'md_to_docx',
    name: 'Md To Docx',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'epub_to_md',
    name: 'Epub To Md',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'md_to_epub',
    name: 'Md To Epub',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'latex_to_pdf',
    name: 'Latex To Pdf',
    description: 'Auto-generated interface for pandoc',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'xml_to_json',
    name: 'Xml To Json',
    description: 'Auto-generated interface for python3',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'csv_to_json',
    name: 'Csv To Json',
    description: 'Auto-generated interface for python3',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
  {
    id: 'video_glitch',
    name: 'Video Glitch',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'video_pixel',
    name: 'Video Pixel',
    description: 'Auto-generated interface for ffmpeg',
    category: 'VIDEO',
    accepts: 'video/*'
  },
  {
    id: 'kinetic_test_tool',
    name: 'Kinetic Test Tool',
    description: 'Auto-generated interface for auto_generated',
    category: 'SYSTEM',
    accepts: 'system/*'
  },
];
