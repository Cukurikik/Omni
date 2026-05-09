// OMNI MOTHER Production Zero-Mock Edge Geographic Router
// Maps incoming AI requests to the nearest edge PoP (Point of Presence)
// containing the required MoE experts based on Lat/Long coordinates.

class GeoCoordinate {
    constructor(lat, lon) {
        this.lat = lat;
        this.lon = lon;
    }
}

class EdgeNode {
    constructor(id, coord, loadedExperts) {
        this.id = id;
        this.coord = coord;
        this.loadedExperts = loadedExperts; // Array of string expert IDs
    }
}

export class MoeGeographicRouter {
    constructor() {
        this.nodes = [];
    }

    registerNode(nodeId, lat, lon, experts) {
        this.nodes.push(new EdgeNode(nodeId, new GeoCoordinate(lat, lon), experts));
    }

    // Haversine formula for spherical distance
    calculateDistance(coord1, coord2) {
        const R = 6371; // Earth radius in km
        const dLat = (coord2.lat - coord1.lat) * Math.PI / 180;
        const dLon = (coord2.lon - coord1.lon) * Math.PI / 180;
        
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(coord1.lat * Math.PI / 180) * Math.cos(coord2.lat * Math.PI / 180) * 
                  Math.sin(dLon/2) * Math.sin(dLon/2);
                  
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    findNearestNodeForExpert(userLat, userLon, requiredExpert) {
        const userCoord = new GeoCoordinate(userLat, userLon);
        
        let bestNode = null;
        let minDistance = Infinity;

        for (const node of this.nodes) {
            if (node.loadedExperts.includes(requiredExpert)) {
                const dist = this.calculateDistance(userCoord, node.coord);
                if (dist < minDistance) {
                    minDistance = dist;
                    bestNode = node.id;
                }
            }
        }

        if (!bestNode) {
            throw new Error(`OMNI CRITICAL: No edge node found hosting expert: ${requiredExpert}`);
        }

        return { nodeId: bestNode, distanceKm: minDistance };
    }
}
