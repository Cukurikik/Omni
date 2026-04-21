// ===========================================================================
// OMNI COMPILE-TIME REFLECTION ENGINE (SEMESTER 3 — BATCH 38.4)
// ===========================================================================
// Absorbed From  : C++20 concepts + CTTI + magic_enum + Boost.Hana
// Logic Inherited: C++ / System Layer (Template Metaprogramming Reflection)
// ===========================================================================
//
// By studying magic_enum and CTTI, Mother learned C++ compile-time
// type introspection patterns:
//   1. constexpr type_name<T>() via __PRETTY_FUNCTION__/__FUNCSIG__
//   2. std::variant + std::visit for type-safe unions
//   3. Concepts constrain template parameters at compile time
//   4. Fold expressions iterate over parameter packs
//   5. if constexpr enables branch selection at compile time

#pragma once

#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <variant>
#include <vector>

namespace omni::system::reflection {

// ---- Compile-Time Type Name Extraction ----

template <typename T>
constexpr std::string_view type_name() {
#if defined(__clang__) || defined(__GNUC__)
    // __PRETTY_FUNCTION__ = "std::string_view type_name() [T = int]"
    constexpr std::string_view fn = __PRETTY_FUNCTION__;
    constexpr auto start = fn.find("T = ") + 4;
    constexpr auto end = fn.rfind(']');
    return fn.substr(start, end - start);
#elif defined(_MSC_VER)
    // __FUNCSIG__ = "... type_name<int>(void)"
    constexpr std::string_view fn = __FUNCSIG__;
    constexpr auto start = fn.find("type_name<") + 10;
    constexpr auto end = fn.rfind(">(void)");
    return fn.substr(start, end - start);
#else
    return "unknown";
#endif
}

// ---- Type ID (compile-time unique identifier) ----

using TypeId = uint64_t;

constexpr TypeId fnv1a_hash(std::string_view str) {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : str) {
        hash ^= static_cast<uint64_t>(c);
        hash *= 1099511628211ULL;
    }
    return hash;
}

template <typename T>
constexpr TypeId type_id() {
    return fnv1a_hash(type_name<T>());
}

// ---- Concepts (C++20 Compile-Time Constraints) ----

template <typename T>
concept Arithmetic = std::is_arithmetic_v<T>;

template <typename T>
concept StringLike = std::is_convertible_v<T, std::string_view>;

template <typename T>
concept Container = requires(T t) {
    t.begin();
    t.end();
    t.size();
};

template <typename T>
concept Serializable = requires(T t) {
    { t.serialize() } -> std::convertible_to<std::string>;
};

template <typename T>
concept HasDiagnostics = requires(T t) {
    { t.diagnostics() };
};

// ---- Field Descriptor (Runtime Reflection Metadata) ----

struct FieldDescriptor {
    std::string name;
    std::string type_name;
    TypeId type_id;
    size_t offset;
    size_t size;
    bool is_const;
    bool is_pointer;
    bool is_reference;
};

// ---- Type Descriptor ----

struct TypeDescriptor {
    std::string name;
    TypeId id;
    size_t size;
    size_t alignment;
    std::vector<FieldDescriptor> fields;
    bool is_aggregate;
    bool is_trivially_copyable;
    bool is_polymorphic;
};

// ---- Type Registry (Runtime) ----

class TypeRegistry {
public:
    static TypeRegistry& instance() {
        static TypeRegistry reg;
        return reg;
    }

    template <typename T>
    TypeDescriptor& register_type() {
        TypeId tid = type_id<T>();
        auto it = types_.find(tid);
        if (it != types_.end()) return it->second;

        TypeDescriptor desc;
        desc.name = std::string(type_name<T>());
        desc.id = tid;
        desc.size = sizeof(T);
        desc.alignment = alignof(T);
        desc.is_aggregate = std::is_aggregate_v<T>;
        desc.is_trivially_copyable = std::is_trivially_copyable_v<T>;
        desc.is_polymorphic = std::is_polymorphic_v<T>;

        auto [inserted_it, _] = types_.emplace(tid, std::move(desc));
        total_registered_++;
        return inserted_it->second;
    }

    template <typename T>
    TypeDescriptor& add_field(const std::string& field_name,
                               size_t offset, size_t size) {
        TypeId tid = type_id<T>();
        auto it = types_.find(tid);
        if (it == types_.end()) {
            register_type<T>();
            it = types_.find(tid);
        }

        FieldDescriptor field;
        field.name = field_name;
        field.type_name = "auto";
        field.type_id = 0;
        field.offset = offset;
        field.size = size;
        field.is_const = false;
        field.is_pointer = false;
        field.is_reference = false;

        it->second.fields.push_back(std::move(field));
        return it->second;
    }

    std::optional<TypeDescriptor> lookup(TypeId tid) const {
        auto it = types_.find(tid);
        if (it != types_.end()) return it->second;
        return std::nullopt;
    }

    template <typename T>
    std::optional<TypeDescriptor> lookup() const {
        return lookup(type_id<T>());
    }

    size_t type_count() const { return types_.size(); }
    uint64_t total_registered() const { return total_registered_; }

    std::vector<TypeDescriptor> all_types() const {
        std::vector<TypeDescriptor> result;
        result.reserve(types_.size());
        for (const auto& [_, desc] : types_) {
            result.push_back(desc);
        }
        return result;
    }

private:
    TypeRegistry() = default;
    std::map<TypeId, TypeDescriptor> types_;
    uint64_t total_registered_ = 0;
};

// ---- Compile-Time Variant Visitor ----

template <typename... Ts>
struct Overloaded : Ts... {
    using Ts::operator()...;
};
template <typename... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;

template <typename Variant, typename... Visitors>
decltype(auto) match(Variant&& variant, Visitors&&... visitors) {
    return std::visit(
        Overloaded{std::forward<Visitors>(visitors)...},
        std::forward<Variant>(variant)
    );
}

// ---- Fold Expression Utilities ----

template <typename... Args>
constexpr size_t total_size() {
    return (sizeof(Args) + ...);
}

template <typename... Args>
constexpr size_t type_count() {
    return sizeof...(Args);
}

template <typename F, typename... Args>
void for_each_type(F&& f) {
    (f.template operator()<Args>(), ...);
}

// ---- Diagnostics ----

struct ReflectionDiagnostics {
    std::map<std::string, std::string> info;

    ReflectionDiagnostics() {
        auto& reg = TypeRegistry::instance();
        info["engine"] = "OmniCompileTimeReflectionEngine";
        info["layer"] = "C++ System";
        info["registered_types"] = std::to_string(reg.type_count());
        info["total_registrations"] = std::to_string(reg.total_registered());
        info["learned_logic"] = "constexpr-type-name-extraction,"
                                 "fnv1a-compile-time-hash,"
                                 "concepts-template-constraints,"
                                 "variant-visit-pattern-match,"
                                 "overloaded-lambda-visitor,"
                                 "fold-expressions-parameter-pack,"
                                 "if-constexpr-branch-selection,"
                                 "type-registry-singleton";
    }
};

} // namespace omni::system::reflection
