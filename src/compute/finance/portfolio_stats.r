# VectorBT inspired Portfolio Stats in R

compute_sharpe_ratio <- function(returns, risk_free_rate = 0.0) {
    mean_ret <- mean(returns)
    std_dev <- sd(returns)
    if (std_dev == 0) return(0)
    return((mean_ret - risk_free_rate) / std_dev * sqrt(252)) # Annualized
}

compute_max_drawdown <- function(cumulative_returns) {
    running_max <- cummax(cumulative_returns)
    drawdowns <- (cumulative_returns - running_max) / running_max
    return(min(drawdowns))
}
