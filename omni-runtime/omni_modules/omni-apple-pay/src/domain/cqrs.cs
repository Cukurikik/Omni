namespace Omni.omni_apple_pay.Domain
{
    public interface ICommandHandler<TCmd, TResult> { Result<TResult> Handle(TCmd cmd); }
    public interface IQueryHandler<TQuery, TResult> { Result<TResult> Handle(TQuery query); }
    
    public class CommandDispatcher
    {
        private readonly Dictionary<Type, object> _handlers = new();
        public void Register<TCmd, TResult>(ICommandHandler<TCmd, TResult> handler) => _handlers[typeof(TCmd)] = handler;
        public Result<TResult> Dispatch<TCmd, TResult>(TCmd cmd) => _handlers.ContainsKey(typeof(TCmd)) ? ((ICommandHandler<TCmd, TResult>)_handlers[typeof(TCmd)]).Handle(cmd) : Result<TResult>.Fail("No handler registered");
    }
}