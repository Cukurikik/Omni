// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Virgilio Mentor Matrix (OMNI Zero-Mock Implementation)
// Implements Cosine Similarity mathematically for syllabus recommendation.

export type Result<T> = 
  | { value: T; isOk: true; error: null }
  | { value: null; isOk: false; error: string };

export class MentorMatrix {
  private calculateDotProduct(vecA: number[], vecB: number[]): number {
    let sum = 0;
    for (let i = 0; i < vecA.length; i++) {
        sum += vecA[i] * vecB[i];
    }
    return sum;
  }

  private calculateMagnitude(vec: number[]): number {
      let sum = 0;
      for (let i = 0; i < vec.length; i++) {
          sum += vec[i] * vec[i];
      }
      return Math.sqrt(sum);
  }

  public recommendSyllabus(userProfile: number[], availableSyllabi: { id: string; profile: number[] }[]): Result<string> {
    if (!userProfile || userProfile.length === 0) {
      return { value: null, isOk: false, error: "Empty user profile vector." };
    }
    
    if (!availableSyllabi || availableSyllabi.length === 0) {
      return { value: null, isOk: false, error: "No syllabi available." };
    }

    let bestMatchId = "";
    let highestSim = -2.0; // Cosine sim ranges [-1, 1]
    
    const userMag = this.calculateMagnitude(userProfile);
    if (userMag === 0) {
       return { value: null, isOk: false, error: "Zero magnitude user profile vector." };
    }

    for (const syllabus of availableSyllabi) {
        if (syllabus.profile.length !== userProfile.length) {
            return { value: null, isOk: false, error: `Dimension mismatch on syllabus ${syllabus.id}` };
        }
        
        const mag = this.calculateMagnitude(syllabus.profile);
        if (mag === 0) continue; // Skip bad distributions
        
        const dot = this.calculateDotProduct(userProfile, syllabus.profile);
        const sim = dot / (userMag * mag);
        
        if (sim > highestSim) {
             highestSim = sim;
             bestMatchId = syllabus.id;
        }
    }
    
    if (bestMatchId === "") {
        return { value: null, isOk: false, error: "Failed to find any viable matches." };
    }

    return { value: bestMatchId, isOk: true, error: null };
  }
}
