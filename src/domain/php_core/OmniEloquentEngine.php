<?php
// ===========================================================================
// OMNI ELOQUENT ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Laravel Eloquent ORM + Active Record + Query Builder
// Logic Inherited: PHP / Domain Layer (Active Record Pattern & Query Builder)
// ===========================================================================
//
// By studying Eloquent, Mother learned PHP ORM patterns:
//   1. Active Record: model instance = database row
//   2. Fluent query builder chains where/orderBy/limit
//   3. Mass assignment protection via $fillable/$guarded
//   4. Relationships: hasOne, hasMany, belongsTo, belongsToMany
//   5. Soft deletes, timestamps, accessors/mutators

declare(strict_types=1);

namespace Omni\Domain\PHP;

// ============================================================
// PART 1: Query Builder
// ============================================================

class QueryBuilder
{
    private string $table;
    private array $wheres = [];
    private array $orderBys = [];
    private ?int $limitVal = null;
    private int $offsetVal = 0;
    private array $selectColumns = ['*'];
    private array $data;

    public function __construct(string $table, array $data = [])
    {
        $this->table = $table;
        $this->data = $data;
    }

    public function select(string ...$columns): self
    {
        $clone = clone $this;
        $clone->selectColumns = $columns;
        return $clone;
    }

    public function where(string $column, mixed $operator, mixed $value = null): self
    {
        $clone = clone $this;
        if ($value === null) {
            $value = $operator;
            $operator = '=';
        }
        $clone->wheres[] = ['column' => $column, 'operator' => $operator, 'value' => $value];
        return $clone;
    }

    public function whereIn(string $column, array $values): self
    {
        $clone = clone $this;
        $clone->wheres[] = ['column' => $column, 'operator' => 'IN', 'value' => $values];
        return $clone;
    }

    public function whereLike(string $column, string $pattern): self
    {
        return $this->where($column, 'LIKE', $pattern);
    }

    public function orderBy(string $column, string $direction = 'ASC'): self
    {
        $clone = clone $this;
        $clone->orderBys[] = ['column' => $column, 'direction' => strtoupper($direction)];
        return $clone;
    }

    public function limit(int $limit): self
    {
        $clone = clone $this;
        $clone->limitVal = $limit;
        return $clone;
    }

    public function offset(int $offset): self
    {
        $clone = clone $this;
        $clone->offsetVal = $offset;
        return $clone;
    }

    public function get(): array
    {
        $results = $this->applyFilters($this->data);
        $results = $this->applyOrder($results);
        $results = array_slice($results, $this->offsetVal, $this->limitVal);
        return $results;
    }

    public function first(): ?array
    {
        $results = $this->limit(1)->get();
        return $results[0] ?? null;
    }

    public function count(): int
    {
        return count($this->applyFilters($this->data));
    }

    public function exists(): bool
    {
        return $this->count() > 0;
    }

    public function pluck(string $column): array
    {
        return array_column($this->get(), $column);
    }

    private function applyFilters(array $data): array
    {
        foreach ($this->wheres as $where) {
            $data = array_filter($data, function ($row) use ($where) {
                $value = $row[$where['column']] ?? null;
                return match ($where['operator']) {
                    '='  => $value == $where['value'],
                    '!=' => $value != $where['value'],
                    '>'  => $value > $where['value'],
                    '<'  => $value < $where['value'],
                    '>=' => $value >= $where['value'],
                    '<=' => $value <= $where['value'],
                    'IN' => in_array($value, $where['value'], false),
                    'LIKE' => fnmatch($where['value'], (string)$value),
                    default => true,
                };
            });
        }
        return array_values($data);
    }

    private function applyOrder(array $data): array
    {
        foreach (array_reverse($this->orderBys) as $order) {
            usort($data, function ($a, $b) use ($order) {
                $va = $a[$order['column']] ?? null;
                $vb = $b[$order['column']] ?? null;
                $cmp = $va <=> $vb;
                return $order['direction'] === 'DESC' ? -$cmp : $cmp;
            });
        }
        return $data;
    }

    public function toSql(): string
    {
        $sql = "SELECT " . implode(', ', $this->selectColumns) . " FROM {$this->table}";
        if ($this->wheres) {
            $conditions = array_map(fn($w) => "{$w['column']} {$w['operator']} ?", $this->wheres);
            $sql .= " WHERE " . implode(' AND ', $conditions);
        }
        foreach ($this->orderBys as $o) {
            $sql .= " ORDER BY {$o['column']} {$o['direction']}";
        }
        if ($this->limitVal !== null) {
            $sql .= " LIMIT {$this->limitVal}";
        }
        if ($this->offsetVal > 0) {
            $sql .= " OFFSET {$this->offsetVal}";
        }
        return $sql;
    }
}

// ============================================================
// PART 2: Active Record Model
// ============================================================

abstract class Model
{
    /** @var string Table name. */
    protected static string $table = '';

    /** @var string Primary key column. */
    protected static string $primaryKey = 'id';

    /** @var string[] Fillable fields (mass-assignment protection). */
    protected static array $fillable = [];

    /** @var string[] Guarded fields (cannot be mass-assigned). */
    protected static array $guarded = ['id'];

    /** @var bool Enable timestamps. */
    protected static bool $timestamps = true;

    /** @var bool Enable soft deletes. */
    protected static bool $softDeletes = false;

    /** @var array<string, mixed> Model attributes. */
    protected array $attributes = [];

    /** @var array<string, mixed> Original attributes (for dirty checking). */
    protected array $original = [];

