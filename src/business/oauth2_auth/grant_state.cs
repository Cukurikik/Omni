using System;

namespace Omni.Business.OAuth2Auth
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public enum GrantState { Initiated, CodeIssued, TokenIssued, Expired }

    public class StateMachine
    {
        public OmniResult<GrantState> TransitionState(GrantState current, string action)
        {
            // Strict OAuth2 Grant State Machine Business Rules
            switch (current)
            {
                case GrantState.Initiated:
                    if (action == "issue_code") return new OmniResult<GrantState>(GrantState.CodeIssued);
                    break;
                case GrantState.CodeIssued:
                    if (action == "exchange_token") return new OmniResult<GrantState>(GrantState.TokenIssued);
                    break;
                case GrantState.TokenIssued:
                    if (action == "expire") return new OmniResult<GrantState>(GrantState.Expired);
                    // Refreshing a token keeps it in TokenIssued state
                    if (action == "refresh_token") return new OmniResult<GrantState>(GrantState.TokenIssued);
                    break;
            }

            return new OmniResult<GrantState>(new InvalidOperationException($"Invalid state transition from {current} via action {action}"));
        }
    }
}
