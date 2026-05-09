"""OMNI Compute — Google QUEST Q&A Labeler"""
import logging
from typing import List, Dict, Tuple
import math

logger = logging.getLogger("omni.qa_labeler")

class QALabel:
    def __init__(self, category: str, score: float):
        self.category = category
        self.score = max(0.0, min(1.0, score))

class GoogleQuestTransformer:
    """
    Predicts subjective properties of Q&A pairs (e.g., question usefulness, answer helpfulness).
    Based on Kaggle Google QUEST Q&A Labeling competition.
    """
    def __init__(self, model_name: str = "roberta-base"):
        self.model_name = model_name
        self.target_labels = [
            "question_asker_intent_understanding",
            "question_body_critical",
            "question_conversational",
            "question_expect_short_answer",
            "question_fact_seeking",
            "question_has_commonly_accepted_answer",
            "question_interestingness_others",
            "question_interestingness_self",
            "question_multi_intent",
            "question_not_really_a_question",
            "question_opinion_seeking",
            "question_type_choice",
            "question_type_compare",
            "question_type_consequence",
            "question_type_definition",
            "question_type_entity",
            "question_type_instructions",
            "question_type_procedure",
            "question_type_reason_explanation",
            "question_type_spelling",
            "question_well_written",
            "answer_helpful",
            "answer_level_of_information",
            "answer_plausible",
            "answer_relevance",
            "answer_satisfaction",
            "answer_type_instructions",
            "answer_type_procedure",
            "answer_type_reason_explanation",
            "answer_well_written"
        ]
        logger.info(f"Initialized GoogleQuestTransformer with {len(self.target_labels)} targets")

    def _simulate_transformer_forward(self, text: str) -> List[float]:
        """Simulates extracting features from a transformer."""
        # Simple heuristic simulation based on string length and question marks
        length_factor = min(len(text) / 1000.0, 1.0)
        q_count = text.count('?') * 0.1
        ex_count = text.count('!') * 0.1
        
        return [length_factor, q_count, ex_count, 0.5, 0.5]

    def predict_qa_quality(self, question_title: str, question_body: str, answer: str) -> Dict[str, float]:
        """Predicts the 30 target probabilities for a given Q&A pair."""
        
        q_feat = self._simulate_transformer_forward(question_title + " " + question_body)
        a_feat = self._simulate_transformer_forward(answer)
        
        predictions = {}
        for i, label in enumerate(self.target_labels):
            if label.startswith("question_"):
                # Weight heavily on question features
                logit = q_feat[0] * 0.4 + q_feat[1] * 0.8 - q_feat[2] * 0.2 + (i % 5)*0.05
            else:
                # Weight heavily on answer features, but question length matters
                logit = a_feat[0] * 0.6 + q_feat[0] * 0.2 + a_feat[2] * 0.1 + (i % 5)*0.05
                
            # Normalize to 0-1
            prob = 1.0 / (1.0 + math.exp(-logit))
            predictions[label] = round(prob, 4)
            
        return predictions

    def filter_high_quality_answers(self, question: str, answers: List[str], threshold: float = 0.7) -> List[str]:
        """Filter answers that meet a certain helpfulness threshold."""
        valid_answers = []
        for ans in answers:
            preds = self.predict_qa_quality("", question, ans)
            if preds["answer_helpful"] >= threshold and preds["answer_relevance"] >= threshold:
                valid_answers.append(ans)
        return valid_answers
