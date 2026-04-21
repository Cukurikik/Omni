// ===========================================================================
// OMNI TEMPLATE METAPROGRAMMING ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : C++ Templates + SFINAE + Concepts + constexpr + STL
// Logic Inherited: C++ / System Layer (Compile-Time Computation & Type Traits)
// ===========================================================================
//
// By studying C++ TMP and Concepts (C++20), Mother learned:
//   1. Templates enable generic programming resolved at compile time
//   2. SFINAE (Substitution Failure Is Not An Error) selects overloads
//   3. constexpr computes values at compile time
//   4. Concepts constrain template parameters declaratively
//   5. Type traits inspect and transform types at compile time

#pragma once

#include <utility>
#include <type_traits>
#include <memory>
#include <string>
#include <vector>
#include <functional>
#include <atomic>
#include <chrono>
#include <optional>
#include <variant>

namespace omni::system::cpp {

// ============================================================
// PART 1: Type Traits (Compile-Time Type Inspection)
// ============================================================

/// Check if T has a method `size()`.
template <typename T, typename = void>
struct has_size : std::false_type {};

template <typename T>
struct has_size<T, std::void_t<decltype(std::declval<T>().size())>>
    : std::true_type {};

template <typename T>
inline constexpr bool has_size_v = has_size<T>::value;

/// Check if T is iterable (has begin/end).
template <typename T, typename = void>
struct is_iterable : std::false_type {};

template <typename T>
struct is_iterable<T, std::void_t<
    decltype(std::begin(std::declval<T>())),
    decltype(std::end(std::declval<T>()))
>> : std::true_type {};

template <typename T>
inline constexpr bool is_iterable_v = is_iterable<T>::value;

/// Check if T is streamable (has operator<<).
template <typename T, typename = void>
struct is_streamable : std::false_type {};

template <typename T>
struct is_streamable<T, std::void_t<
    decltype(std::declval<std::ostream&>() << std::declval<T>())
>> : std::true_type {};

template <typename T>
inline constexpr bool is_streamable_v = is_streamable<T>::value;

// ============================================================
// PART 2: Concepts (C++20 Constraints)
// ============================================================

/// Concept: T must be numeric.
template <typename T>
concept Numeric = std::is_arithmetic_v<T>;

/// Concept: T must be equality comparable.
template <typename T>
concept EqualityComparable = requires(T a, T b) {
    { a == b } -> std::convertible_to<bool>;
    { a != b } -> std::convertible_to<bool>;
};

/// Concept: T must be hashable.
template <typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
};

/// Concept: T must be printable.
template <typename T>
concept Printable = requires(T a, std::ostream& os) {
    { os << a } -> std::same_as<std::ostream&>;
};

/// Concept: Container type.
template <typename T>
concept Container = requires(T c) {
    typename T::value_type;
    { c.size() } -> std::convertible_to<std::size_t>;
    { c.begin() };
    { c.end() };
};

// ============================================================
// PART 3: constexpr Compile-Time Computation
// ============================================================

