"""OmniCourseAllocatorEngine for deterministic course registration matching."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniCourseAllocatorEngine(OmniBaseEngine):
    """Production-grade Omni Course Allocator Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def allocate(self, 
                 students: List[Dict[str, Any]], 
                 course_capacities: Dict[str, int]) -> Result[Dict[str, Any], str]:
        """
        Allocates students to courses based on their ordered preferences.
        Students must have: 'id', 'gpa', 'preferences' (list of course codes).
        High GPA gets priority.
        """
        try:
            # Deep copy to maintain determinism
            caps = {k: v for k, v in course_capacities.items()}
            
            # Sort students by GPA descending, then by ID ascending for deterministic resolution
            sorted_students = sorted(
                students, 
                key=lambda x: (-float(x.get('gpa', 0.0)), str(x['id']))
            )

            allocations: Dict[str, str] = {} # student_id -> course_id
            waitlists: Dict[str, List[str]] = {c: [] for c in caps.keys()}

            for student in sorted_students:
                allocated = False
                sid = str(student['id'])
                prefs = student.get('preferences', [])
                
                for course in prefs:
                    if course in caps and caps[course] > 0:
                        allocations[sid] = course
                        caps[course] -= 1
                        allocated = True
                        break
                
                if not allocated and prefs:
                    # Add to waitlist of first choice
                    first_choice = prefs[0]
                    if first_choice in waitlists:
                        waitlists[first_choice].append(sid)

            return Result.ok({
                "allocations": allocations,
                "remaining_capacities": caps,
                "waitlists": waitlists
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniCourseAllocatorEngine",
            "status": "operational",
            "priority": "GPA Descending Fixed"
        }
