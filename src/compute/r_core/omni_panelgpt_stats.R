# Omni PanelGPT Consistency (R)
omni_panel_consistency <- function(answers) {
  n <- length(answers); if (n < 2) return(1)
  pairs <- combn(n, 2); same <- sum(apply(pairs, 2, function(p) answers[p[1]] == answers[p[2]]))
  round(same / ncol(pairs), 4)
}
omni_panel_improvement <- function(baseline_acc, panel_acc) {
  list(baseline = baseline_acc, panel = panel_acc, delta = round(panel_acc - baseline_acc, 4))
}
