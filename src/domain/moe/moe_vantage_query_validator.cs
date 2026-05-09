// moe_vantage_query_validator.cs — Domain Layer: Vantage Query Validator
// C# Domain-Driven Design logic for ensuring generated SQL is syntactically safe.

using System;
using System.Text.RegularExpressions;

namespace Omni.Domain.MoE.Vantage
{
    public class SqlValidator
    {
        private static readonly string[] DangerousKeywords = { "DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE" };

        public bool IsQuerySafe(string sqlQuery, out string errorMessage)
        {
            if (string.IsNullOrWhiteSpace(sqlQuery))
            {
                errorMessage = "Query cannot be empty.";
                return false;
            }

            string upperQuery = sqlQuery.ToUpperInvariant();

            // Strict Read-Only Policy for Agentic SQL generation
            foreach (var keyword in DangerousKeywords)
            {
                // Regex checks for word boundaries to avoid matching partial words
                if (Regex.IsMatch(upperQuery, $@"\b{keyword}\b"))
                {
                    errorMessage = $"Query contains unsafe DML/DDL keyword: {keyword}";
                    return false;
                }
            }

            // Ensure it's a SELECT query
            if (!upperQuery.TrimStart().StartsWith("SELECT"))
            {
                errorMessage = "Only SELECT queries are permitted.";
                return false;
            }

            errorMessage = string.Empty;
            return true;
        }
    }
}
