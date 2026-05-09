using System;

namespace Omni.Domain.Education
{
    public class AICourseNotesManager
    {
        public string CourseId { get; }

        public AICourseNotesManager(string courseId)
        {
            CourseId = courseId;
        }
    }
}
