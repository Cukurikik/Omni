export class OmniAllInRAGAPI {
    public static ndcg(relevances: number[]): number {
        if (relevances.length === 0) return 0;
        let dcg = 0, idcg = 0;
        for (let i = 0; i < relevances.length; ++i) {
            const disc = 1 / Math.log2(i + 2);
            dcg += relevances[i] * disc;
            idcg += disc;
        }
        return idcg > 0 ? dcg / idcg : 0;
    }
}
