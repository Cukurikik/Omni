namespace Omni.omni_glassmorphism.Domain
{
    public static class EntityMapper
    {
        public static TDest Map<TSrc, TDest>(TSrc src) where TDest : new() { return new TDest(); }
        public static IReadOnlyList<TDest> MapList<TSrc, TDest>(IEnumerable<TSrc> src) where TDest : new() { return src.Select(s => Map<TSrc, TDest>(s)).ToList().AsReadOnly(); }
    }
    
    public interface IMapper<TSrc, TDest> { TDest Map(TSrc source); TSrc ReverseMap(TDest dest); }
}