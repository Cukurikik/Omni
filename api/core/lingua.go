package core

import (
	"encoding/json"
	"os"
	"strings"
)

var Dictionary map[string]string

func LoadLingua() {
	lang := AppConfig.CliLanguage
	if lang == "" {
		lang = "en"
	}

	fileData, err := os.ReadFile("../configs/locales/" + lang + ".json")
	if err != nil {
		fileData, _ = os.ReadFile("../configs/locales/en.json") // Fallback ke Inggris
	}

	Dictionary = make(map[string]string)
	json.Unmarshal(fileData, &Dictionary)
}

// T (Translate) mengembalikan string berdasarkan kunci dan melakukan replace variabel dinamis
func T(key string, vars map[string]string) string {
	text, exists := Dictionary[key]
	if !exists {
		return "[" + key + "]"
	}

	for k, v := range vars {
		text = strings.ReplaceAll(text, "{{"+k+"}}", v)
	}
	return text
}
