package engine

import "omnitools/core"

// ProcessimageBlur adalah logika untuk fitur image_blur.
// Skuad Backend: Fokus di sini! Jangan pikirkan UI.
func ProcessimageBlur(job *core.Job) error {
    inputPath := ""
    outputPath := ""
    if len(job.Args) >= 2 {
        inputPath = job.Args[0]
        outputPath = job.Args[1]
    }
    // Gunakan Blackbox Engine agar Anda tidak perlu menyentuh C++
    return RunHeavyEngine("image_blur", inputPath, outputPath)
}
