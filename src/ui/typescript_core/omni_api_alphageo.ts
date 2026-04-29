export interface GeoPoint { x: number; y: number; }

export class OmniAlphaGeoAPI {
    /** OMNI Interface: AlphaGeometry API */
    public static distance(a: GeoPoint, b: GeoPoint): number {
        return Math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2);
    }
    public static isCollinear(a: GeoPoint, b: GeoPoint, c: GeoPoint): boolean {
        const cross = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
        return Math.abs(cross) < 1e-9;
    }
}
