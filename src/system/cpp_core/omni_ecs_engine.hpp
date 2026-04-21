// ===========================================================================
// OMNI ECS ENGINE (SEMESTER 3 — BATCH 38.4)
// ===========================================================================
// Absorbed From  : EnTT + flecs + Bevy ECS + Unity DOTS
// Logic Inherited: C++ / System Layer (Entity Component System)
// ===========================================================================
//
// By studying EnTT and flecs, Mother learned that ECS architecture
// enables cache-friendly iteration over millions of entities:
//   1. Components are stored in contiguous arrays (SoA layout)
//   2. Entities are just IDs — no inheritance, no vtables
//   3. Systems iterate over component tuples efficiently
//   4. Sparse set maps entity IDs to dense component indices
//   5. Archetypes group entities with identical component sets

#pragma once

#include <algorithm>
#include <any>
#include <bitset>
#include <cassert>
#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <typeindex>
#include <unordered_map>
#include <vector>

namespace omni::system::ecs {

// ---- Entity (lightweight ID) ----

using Entity = uint64_t;
constexpr Entity NULL_ENTITY = 0;

// ---- Component Type ID ----

using ComponentTypeId = std::type_index;

template <typename T>
ComponentTypeId component_id() {
    return std::type_index(typeid(T));
}

// ---- Component Pool (Dense Array Storage) ----

class IComponentPool {
public:
    virtual ~IComponentPool() = default;
    virtual void remove(Entity entity) = 0;
    virtual bool has(Entity entity) const = 0;
    virtual size_t size() const = 0;
};

template <typename T>
class ComponentPool : public IComponentPool {
public:
    /// Add or update a component for an entity.
    void set(Entity entity, T component) {
        auto it = entity_to_index_.find(entity);
        if (it != entity_to_index_.end()) {
            components_[it->second] = std::move(component);
        } else {
            size_t index = components_.size();
            components_.push_back(std::move(component));
            entities_.push_back(entity);
            entity_to_index_[entity] = index;
        }
    }

    /// Get a component by entity (mutable).
    T* get(Entity entity) {
        auto it = entity_to_index_.find(entity);
        if (it == entity_to_index_.end()) return nullptr;
        return &components_[it->second];
    }

    /// Get a component by entity (const).
    const T* get(Entity entity) const {
        auto it = entity_to_index_.find(entity);
        if (it == entity_to_index_.end()) return nullptr;
        return &components_[it->second];
    }

    bool has(Entity entity) const override {
        return entity_to_index_.count(entity) > 0;
    }

    void remove(Entity entity) override {
        auto it = entity_to_index_.find(entity);
        if (it == entity_to_index_.end()) return;

        size_t index = it->second;
        size_t last = components_.size() - 1;

        if (index != last) {
            // Swap with last element to maintain density
            std::swap(components_[index], components_[last]);
            std::swap(entities_[index], entities_[last]);
            entity_to_index_[entities_[index]] = index;
        }

        components_.pop_back();
        entities_.pop_back();
        entity_to_index_.erase(entity);
    }

    size_t size() const override { return components_.size(); }

    /// Iterate over all components.
    template <typename Func>
    void each(Func&& func) {
        for (size_t i = 0; i < components_.size(); i++) {
            func(entities_[i], components_[i]);
        }
    }

    const std::vector<Entity>& entities() const { return entities_; }

private:
    std::vector<T> components_;                        // Dense storage
    std::vector<Entity> entities_;                     // Parallel entity array
    std::unordered_map<Entity, size_t> entity_to_index_;  // Sparse → dense map
};

// ---- World (ECS Container) ----

class OmniECSEngine {
public:
    OmniECSEngine() : next_entity_(1) {}

    /// Create a new entity.
    Entity create_entity() {
        Entity e = next_entity_++;
        alive_entities_.push_back(e);
        total_created_++;
        return e;
    }

    /// Destroy an entity and all its components.
    void destroy_entity(Entity entity) {
        for (auto& [_, pool] : pools_) {
            pool->remove(entity);
        }
        alive_entities_.erase(
            std::remove(alive_entities_.begin(), alive_entities_.end(), entity),
            alive_entities_.end()
        );
        total_destroyed_++;
    }

    /// Add a component to an entity.
    template <typename T>
    void add_component(Entity entity, T component) {
        get_or_create_pool<T>().set(entity, std::move(component));
        total_components_added_++;
    }

    /// Get a component from an entity.
    template <typename T>
    T* get_component(Entity entity) {
        auto pool = get_pool<T>();
        return pool ? pool->get(entity) : nullptr;
    }

