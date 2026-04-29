export class OmniAIRenamerAPI {
    public static levenshtein(s1: string, s2: string): number {
        const m = s1.length, n = s2.length;
        const dp: number[][] = Array.from({length: m+1}, (_, i) => Array(n+1).fill(0));
        for (let i = 0; i <= m; ++i) dp[i][0] = i;
        for (let j = 0; j <= n; ++j) dp[0][j] = j;
        for (let i = 1; i <= m; ++i)
            for (let j = 1; j <= n; ++j)
                dp[i][j] = Math.min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+(s1[i-1]===s2[j-1]?0:1));
        return dp[m][n];
    }
}
