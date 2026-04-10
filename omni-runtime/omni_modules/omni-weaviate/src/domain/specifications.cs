namespace Omni.omni_weaviate.Domain
{
    public abstract class Specification<T> { public abstract bool IsSatisfiedBy(T entity); }
    public class AndSpecification<T> : Specification<T>
    {
        private readonly Specification<T> _a, _b;
        public AndSpecification(Specification<T> a, Specification<T> b) { _a = a; _b = b; }
        public override bool IsSatisfiedBy(T e) => _a.IsSatisfiedBy(e) && _b.IsSatisfiedBy(e);
    }
    public class OrSpecification<T> : Specification<T>
    {
        private readonly Specification<T> _a, _b;
        public OrSpecification(Specification<T> a, Specification<T> b) { _a = a; _b = b; }
        public override bool IsSatisfiedBy(T e) => _a.IsSatisfiedBy(e) || _b.IsSatisfiedBy(e);
    }
    public class NotSpecification<T> : Specification<T>
    {
        private readonly Specification<T> _inner;
        public NotSpecification(Specification<T> inner) { _inner = inner; }
        public override bool IsSatisfiedBy(T e) => !_inner.IsSatisfiedBy(e);
    }
}