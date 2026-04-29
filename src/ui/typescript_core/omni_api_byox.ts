export interface ModelWeights {
    m: number;
    c: number;
}

export class OmniBYOXMLAPI {
    /** OMNI Interface Layer: BYOX ML API */
    public static predict(x: number, model: ModelWeights): number {
        return model.m * x + model.c;
    }

    public static calculateMSE(x: number[], y: number[], model: ModelWeights): number {
        if (x.length !== y.length || x.length === 0) return -1;
        
        let error = 0;
        for (let i = 0; i < x.length; i++) {
            const pred = this.predict(x[i], model);
            error += Math.pow(pred - y[i], 2);
        }
        return error / x.length;
    }
}
