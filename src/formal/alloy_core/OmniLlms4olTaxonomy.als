// Omni LLMs4OL Taxonomy (Alloy)
// Formal Layer: Structural verification of ontology acyclicity.
// Ref: HamedBabaei/LLMs4OL

sig Concept { subclassOf: set Concept }
fact Acyclic { no c: Concept | c in c.^subclassOf }
fact RootExists { some c: Concept | no c.subclassOf }
assert TaxonomySound { all c: Concept | c not in c.^subclassOf }
check TaxonomySound for 6
