export class OmniAIDataSciAPI {
    public static pearsonR(x: number[], y: number[]): number {
        const n = Math.min(x.length, y.length);
        if (n <= 1) return 0;
        let sx=0,sy=0,sxy=0,sx2=0,sy2=0;
        for (let i=0;i<n;++i){sx+=x[i];sy+=y[i];sxy+=x[i]*y[i];sx2+=x[i]*x[i];sy2+=y[i]*y[i];}
        const num = n*sxy - sx*sy;
        const den = Math.sqrt((n*sx2-sx*sx)*(n*sy2-sy*sy));
        return den > 0 ? num / den : 0;
    }
}
