// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// SpaCy Dependency Parser (OMNI Zero-Mock Implementation)
// Implements deterministic projective dependency tree validation logic.

export type Result<T> = 
  | { value: T; isOk: true; error: null }
  | { value: null; isOk: false; error: string };

export type DependencyArc = {
    headIndex: number;
    childIndex: number;
};

export class DependencyParserEngine {
   
   // Validates whether a given dependency graph is projective mathematically
   // A tree is projective if there are no crossing dependency arcs.
   public isProjective(nodesCount: number, arcs: DependencyArc[]): Result<boolean> {
       if (nodesCount <= 0) {
            return { value: null, isOk: false, error: "Count of nodes must be positive." };
       }
       if (arcs.length === 0) {
            return { value: true, isOk: true, error: null }; // 0 arcs mathematically projective
       }
       
       for (let i = 0; i < arcs.length; i++) {
            const arc1 = arcs[i];
            
            // Bounds check
            if (arc1.headIndex < 0 || arc1.headIndex >= nodesCount ||
                arc1.childIndex < 0 || arc1.childIndex >= nodesCount) {
                 return { value: null, isOk: false, error: "Arc index out of bounds." };
            }
            
            const min1 = Math.min(arc1.headIndex, arc1.childIndex);
            const max1 = Math.max(arc1.headIndex, arc1.childIndex);
            
            for (let j = i + 1; j < arcs.length; j++) {
                 const arc2 = arcs[j];
                 const min2 = Math.min(arc2.headIndex, arc2.childIndex);
                 const max2 = Math.max(arc2.headIndex, arc2.childIndex);
                 
                 // Arcs cross if: min1 < min2 < max1 < max2 OR min2 < min1 < max2 < max1
                 const condition1 = min1 < min2 && min2 < max1 && max1 < max2;
                 const condition2 = min2 < min1 && min1 < max2 && max2 < max1;
                 
                 if (condition1 || condition2) {
                     return { value: false, isOk: true, error: null }; // Crossing arc found -> non-projective
                 }
            }
       }
       
       return { value: true, isOk: true, error: null }; // Projective
   }
}
