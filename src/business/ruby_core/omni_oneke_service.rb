# Omni OneKE Extraction Service (Ruby)
module Omni; module OneKE
  def self.extract_entities(text, schema)
    text.scan(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/).map { |e| {text: e, type: schema.first || 'Entity'} }
  end
  def self.ner_f1(pred, gold)
    ps = pred.to_set; gs = gold.to_set; tp = (ps & gs).size
    p = tp.to_f / [ps.size, 1].max; r = tp.to_f / [gs.size, 1].max
    f1 = (p + r) > 0 ? 2*p*r/(p+r) : 0
    {precision: p.round(4), recall: r.round(4), f1: f1.round(4)}
  end
end; end
