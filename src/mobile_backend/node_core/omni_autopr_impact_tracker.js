// Omni AutoPR Research Impact Tracker (Node.js)
// Ref: LightChen233/AutoPR
function computeHIndex(citations) {
  const sorted = [...citations].sort((a, b) => b - a);
  let h = 0;
  for (let i = 0; i < sorted.length; i++) {
    if (sorted[i] >= i + 1) h = i + 1; else break;
  }
  return h;
}
function promotionScore(papers, citations, serviceCount) {
  const pubScore = papers.length * 2 + papers.filter(p => ['A*', 'A'].includes(p.venue)).length * 5;
  const citeScore = citations.reduce((s, c) => s + Math.min(c, 100), 0) * 0.1;
  return { publication: pubScore, citation: Math.round(citeScore * 100) / 100,
           service: serviceCount * 1.5, hIndex: computeHIndex(citations) };
}
module.exports = { computeHIndex, promotionScore };
