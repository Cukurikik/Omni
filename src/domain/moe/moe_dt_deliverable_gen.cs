// moe_dt_deliverable_gen.cs — Domain Layer: Digital Transformation Deliverable Generator
// C# document structure generator formatting consultant bot data into structured reports.

using System.Collections.Generic;
using System.Text;

namespace Omni.Domain.MoE.DigitalTransformation
{
    public class ReportGenerator
    {
        public string GenerateMarkdownReport(string clientName, List<string> painPoints, List<string> recommendations)
        {
            var sb = new StringBuilder();
            sb.AppendLine($"# Digital Transformation Strategic Report: {clientName}");
            sb.AppendLine("## Identified Bottlenecks");
            
            foreach(var point in painPoints)
            {
                sb.AppendLine($"- {point}");
            }

            sb.AppendLine();
            sb.AppendLine("## Core Recommendations (MoE AI Generated)");
            
            foreach(var rec in recommendations)
            {
                sb.AppendLine($"- [ ] {rec}");
            }

            return sb.ToString();
        }
    }
}
