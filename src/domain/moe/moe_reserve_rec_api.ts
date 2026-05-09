// moe_reserve_rec_api.ts — Domain / API
// Layer: Domain / Web — BC Parks & Recreation Integrator
//
// Inspired by `bcgov/reserve-rec-public`.
// This TypeScript module serves as a domain-specific middleware. When users
// query the MoE for park availability, this module intercepts the intent
// and formats a strictly typed request to the legacy Parks & Rec database system.

export interface ParkReservationRequest {
    parkId: string;
    date: string;
    partySize: number;
    facilityType: 'campsite' | 'picnic_shelter';
}

export interface ParkAvailabilityResponse {
    available: boolean;
    slots: string[];
    priceCad: number;
}

export class ReserveRecIntegrator {
    private apiEndpoint: string;

    constructor(endpoint: string = "https://api.bcparks.ca/v1") {
        this.apiEndpoint = endpoint;
        console.log(`[Reserve Rec] Initialized BC Parks & Recreation API Integrator at ${this.apiEndpoint}`);
    }

    /**
     * Parses the unstructured JSON output from the MoE (Expert #8 - Govt Services)
     * and executes the formal API call to the parks system.
     */
    public async checkAvailability(llmJsonPayload: string): Promise<ParkAvailabilityResponse> {
        try {
            const req: ParkReservationRequest = JSON.parse(llmJsonPayload);
            
            // Validate schema before hitting government APIs
            if (!req.parkId || !req.date) {
                throw new Error("Invalid schema: Missing parkId or date.");
            }

            console.log(`[Reserve Rec] Querying availability for Park ${req.parkId} on ${req.date}...`);

            // Mocking the actual fetch to the BC Gov servers
            // const response = await fetch(`${this.apiEndpoint}/availability?park=${req.parkId}&date=${req.date}`);
            // return await response.json();

            // Return mock successful response for demonstration
            return {
                available: true,
                slots: ["14:00", "15:00"],
                priceCad: 35.00
            };

        } catch (e) {
            console.error(`[Reserve Rec] LLM failed to generate valid reservation schema: ${e}`);
            return { available: false, slots: [], priceCad: 0 };
        }
    }
}
