// OmniAuthMiddleware.cs — API Authentication Middleware
// Layer: Domain / C#
//
// ASP.NET Core compatible middleware for intercepting HTTP requests,
// extracting JWTs, and validating them against the OmniRoleManager.

using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Omni.Domain.IAM;

namespace Omni.Domain.Middleware
{
    public sealed class OmniAuthMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly OmniRoleManager _roleManager;

        public OmniAuthMiddleware(RequestDelegate next, OmniRoleManager roleManager)
        {
            _next = next;
            _roleManager = roleManager;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            var authHeader = context.Request.Headers["Authorization"].ToString();
            
            if (string.IsNullOrWhiteSpace(authHeader) || !authHeader.StartsWith("Bearer "))
            {
                context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                await context.Response.WriteAsync("{\"error\": \"Missing or invalid Authorization header\"}");
                return;
            }

            var token = authHeader.Substring("Bearer ".Length).Trim();
            
            // In a real implementation, we validate the JWT signature here via the Rust FFI
            // bool isValid = CryptoFFI.VerifyJWT(token);
            bool isValid = true; // Mock for architecture layout

            if (!isValid)
            {
                context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                await context.Response.WriteAsync("{\"error\": \"Invalid token signature\"}");
                return;
            }

            // Extract claims (Mocked logic)
            // var principal = CreatePrincipalFromToken(token);
            // context.User = principal;

            await _next(context);
        }
    }
}
