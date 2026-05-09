// moe_kb_tricks_lifecycle.cs — Domain
// Layer: Domain — KB Tricks Lifecycle Management
// Inspired by: kb-tricks (Composable skills for full KB lifecycle)

using System;
using System.Collections.Generic;

namespace Omni.Domain.MoE
{
    public enum KBLifecycleState
    {
        DRAFT,
        REVIEW_PENDING,
        PUBLISHED,
        ARCHIVED,
        POSTMORTEM
    }

    public class KnowledgeBaseDocument
    {
        public Guid DocumentId { get; private set; }
        public string Title { get; private set; }
        public string MarkdownContent { get; private set; }
        public KBLifecycleState State { get; private set; }
        public DateTime LastUpdated { get; private set; }

        public KnowledgeBaseDocument(string title, string content)
        {
            DocumentId = Guid.NewGuid();
            Title = title;
            MarkdownContent = content;
            State = KBLifecycleState.DRAFT;
            LastUpdated = DateTime.UtcNow;
        }

        // Domain Rule: Cannot jump straight to published
        public void SubmitForReview()
        {
            if (State != KBLifecycleState.DRAFT)
                throw new InvalidOperationException("Only DRAFT documents can be submitted for review.");
            
            State = KBLifecycleState.REVIEW_PENDING;
            LastUpdated = DateTime.UtcNow;
        }

        public void Publish(string reviewerId)
        {
            if (State != KBLifecycleState.REVIEW_PENDING)
                throw new InvalidOperationException("Document must be reviewed before publishing.");
            if (string.IsNullOrWhiteSpace(reviewerId))
                throw new ArgumentException("Reviewer ID is required.");

            State = KBLifecycleState.PUBLISHED;
            LastUpdated = DateTime.UtcNow;
        }
    }
}