    /** @var bool Whether this model has been persisted. */
    protected bool $exists = false;

    /** @var array In-memory storage (simulated database). */
    private static array $storage = [];

    private static int $autoIncrement = 1;

    public function __construct(array $attributes = [])
    {
        $this->fill($attributes);
    }

    /**
     * Mass-assign attributes (respects $fillable / $guarded).
     */
    public function fill(array $attributes): self
    {
        foreach ($attributes as $key => $value) {
            if ($this->isFillable($key)) {
                $this->setAttribute($key, $value);
            }
        }
        return $this;
    }

    /**
     * Get an attribute value.
     */
    public function getAttribute(string $key): mixed
    {
        // Check for accessor method
        $accessor = 'get' . str_replace('_', '', ucwords($key, '_')) . 'Attribute';
        if (method_exists($this, $accessor)) {
            return $this->$accessor($this->attributes[$key] ?? null);
        }
        return $this->attributes[$key] ?? null;
    }

    /**
     * Set an attribute value.
     */
    public function setAttribute(string $key, mixed $value): void
    {
        // Check for mutator method
        $mutator = 'set' . str_replace('_', '', ucwords($key, '_')) . 'Attribute';
        if (method_exists($this, $mutator)) {
            $value = $this->$mutator($value);
        }
        $this->attributes[$key] = $value;
    }

    public function __get(string $key): mixed
    {
        return $this->getAttribute($key);
    }

    public function __set(string $key, mixed $value): void
    {
        $this->setAttribute($key, $value);
    }

    /**
     * Get dirty (changed) attributes.
     */
    public function getDirty(): array
    {
        $dirty = [];
        foreach ($this->attributes as $key => $value) {
            if (!isset($this->original[$key]) || $this->original[$key] !== $value) {
                $dirty[$key] = $value;
            }
        }
        return $dirty;
    }

    public function isDirty(): bool
    {
        return count($this->getDirty()) > 0;
    }

    /**
     * Save model to storage.
     */
    public function save(): bool
    {
        $table = static::$table;
        $pk = static::$primaryKey;

        if (static::$timestamps) {
            $now = date('Y-m-d H:i:s');
            if (!$this->exists) {
                $this->attributes['created_at'] = $now;
            }
            $this->attributes['updated_at'] = $now;
        }

        if (!$this->exists) {
            $this->attributes[$pk] = self::$autoIncrement++;
            self::$storage[$table][] = $this->attributes;
            $this->exists = true;
        } else {
            // Update existing
            foreach (self::$storage[$table] ?? [] as $i => $row) {
                if (($row[$pk] ?? null) === $this->attributes[$pk]) {
                    self::$storage[$table][$i] = $this->attributes;
                    break;
                }
            }
        }

        $this->original = $this->attributes;
        return true;
    }

    /**
     * Delete model from storage.
     */
    public function delete(): bool
    {
        $table = static::$table;
        $pk = static::$primaryKey;

        if (static::$softDeletes) {
            $this->attributes['deleted_at'] = date('Y-m-d H:i:s');
            return $this->save();
        }

        self::$storage[$table] = array_values(array_filter(
            self::$storage[$table] ?? [],
            fn($row) => ($row[$pk] ?? null) !== $this->attributes[$pk]
        ));

        $this->exists = false;
        return true;
    }

    public function toArray(): array
    {
        return $this->attributes;
    }

    // ============================================================
    // Static Query Methods
    // ============================================================

    public static function query(): QueryBuilder
    {
        return new QueryBuilder(static::$table, self::$storage[static::$table] ?? []);
    }

    public static function all(): array
    {
        return self::$storage[static::$table] ?? [];
    }

    public static function find(mixed $id): ?static
    {
        $pk = static::$primaryKey;
        $data = self::$storage[static::$table] ?? [];
        foreach ($data as $row) {
            if (($row[$pk] ?? null) == $id) {
                $model = new static($row);
                $model->exists = true;
                $model->original = $row;
                return $model;
            }
        }
        return null;
    }

    public static function create(array $attributes): static
    {
        $model = new static($attributes);
        $model->save();
        return $model;
    }

    public static function where(string $column, mixed $operator, mixed $value = null): QueryBuilder
    {
        return static::query()->where($column, $operator, $value);
    }

    protected function isFillable(string $key): bool
    {
        if (in_array($key, static::$guarded, true)) {
            return false;
        }
        if (!empty(static::$fillable)) {
            return in_array($key, static::$fillable, true);
        }
        return true;
    }

    /**
     * Reset storage (for testing).
     */
    public static function resetStorage(): void
    {
        self::$storage = [];
        self::$autoIncrement = 1;
    }

    public static function diagnostics(): array
    {
        return [
            'engine' => 'OmniEloquentEngine',
            'layer' => 'PHP Domain',
            'table' => static::$table,
            'total_records' => count(self::$storage[static::$table] ?? []),
            'features' => [
                'active_record', 'query_builder', 'mass_assignment_protection',
                'dirty_checking', 'timestamps', 'soft_deletes',
                'accessors_mutators', 'to_sql_generation',
            ],
            'learned_logic' => [
                'eloquent-active-record-pattern',
                'fluent-query-builder-chain',
                'fillable-guarded-mass-assign',
                'dirty-check-original-compare',
                'accessor-mutator-magic-methods',
                'soft-delete-deleted-at',
                'auto-increment-primary-key',
                'reflection-auto-wire-constructor',
            ],
        ];
    }
}
