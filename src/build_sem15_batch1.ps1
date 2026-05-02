"$configs = @(\
    @{ name=\"llm_table_survey\"; desc=\"TF-IDF term frequency calculation\"; cpp=@\"\
        double compute(const double* term_freqs, const double* doc_freqs, int32_t len, double total_docs) {\
            double sum = 0.0;\
            f
<truncated 12972 bytes>