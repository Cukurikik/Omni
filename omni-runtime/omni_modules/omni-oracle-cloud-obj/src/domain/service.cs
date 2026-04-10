namespace Omni.omni_oracle_cloud_obj.Domain
{
    public class DomainService
    {
        private readonly IRepository _repo;
        private readonly IValidator _validator;
        private readonly IEventBus _eventBus;
        
        public DomainService(IRepository repo, IValidator validator, IEventBus eventBus) { _repo = repo; _validator = validator; _eventBus = eventBus; }
        
        public Result<T> Execute<T>(Command<T> cmd) where T : class
        {
            var validation = _validator.Validate(cmd);
            if (!validation.IsValid) return Result<T>.Fail(validation.Error);
            var result = _repo.Execute(cmd);
            _eventBus.Publish(new DomainEvent(cmd.Name, result));
            return Result<T>.Ok(result);
        }
        
        public Result<T> Query<T>(Query<T> query) where T : class { return _repo.Query(query); }
    }
    
    public class Result<T>
    {
        public bool Success { get; private set; }
        public T Value { get; private set; }
        public string Error { get; private set; }
        public static Result<T> Ok(T val) => new Result<T> { Success = true, Value = val };
        public static Result<T> Fail(string err) => new Result<T> { Success = false, Error = err };
    }
    
    public interface IRepository { T Execute<T>(Command<T> cmd) where T : class; Result<T> Query<T>(Query<T> query) where T : class; }
    public interface IValidator { ValidationResult Validate<T>(Command<T> cmd) where T : class; }
    public interface IEventBus { void Publish(DomainEvent evt); void Subscribe(string topic, Action<DomainEvent> handler); }
    public record Command<T>(string Name, T Payload) where T : class;
    public record Query<T>(string Name, string Filter) where T : class;
    public record DomainEvent(string Name, object Payload);
    public record ValidationResult(bool IsValid, string Error);
}