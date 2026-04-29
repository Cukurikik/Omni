package rules.datablations

default is_subset_valid = false

is_subset_valid {
    input.subset_size >= 1000
    input.maintains_class_balance == true
    # Rego policy defining structural constraints for valid Datablation subsets
}
