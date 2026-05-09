// moe_comfyui_job_queue.cs — Domain
// Layer: Domain — ComfyUI Job Queue
// Inspired by: Eric-Alice-T2V-ComfyUI-Wrapper

using System;
using System.Collections.Concurrent;

namespace Omni.Domain.MoE
{
    public class ComfyJob
    {
        public Guid JobId { get; private set; }
        public string Prompt { get; private set; }
        public int VramRequiredGb { get; private set; }
        public string Status { get; set; }

        public ComfyJob(string prompt, int vramRequired)
        {
            JobId = Guid.NewGuid();
            Prompt = prompt;
            VramRequiredGb = vramRequired;
            Status = "QUEUED";
        }
    }

    public class T2VJobQueue
    {
        private ConcurrentQueue<ComfyJob> _queue = new ConcurrentQueue<ComfyJob>();
        public int TotalAvailableVramGb { get; private set; }

        public T2VJobQueue(int totalVram)
        {
            TotalAvailableVramGb = totalVram;
        }

        public void SubmitJob(ComfyJob job)
        {
            if (job.VramRequiredGb > TotalAvailableVramGb)
            {
                throw new InvalidOperationException("Job requires more VRAM than node capacity.");
            }
            _queue.Enqueue(job);
        }

        public ComfyJob DispatchNext(int currentFreeVram)
        {
            if (_queue.TryPeek(out ComfyJob nextJob))
            {
                if (currentFreeVram >= nextJob.VramRequiredGb)
                {
                    _queue.TryDequeue(out ComfyJob dispatched);
                    dispatched.Status = "PROCESSING";
                    return dispatched;
                }
            }
            return null; // Resource constrained, wait.
        }
    }
}
