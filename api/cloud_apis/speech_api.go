package cloud_apis

import (
	"context"
	"fmt"
	"io"
	"log"

	speech "cloud.google.com/go/speech/apiv1"
	"cloud.google.com/go/speech/apiv1/speechpb"
	texttospeech "cloud.google.com/go/texttospeech/apiv1"
	"cloud.google.com/go/texttospeech/apiv1/texttospeechpb"
)

// ==========================================
// 🎤 OMNI SPEECH — STT & TTS ENGINE
// ==========================================

type SpeechBridge struct{ projectID string }

func NewSpeechBridge(projectID string) *SpeechBridge {
	return &SpeechBridge{projectID: projectID}
}

func (s *SpeechBridge) Transcribe(ctx context.Context, audioData []byte, languageCode string, sampleRate int32) (string, error) {
	client, err := speech.NewClient(ctx)
	if err != nil {
		return "", fmt.Errorf("OMNI_SPEECH_ERROR: gagal membuat STT client: %v", err)
	}
	defer client.Close()

	resp, err := client.Recognize(ctx, &speechpb.RecognizeRequest{
		Config: &speechpb.RecognitionConfig{
			Encoding:        speechpb.RecognitionConfig_LINEAR16,
			SampleRateHertz: sampleRate,
			LanguageCode:    languageCode,
		},
		Audio: &speechpb.RecognitionAudio{AudioSource: &speechpb.RecognitionAudio_Content{Content: audioData}},
	})
	if err != nil {
		return "", fmt.Errorf("OMNI_SPEECH_ERROR: gagal transkripsi: %v", err)
	}

	var transcript string
	for _, result := range resp.Results {
		if len(result.Alternatives) > 0 {
			transcript += result.Alternatives[0].Transcript
		}
	}
	log.Printf("🎤 [OMNI SPEECH] Transkripsi selesai: %d karakter", len(transcript))
	return transcript, nil
}

func (s *SpeechBridge) Synthesize(ctx context.Context, text, languageCode string, writer io.Writer) error {
	client, err := texttospeech.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_SPEECH_ERROR: gagal membuat TTS client: %v", err)
	}
	defer client.Close()

	resp, err := client.SynthesizeSpeech(ctx, &texttospeechpb.SynthesizeSpeechRequest{
		Input:       &texttospeechpb.SynthesisInput{InputSource: &texttospeechpb.SynthesisInput_Text{Text: text}},
		Voice:       &texttospeechpb.VoiceSelectionParams{LanguageCode: languageCode, SsmlGender: texttospeechpb.SsmlVoiceGender_NEUTRAL},
		AudioConfig: &texttospeechpb.AudioConfig{AudioEncoding: texttospeechpb.AudioEncoding_MP3},
	})
	if err != nil {
		return fmt.Errorf("OMNI_SPEECH_ERROR: gagal sintesis: %v", err)
	}

	if _, err := writer.Write(resp.AudioContent); err != nil {
		return fmt.Errorf("OMNI_SPEECH_ERROR: gagal menulis audio: %v", err)
	}
	log.Printf("🎤 [OMNI SPEECH] TTS selesai: %d bytes audio", len(resp.AudioContent))
	return nil
}
