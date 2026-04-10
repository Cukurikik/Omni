namespace Omni.omni_lodash_native.Domain
{
    public class InMemoryRepository : IRepository
    {
        private readonly Dictionary<string, object> _store = new();
        public T Execute<T>(Command<T> cmd) where T : class { _store[cmd.Name] = cmd.Payload; return cmd.Payload; }
        public Result<T> Query<T>(Query<T> query) where T : class { return _store.ContainsKey(query.Name) ? Result<T>.Ok((T)_store[query.Name]) : Result<T>.Fail("Not found"); }
        public void Delete(string key) { _store.Remove(key); }
        public bool Exists(string key) => _store.ContainsKey(key);
        public int Count() => _store.Count;
    }
}