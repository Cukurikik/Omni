// OMNI MOTHER: Enka.Network API Wrapper
// Fetches Genshin Impact profiles via Enka.Network API

export class OmniEnkaNetwork {
    private readonly baseUrl = 'https://enka.network/api/uid/';

    public async fetchPlayerProfile(uid: string): Promise<any> {
        console.log(`[OMNI ENKA] Fetching UID: ${uid}`);
        try {
            const response = await fetch(`${this.baseUrl}${uid}`);
            if (!response.ok) throw new Error("UID not found or rate limited");
            return await response.json();
        } catch (error) {
            console.error("[OMNI ENKA ERROR]", error);
            return null;
        }
    }
}
