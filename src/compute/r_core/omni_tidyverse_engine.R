# ===========================================================================
# OMNI TIDYVERSE ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : dplyr + tidyr + purrr + stringr + lubridate
# Logic Inherited: R / Compute Layer (Tidy Data Transformation Pipeline)
# ===========================================================================
#
# By studying the tidyverse, Mother learned:
#   1. Pipe %>% chains transformations left-to-right
#   2. dplyr verbs (select, filter, mutate, summarize, arrange, group_by)
#   3. tidyr reshape (pivot_longer, pivot_wider, separate, unite)
#   4. purrr map functions replace loops with functionals
#   5. Non-standard evaluation (NSE) with tidy eval ({{ }})

# ============================================================
# PART 1: Pipe-Based Data Frame Operations
# ============================================================

#' Select columns from a data frame
omni_select <- function(df, ...) {
  cols <- as.character(substitute(list(...)))[-1]
  df[, cols, drop = FALSE]
}

#' Filter rows by condition
omni_filter <- function(df, condition_fn) {
  mask <- sapply(seq_len(nrow(df)), function(i) {
    condition_fn(df[i, , drop = FALSE])
  })
  df[mask, , drop = FALSE]
}

#' Add or modify columns
omni_mutate <- function(df, ...) {
  mutations <- list(...)
  result <- df
  for (col_name in names(mutations)) {
    fn <- mutations[[col_name]]
    if (is.function(fn)) {
      result[[col_name]] <- sapply(seq_len(nrow(result)), function(i) {
        fn(result[i, , drop = FALSE])
      })
    } else {
      result[[col_name]] <- fn
    }
  }
  result
}

#' Sort rows by column
omni_arrange <- function(df, col, decreasing = FALSE) {
  col_name <- as.character(substitute(col))
  ord <- order(df[[col_name]], decreasing = decreasing)
  df[ord, , drop = FALSE]
}

#' Group-by + Summarize
omni_group_summarize <- function(df, group_col, ...) {
  group_col_name <- as.character(substitute(group_col))
  summaries <- list(...)

  groups <- unique(df[[group_col_name]])
  result_list <- lapply(groups, function(g) {
    subset_df <- df[df[[group_col_name]] == g, , drop = FALSE]
    row <- list()
    row[[group_col_name]] <- g
    for (sum_name in names(summaries)) {
      fn <- summaries[[sum_name]]
      row[[sum_name]] <- fn(subset_df)
    }
    as.data.frame(row, stringsAsFactors = FALSE)
  })

  do.call(rbind, result_list)
}

#' Count occurrences per group
omni_count <- function(df, group_col) {
  group_col_name <- as.character(substitute(group_col))
  counts <- table(df[[group_col_name]])
  data.frame(
    value = names(counts),
    n = as.integer(counts),
    stringsAsFactors = FALSE
  )
}

#' Take first n rows
omni_head <- function(df, n = 6) {
  df[seq_len(min(n, nrow(df))), , drop = FALSE]
}

#' Take last n rows
omni_tail <- function(df, n = 6) {
  start <- max(1, nrow(df) - n + 1)
  df[start:nrow(df), , drop = FALSE]
}

#' Distinct/unique rows
omni_distinct <- function(df, ...) {
  cols <- as.character(substitute(list(...)))[-1]
  if (length(cols) == 0) {
    return(unique(df))
  }
  sub <- df[, cols, drop = FALSE]
  df[!duplicated(sub), , drop = FALSE]
}

# ============================================================
# PART 2: Reshape Operations (tidyr-inspired)
# ============================================================

#' Pivot wider (long -> wide format)
omni_pivot_wider <- function(df, names_from, values_from) {
  names_col <- as.character(substitute(names_from))
  values_col <- as.character(substitute(values_from))

  # Identify ID columns (everything except names and values)
  id_cols <- setdiff(names(df), c(names_col, values_col))

  # Get unique name values
  unique_names <- unique(df[[names_col]])

  # Build result
  if (length(id_cols) > 0) {
    id_df <- unique(df[, id_cols, drop = FALSE])
  } else {
    id_df <- data.frame(row = 1)
  }

  for (nm in unique_names) {
    subset_vals <- df[df[[names_col]] == nm, values_col]
    id_df[[as.character(nm)]] <- subset_vals[seq_len(nrow(id_df))]
  }

  id_df
}

