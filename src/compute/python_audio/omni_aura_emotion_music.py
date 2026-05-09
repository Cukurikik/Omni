from transformers import pipeline

class OmniAuraRecommender:
    """
    Aura: Emotion-Based Song Recommender.
    Uses an NLP Transformer trained on GoEmotions to classify text input,
    then maps the emotional aura to a specific music genre or track.
    """
    def __init__(self):
        # Load a pre-trained emotion classification pipeline
        self.emotion_classifier = pipeline(
            "text-classification", 
            model="bhadresh-savani/distilbert-base-uncased-emotion", 
            return_all_scores=False
        )
        
        self.music_map = {
            "joy": ["Happy - Pharrell Williams", "Walking On Sunshine - Katrina & The Waves"],
            "sadness": ["Someone Like You - Adele", "Fix You - Coldplay"],
            "anger": ["Break Stuff - Limp Bizkit", "Killing in the Name - RATM"],
            "fear": ["Breathe Me - Sia", "Creep - Radiohead"],
            "surprise": ["Bohemian Rhapsody - Queen"],
            "love": ["Perfect - Ed Sheeran", "All of Me - John Legend"]
        }

    def recommend_music(self, user_input: str) -> dict:
        """
        Analyze user text, detect emotion, and recommend a song.
        """
        result = self.emotion_classifier(user_input)[0]
        emotion = result['label']
        confidence = result['score']
        
        songs = self.music_map.get(emotion, ["Lofi Hip Hop Radio - Beats to Relax/Study to"])
        
        # Pick the first one for deterministic behavior, or random.choice(songs)
        recommended_song = songs[0] 
        
        return {
            "detected_emotion": emotion,
            "confidence": round(confidence, 4),
            "recommended_song": recommended_song
        }

if __name__ == "__main__":
    aura = OmniAuraRecommender()
    print(aura.recommend_music("I just got a huge promotion at work and I'm thrilled!"))
