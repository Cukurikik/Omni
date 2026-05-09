# OMNI Framework - Crypto Sentiment Visualizer in R
# Uses R ggplot2 to visualize the distribution of FinBERT signals

library(ggplot2)
library(dplyr)
library(jsonlite)

# Simulate fetching JSON data from OMNI API
fetch_sentiment_data <- function() {
  # Mock JSON string representation
  json_data <- '[
    {"symbol": "BTC", "signal": "BUY", "confidence": 0.85, "timestamp": "2026-05-01T10:00:00Z"},
    {"symbol": "ETH", "signal": "BUY", "confidence": 0.78, "timestamp": "2026-05-01T10:05:00Z"},
    {"symbol": "SOL", "signal": "SELL", "confidence": 0.92, "timestamp": "2026-05-01T10:10:00Z"},
    {"symbol": "BTC", "signal": "HOLD", "confidence": 0.65, "timestamp": "2026-05-01T10:15:00Z"}
  ]'
  
  df <- fromJSON(json_data)
  df$timestamp <- as.POSIXct(df$timestamp, format="%Y-%m-%dT%H:%M:%SZ", tz="UTC")
  return(df)
}

generate_sentiment_plot <- function() {
  df <- fetch_sentiment_data()
  
  p <- ggplot(df, aes(x=symbol, fill=signal)) +
    geom_bar(position="dodge") +
    theme_minimal() +
    labs(title="OMNI FinBERT Crypto Sentiment Distribution",
         x="Cryptocurrency Symbol",
         y="Count",
         fill="Signal") +
    scale_fill_manual(values=c("BUY"="#4CAF50", "SELL"="#F44336", "HOLD"="#9E9E9E"))
    
  ggsave("/tmp/omni_sentiment_distribution.png", plot=p, width=8, height=6)
  print("Plot saved to /tmp/omni_sentiment_distribution.png")
}

generate_sentiment_plot()
