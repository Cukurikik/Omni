// ===========================================================================
// OMNI SYSTEM LAYER — C++ RUNTIME REFLECTION ENGINE
// ===========================================================================
// Source Paradigm : AustinBrunkhorst/CPP-Reflection
// Domain Layer   : System (Template metaprogramming, RTTI)
// Language        : C++
// Function        : Runtime type introspection system providing dynamic
//                   field enumeration, method invocation, and type registry
//                   for serialization/deserialization of arbitrary C++ objects
// ===========================================================================

#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include <memory>
#include <cstdint>
#include <cstdio>

namespace omni::reflection {

// ---- Field Descriptor -----------------------------------------------------

enum class FieldType {
    Int32,
    Int64,
    Float32,
    Float64,
    String,
    Bool,
    Custom,
};

struct FieldDescriptor {
    std::string name;
    FieldType   type;
    size_t      offset;       // byte offset from struct base
    size_t      size;         // sizeof the field
    bool        is_pointer;
    std::string custom_type;  // non-empty if FieldType::Custom
};

// ---- Method Descriptor ----------------------------------------------------

using MethodInvoker = std::function<void(void* instance, void* args, void* ret)>;

struct MethodDescriptor {
    std::string   name;
    std::string   return_type;
    std::vector<std::string> param_types;
    MethodInvoker invoker;
};

// ---- Type Descriptor (mirrors CPP-Reflection TypeData) --------------------

struct TypeDescriptor {
    std::string  name;
    size_t       size;          // total sizeof
    size_t       alignment;
    std::string  base_type;    // parent class (empty if none)
    std::vector<FieldDescriptor>  fields;
    std::vector<MethodDescriptor> methods;

    /// Lookup a field by name.
    const FieldDescriptor* find_field(const std::string& field_name) const {
        for (const auto& f : fields) {
            if (f.name == field_name) return &f;
        }
        return nullptr;
    }

    /// Lookup a method by name.
    const MethodDescriptor* find_method(const std::string& method_name) const {
        for (const auto& m : methods) {
            if (m.name == method_name) return &m;
        }
        return nullptr;
    }
};

// ---- Global Type Registry -------------------------------------------------

class TypeRegistry {
public:
    static TypeRegistry& instance() {
        static TypeRegistry reg;
        return reg;
    }

    /// Register a type.
    void register_type(const TypeDescriptor& desc) {
        printf("[REFLECT-OMNI-CPP] Registered type: %s (%zu bytes, %zu fields, %zu methods)\n",
               desc.name.c_str(), desc.size, desc.fields.size(), desc.methods.size());
        types_[desc.name] = desc;
    }

    /// Lookup a type by name.
    const TypeDescriptor* lookup(const std::string& name) const {
        auto it = types_.find(name);
        if (it != types_.end()) return &it->second;
        return nullptr;
    }

    /// Get all registered types.
    std::vector<std::string> all_type_names() const {
        std::vector<std::string> names;
        names.reserve(types_.size());
        for (const auto& kv : types_) {
            names.push_back(kv.first);
        }
        return names;
    }

    /// Dynamic field read (unsafe, raw memory access).
    template<typename T>
    T read_field(void* instance, const FieldDescriptor& field) const {
        T value;
        std::memcpy(&value, static_cast<char*>(instance) + field.offset, sizeof(T));
        return value;
    }

    /// Dynamic field write (unsafe, raw memory access).
    template<typename T>
    void write_field(void* instance, const FieldDescriptor& field, const T& value) {
        std::memcpy(static_cast<char*>(instance) + field.offset, &value, sizeof(T));
    }

    /// Serialize all fields of a registered type to JSON-like string.
    std::string serialize_to_json(const std::string& type_name, void* instance) const {
        const TypeDescriptor* desc = lookup(type_name);
        if (!desc) return "{}";

        std::string json = "{";
        for (size_t i = 0; i < desc->fields.size(); ++i) {
            const auto& f = desc->fields[i];
            json += "\"" + f.name + "\": ";

            switch (f.type) {
                case FieldType::Int32: {
                    int32_t val = read_field<int32_t>(instance, f);
                    json += std::to_string(val);
                    break;
                }
                case FieldType::Float64: {
                    double val = read_field<double>(instance, f);
                    json += std::to_string(val);
                    break;
                }
                case FieldType::Bool: {
                    bool val = read_field<bool>(instance, f);
                    json += val ? "true" : "false";
                    break;
                }
                default:
                    json += "\"(complex)\"";
                    break;
            }
            if (i + 1 < desc->fields.size()) json += ", ";
        }
        json += "}";
        return json;
    }

private:
    TypeRegistry() {
        printf("[REFLECT-OMNI-CPP] TypeRegistry initialized.\n");
    }
    std::unordered_map<std::string, TypeDescriptor> types_;
};

// ---- Registration Macro (mirrors CPP-Reflection REGISTER_TYPE) ----------------------

// Usage:
// TypeDescriptor desc;
// desc.name = "Player";
// desc.size = sizeof(Player);
// desc.fields.push_back({"health", FieldType::Int32, offsetof(Player, health), sizeof(int32_t), false, ""});
// TypeRegistry::instance().register_type(desc);

} // namespace omni::reflection

// int main() {
//     using namespace omni::reflection;
//     struct Player { int32_t health; double speed; bool alive; };
//     TypeDescriptor desc;
//     desc.name = "Player"; desc.size = sizeof(Player); desc.alignment = alignof(Player);
//     desc.fields.push_back({"health", FieldType::Int32, offsetof(Player, health), sizeof(int32_t), false, ""});
//     desc.fields.push_back({"speed", FieldType::Float64, offsetof(Player, speed), sizeof(double), false, ""});
//     desc.fields.push_back({"alive", FieldType::Bool, offsetof(Player, alive), sizeof(bool), false, ""});
//     TypeRegistry::instance().register_type(desc);
//     Player p{100, 3.5, true};
//     auto json = TypeRegistry::instance().serialize_to_json("Player", &p);
//     printf("Serialized: %s\n", json.c_str());
// }
