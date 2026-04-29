# Omni AutoTools Service (Ruby)
module Omni; module AutoTools
  def self.discover(query, tools, top_k = 5)
    q = query.downcase.split.to_set
    tools.map { |t| {tool: t[:name], score: (q & t[:description].downcase.split.to_set).size.to_f / [q.size, 1].max} }
         .sort_by { |t| -t[:score] }.first(top_k)
  end
  def self.chain(calls) = calls.each_with_index.map { |c, i| {step: i+1, tool: c[:tool], status: 'executed'} }
end; end
