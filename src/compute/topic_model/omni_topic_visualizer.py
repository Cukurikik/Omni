"""
omni_topic_visualizer.py — Topic Modeling Visualization
Inspired by: turftopic (Semantic Topic Models)
Layer: Compute / AI

Provides dynamic generation of HTML/JS visualization payloads for analyzing
document embeddings and semantic topic clusters (c-TF-IDF).
"""

import json
from typing import List, Dict, Tuple
import numpy as np

class OmniTopicVisualizer:
    """
    Transforms topic-word distributions and document 2D projections into
    interactive visualization structures compatible with D3.js or Plotly.
    """

    def __init__(self, topic_model):
        self.topic_model = topic_model # Refers to OmniTurfTopic instance

    def generate_scatter_data(self, 
                              doc_embeddings_2d: np.ndarray, 
                              doc_topics: List[int],
                              doc_texts: List[str]) -> str:
        """
        Serializes 2D embeddings and topics into JSON for scatter plots.
        """
        assert len(doc_embeddings_2d) == len(doc_topics) == len(doc_texts)
        
        data = []
        for i in range(len(doc_topics)):
            data.append({
                "x": float(doc_embeddings_2d[i][0]),
                "y": float(doc_embeddings_2d[i][1]),
                "topic": int(doc_topics[i]),
                "text": doc_texts[i][:100] + "..." # Snippet
            })
            
        return json.dumps({
            "type": "scatter",
            "data": data,
            "title": "Document Semantic Map"
        })

    def generate_barchart_data(self, top_n: int = 10) -> str:
        """
        Generates bar chart data for the highest scoring words per topic.
        """
        topic_words = self.topic_model.get_topic_words(top_n=top_n)
        
        data = []
        for topic_id, words in topic_words.items():
            words_list, scores_list = zip(*words)
            data.append({
                "topic": topic_id,
                "words": list(words_list),
                "scores": [float(s) for s in scores_list]
            })
            
        return json.dumps({
            "type": "barchart",
            "data": data,
            "title": "Top Words per Topic (c-TF-IDF)"
        })

    def export_html(self, output_path: str, doc_embeddings_2d: np.ndarray, doc_topics: List[int], doc_texts: List[str]):
        """
        Exports a self-contained HTML file wrapping the visualizations.
        """
        scatter_json = self.generate_scatter_data(doc_embeddings_2d, doc_topics, doc_texts)
        barchart_json = self.generate_barchart_data()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OMNI Topic Explorer</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body style="font-family: sans-serif; background: #0a0a0a; color: #fff;">
            <h1>OMNI Semantic Topic Visualizer</h1>
            <div id="scatter" style="width:100%;height:600px;"></div>
            <div id="barcharts" style="width:100%;height:600px; display:flex; overflow-x: auto;"></div>
            
            <script>
                // This would contain the Plotly rendering logic for the injected JSON payloads
                const scatterData = {scatter_json};
                const barData = {barchart_json};
                console.log("Visualizations loaded.");
            </script>
        </body>
        </html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return output_path