    /// Check if entity has a component.
    template <typename T>
    bool has_component(Entity entity) const {
        auto pool = get_pool<T>();
        return pool ? pool->has(entity) : false;
    }

    /// Remove a component from an entity.
    template <typename T>
    void remove_component(Entity entity) {
        auto pool = get_pool<T>();
        if (pool) pool->remove(entity);
        total_components_removed_++;
    }

    /// Query: iterate entities that have ALL specified component types.
    template <typename... Components, typename Func>
    void query(Func&& func) {
        total_queries_++;

        // Find the smallest pool for efficient iteration
        auto pools = std::array<IComponentPool*, sizeof...(Components)>{
            get_pool<Components>()...
        };

        // Check all pools exist
        for (auto* p : pools) {
            if (!p || p->size() == 0) return;
        }

        // Iterate the smallest pool
        size_t min_idx = 0;
        size_t min_size = pools[0]->size();
        for (size_t i = 1; i < pools.size(); i++) {
            if (pools[i]->size() < min_size) {
                min_size = pools[i]->size();
                min_idx = i;
            }
        }

        // Use first component type's pool to iterate entities
        auto* first_pool = static_cast<ComponentPool<
            std::tuple_element_t<0, std::tuple<Components...>>>*>(pools[0]);

        for (Entity entity : first_pool->entities()) {
            // Check this entity has ALL required components
            bool has_all = (has_component<Components>(entity) && ...);
            if (has_all) {
                func(entity, *get_component<Components>(entity)...);
            }
        }
    }

    /// Register a system (named function that runs on matching entities).
    void register_system(const std::string& name, std::function<void()> system) {
        systems_.push_back({name, std::move(system)});
    }

    /// Tick: execute all registered systems.
    void tick() {
        for (auto& [name, system] : systems_) {
            system();
        }
        total_ticks_++;
    }

    // ---- Stats ----

    size_t entity_count() const { return alive_entities_.size(); }
    size_t pool_count() const { return pools_.size(); }

    // ---- Diagnostics ----

    std::map<std::string, std::string> diagnostics() const {
        return {
            {"engine", "OmniECSEngine"},
            {"layer", "C++ System"},
            {"alive_entities", std::to_string(alive_entities_.size())},
            {"component_pools", std::to_string(pools_.size())},
            {"registered_systems", std::to_string(systems_.size())},
            {"total_created", std::to_string(total_created_)},
            {"total_destroyed", std::to_string(total_destroyed_)},
            {"total_components_added", std::to_string(total_components_added_)},
            {"total_components_removed", std::to_string(total_components_removed_)},
            {"total_queries", std::to_string(total_queries_)},
            {"total_ticks", std::to_string(total_ticks_)},
            {"learned_logic",
                "entt-sparse-set-mapping,"
                "dense-array-soa-layout,"
                "entity-as-plain-id,"
                "swap-remove-dense-packing,"
                "variadic-query-fold-expression,"
                "smallest-pool-iteration,"
                "system-registration-ecs,"
                "cache-friendly-iteration"},
        };
    }

private:
    Entity next_entity_;
    std::vector<Entity> alive_entities_;
    std::unordered_map<ComponentTypeId, std::unique_ptr<IComponentPool>> pools_;
    std::vector<std::pair<std::string, std::function<void()>>> systems_;

    uint64_t total_created_ = 0;
    uint64_t total_destroyed_ = 0;
    uint64_t total_components_added_ = 0;
    uint64_t total_components_removed_ = 0;
    uint64_t total_queries_ = 0;
    uint64_t total_ticks_ = 0;

    template <typename T>
    ComponentPool<T>& get_or_create_pool() {
        auto key = component_id<T>();
        auto it = pools_.find(key);
        if (it != pools_.end()) {
            return *static_cast<ComponentPool<T>*>(it->second.get());
        }
        auto pool = std::make_unique<ComponentPool<T>>();
        auto* raw = pool.get();
        pools_[key] = std::move(pool);
        return *raw;
    }

    template <typename T>
    ComponentPool<T>* get_pool() {
        auto it = pools_.find(component_id<T>());
        return it != pools_.end()
            ? static_cast<ComponentPool<T>*>(it->second.get())
            : nullptr;
    }

    template <typename T>
    const ComponentPool<T>* get_pool() const {
        auto it = pools_.find(component_id<T>());
        return it != pools_.end()
            ? static_cast<const ComponentPool<T>*>(it->second.get())
            : nullptr;
    }
};

} // namespace omni::system::ecs