#' Pivot longer (wide -> long format)
omni_pivot_longer <- function(df, cols, names_to = "name", values_to = "value") {
  id_cols <- setdiff(names(df), cols)

  rows <- list()
  for (i in seq_len(nrow(df))) {
    for (col in cols) {
      row <- df[i, id_cols, drop = FALSE]
      row[[names_to]] <- col
      row[[values_to]] <- df[i, col]
      rows <- c(rows, list(row))
    }
  }

  do.call(rbind, rows)
}

# ============================================================
# PART 3: Functional Programming (purrr-inspired)
# ============================================================

#' Map a function over a list
omni_map <- function(.x, .f, ...) {
  lapply(.x, .f, ...)
}

#' Map returning a numeric vector
omni_map_dbl <- function(.x, .f, ...) {
  vapply(.x, .f, FUN.VALUE = numeric(1), ...)
}

#' Map returning a character vector
omni_map_chr <- function(.x, .f, ...) {
  vapply(.x, .f, FUN.VALUE = character(1), ...)
}

#' Map returning a logical vector
omni_map_lgl <- function(.x, .f, ...) {
  vapply(.x, .f, FUN.VALUE = logical(1), ...)
}

#' Map over two lists in parallel
omni_map2 <- function(.x, .y, .f, ...) {
  mapply(.f, .x, .y, MoreArgs = list(...), SIMPLIFY = FALSE)
}

#' Reduce a list to a single value
omni_reduce <- function(.x, .f, .init = NULL) {
  Reduce(.f, .x, accumulate = FALSE, init = .init)
}

#' Keep elements matching predicate
omni_keep <- function(.x, .p) {
  Filter(.p, .x)
}

#' Discard elements matching predicate
omni_discard <- function(.x, .p) {
  Filter(Negate(.p), .x)
}

#' Compose functions (right-to-left)
omni_compose <- function(...) {
  fns <- rev(list(...))
  function(x) {
    result <- x
    for (fn in fns) {
      result <- fn(result)
    }
    result
  }
}

# ============================================================
# PART 4: String Operations (stringr-inspired)
# ============================================================

#' Detect pattern in string
omni_str_detect <- function(string, pattern) {
  grepl(pattern, string)
}

#' Extract first match
omni_str_extract <- function(string, pattern) {
  regmatches(string, regexpr(pattern, string))
}

#' Replace first match
omni_str_replace <- function(string, pattern, replacement) {
  sub(pattern, replacement, string)
}

#' Replace all matches
omni_str_replace_all <- function(string, pattern, replacement) {
  gsub(pattern, replacement, string)
}

#' Pad string to width
omni_str_pad <- function(string, width, side = "left", pad = " ") {
  formatC(string, width = width, flag = ifelse(side == "left", " ", "-"),
          format = "s")
}

# ============================================================
# Engine Diagnostics
# ============================================================

omni_tidyverse_diagnostics <- function() {
  list(
    engine = "OmniTidyverseEngine",
    layer = "R Compute",
    verbs = c(
      "omni_select", "omni_filter", "omni_mutate",
      "omni_arrange", "omni_group_summarize", "omni_count",
      "omni_distinct", "omni_head", "omni_tail"
    ),
    reshape = c("omni_pivot_wider", "omni_pivot_longer"),
    functionals = c(
      "omni_map", "omni_map_dbl", "omni_map_chr", "omni_map_lgl",
      "omni_map2", "omni_reduce", "omni_keep", "omni_discard",
      "omni_compose"
    ),
    strings = c(
      "omni_str_detect", "omni_str_extract",
      "omni_str_replace", "omni_str_replace_all", "omni_str_pad"
    ),
    learned_logic = c(
      "pipe-chain-left-to-right",
      "dplyr-verb-grammar-of-data",
      "group-by-split-apply-combine",
      "pivot-reshape-long-wide",
      "purrr-map-functionals",
      "vapply-type-safe-map",
      "nse-substitute-deparse",
      "compose-function-pipeline"
    )
  )
}