/// Compile-time factorial.
constexpr unsigned long long factorial(unsigned n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

/// Compile-time fibonacci.
constexpr unsigned long long fibonacci(unsigned n) {
    if (n <= 1) return n;
    unsigned long long a = 0, b = 1;
    for (unsigned i = 2; i <= n; ++i) {
        unsigned long long tmp = a + b;
        a = b;
        b = tmp;
    }
    return b;
}

/// Compile-time power.
constexpr double power(double base, unsigned exp) {
    double result = 1.0;
    for (unsigned i = 0; i < exp; ++i) {
        result *= base;
    }
    return result;
}

/// Compile-time string length.
constexpr std::size_t ct_strlen(const char* str) {
    std::size_t len = 0;
    while (str[len] != '\0') ++len;
    return len;
}

/// Compile-time max.
template <Numeric T>
constexpr T ct_max(T a, T b) {
    return a > b ? a : b;
}

/// Compile-time clamp.
template <Numeric T>
constexpr T ct_clamp(T value, T lo, T hi) {
    return value < lo ? lo : (value > hi ? hi : value);
}

// ============================================================
// PART 4: CRTP (Curiously Recurring Template Pattern)
// ============================================================

/// CRTP base for static polymorphism (no virtual overhead).
template <typename Derived>
class CRTPBase {
public:
    void interface_method() {
        static_cast<Derived*>(this)->implementation();
    }

    std::string type_name() const {
        return typeid(Derived).name();
    }
};

// ============================================================
// PART 5: Type-Safe Variant Visitor
// ============================================================

/// Overloaded: combines multiple lambdas into a single visitor.
template <typename... Ts>
struct Overloaded : Ts... {
    using Ts::operator()...;
};

/// Deduction guide (C++17).
template <typename... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;

/// OmniVariant: enhanced std::variant with pattern matching.
template <typename... Ts>
class OmniVariant {
    std::variant<Ts...> inner;

public:
    template <typename T>
    OmniVariant(T&& value) : inner(std::forward<T>(value)) {}

    /// Pattern match with visitor.
    template <typename... Visitors>
    auto match(Visitors&&... visitors) const {
        return std::visit(Overloaded{std::forward<Visitors>(visitors)...}, inner);
    }

    /// Check if holds a specific type.
    template <typename T>
    bool holds() const {
        return std::holds_alternative<T>(inner);
    }

    /// Get value of specific type (throws if wrong type).
    template <typename T>
    const T& get() const {
        return std::get<T>(inner);
    }

    /// Try to get value (returns nullptr if wrong type).
    template <typename T>
    const T* get_if() const {
        return std::get_if<T>(&inner);
    }

    /// Index of current type.
    std::size_t index() const {
        return inner.index();
    }
};

// ============================================================
// PART 6: Smart Pointer Utilities
// ============================================================

/// RAII unique pointer with custom deleter and metrics.
template <typename T>
class OmniUniquePtr {
    std::unique_ptr<T> ptr;
    static inline std::atomic<uint64_t> total_created{0};
    static inline std::atomic<uint64_t> total_destroyed{0};

public:
    explicit OmniUniquePtr(T* raw) : ptr(raw) {
        total_created.fetch_add(1, std::memory_order_relaxed);
    }

    ~OmniUniquePtr() {
        if (ptr) total_destroyed.fetch_add(1, std::memory_order_relaxed);
    }

    // Move-only semantics
    OmniUniquePtr(OmniUniquePtr&& other) noexcept = default;
    OmniUniquePtr& operator=(OmniUniquePtr&& other) noexcept = default;
    OmniUniquePtr(const OmniUniquePtr&) = delete;
    OmniUniquePtr& operator=(const OmniUniquePtr&) = delete;

    T& operator*() const { return *ptr; }
    T* operator->() const { return ptr.get(); }
    T* get() const { return ptr.get(); }
    explicit operator bool() const { return ptr != nullptr; }

    T* release() { return ptr.release(); }
    void reset(T* raw = nullptr) { ptr.reset(raw); }

    static uint64_t get_total_created() { return total_created.load(); }
    static uint64_t get_total_destroyed() { return total_destroyed.load(); }
};

/// Factory function.
template <typename T, typename... Args>
OmniUniquePtr<T> make_omni_unique(Args&&... args) {
    return OmniUniquePtr<T>(new T(std::forward<Args>(args)...));
}

// ============================================================
// Diagnostics
// ============================================================

struct OmniTMPDiagnostics {
    static auto diagnostics() {
        struct Result {
            const char* engine = "OmniTemplateMetaprogrammingEngine";
            const char* layer = "C++ System";
            std::vector<std::string> components = {
                "TypeTraits", "Concepts", "constexpr",
                "CRTP", "OmniVariant", "OmniUniquePtr"
            };
            std::vector<std::string> learned_logic = {
                "sfinae-substitution-overload",
                "concepts-declarative-constraints",
                "constexpr-compile-time-compute",
                "crtp-static-polymorphism",
                "variant-visitor-pattern-match",
                "overloaded-lambda-combiner",
                "move-semantics-unique-ptr",
                "type-traits-void-t-detection"
            };
        };
        return Result{};
    }
};

} // namespace omni::system::cpp
