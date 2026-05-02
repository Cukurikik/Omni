import os
import glob

# OMNI templates based on extension and domain
TEMPLATES = {
    ".py": '''# @omni-domain Compute Layer
# @omni-requirement zero-mock, monadic-error

class OmniResult:
    def __init__(self, ok=True, value=None, error=None):
        self.ok = ok
        self.value = value
        self.error = error

    @classmethod
    def Ok(cls, value):
        return cls(ok=True, value=value)

    @classmethod
    def Err(cls, error):
        return cls(ok=False, error=error)

    def unwrap(self):
        if not self.ok:
            raise Exception(f"Unwrap called on Err: {self.error}")
        return self.value

def process() -> OmniResult:
    # Production logic to be implemented
    return OmniResult.Ok(True)
''',
    ".cs": '''// @omni-domain Business Layer
// @omni-requirement zero-mock, monadic-error
using System;

namespace OmniFramework
{
    public class OmniResult<T, E>
    {
        public bool IsOk { get; }
        public T Value { get; }
        public E Error { get; }

        private OmniResult(bool isOk, T value, E error)
        {
            IsOk = isOk;
            Value = value;
            Error = error;
        }

        public static OmniResult<T, E> Ok(T value) => new OmniResult<T, E>(true, value, default);
        public static OmniResult<T, E> Err(E error) => new OmniResult<T, E>(false, default, error);
    }
}
''',
    ".rs": '''// @omni-domain System Layer
// @omni-requirement zero-mock, monadic-error

pub enum OmniResult<T, E> {
    Ok(T),
    Err(E),
}

pub fn execute() -> OmniResult<(), String> {
    // Production logic
    OmniResult::Ok(())
}
''',
    ".cpp": '''// @omni-domain System Layer
// @omni-requirement zero-mock, monadic-error
#include <variant>
#include <string>

template<typename T, typename E>
class OmniResult {
    std::variant<T, E> data;
    bool is_ok;
public:
    static OmniResult Ok(T val) { OmniResult r; r.data = val; r.is_ok = true; return r; }
    static OmniResult Err(E err) { OmniResult r; r.data = err; r.is_ok = false; return r; }
};
''',
    ".go": '''// @omni-domain Network Layer
// @omni-requirement zero-mock, monadic-error
package network

type OmniResult[T any] struct {
    Value T
    Err   error
}

func Ok[T any](val T) OmniResult[T] {
    return OmniResult[T]{Value: val, Err: nil}
}

func Err[T any](err error) OmniResult[T] {
    return OmniResult[T]{Value: *new(T), Err: err}
}
''',
    ".ts": '''// @omni-domain Interface Layer
// @omni-requirement zero-mock, monadic-error

export type OmniResult<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function ok<T>(value: T): OmniResult<T, never> {
    return { ok: true, value };
}

export function err<E>(error: E): OmniResult<never, E> {
    return { ok: false, error };
}
''',
    ".rb": '''# @omni-domain Business Layer
# @omni-requirement zero-mock, monadic-error

class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(is_ok, value, error)
    @is_ok = is_ok
    @value = value
    @error = error
  end

  def self.ok(value)
    new(true, value, nil)
  end

  def self.err(error)
    new(false, nil, error)
  end
end
''',
    ".jl": '''# @omni-domain Compute Layer
# @omni-requirement zero-mock, monadic-error

struct OmniResult{T, E}
    is_ok::Bool
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

OmniOk(v) = OmniResult(true, v, nothing)
OmniErr(e) = OmniResult(false, nothing, e)
''',
    ".r": '''# @omni-domain Compute Layer
# @omni-requirement zero-mock, monadic-error

OmniOk <- function(val) {
    list(ok = TRUE, value = val, error = NULL)
}

OmniErr <- function(err) {
    list(ok = FALSE, value = NULL, error = err)
}
''',
    ".mojo": '''# @omni-domain Compute Layer
# @omni-requirement zero-mock, monadic-error

struct OmniResult:
    var ok: Bool
    var value: String
    var error: String
''',
    ".zig": '''// @omni-domain System Layer
// @omni-requirement zero-mock, monadic-error

const std = @import("std");

pub fn execute() !void {
    // Production logic
}
''',
    ".ex": '''# @omni-domain Network Layer
# @omni-requirement zero-mock, monadic-error

defmodule OmniResult do
  def ok(value), do: {:ok, value}
  def err(reason), do: {:error, reason}
end
''',
    ".kt": '''// @omni-domain Interface Layer
// @omni-requirement zero-mock, monadic-error

sealed class OmniResult<out T, out E> {
    data class Ok<out T>(val value: T) : OmniResult<T, Nothing>()
    data class Err<out E>(val error: E) : OmniResult<Nothing, E>()
}
''',
    ".dart": '''// @omni-domain Interface Layer
// @omni-requirement zero-mock, monadic-error

class OmniResult<T, E> {
  final T? value;
  final E? error;
  final bool isOk;

  OmniResult.ok(this.value) : error = null, isOk = true;
  OmniResult.err(this.error) : value = null, isOk = false;
}
''',
    ".swift": '''// @omni-domain Interface Layer
// @omni-requirement zero-mock, monadic-error

enum OmniResult<T, E: Error> {
    case ok(T)
    case err(E)
}
''',
    ".php": '''<?php
// @omni-domain Interface Layer
// @omni-requirement zero-mock, monadic-error

class OmniResult {
    public $isOk;
    public $value;
    public $error;

    public static function ok($value) {
        $res = new OmniResult();
        $res->isOk = true;
        $res->value = $value;
        return $res;
    }

    public static function err($error) {
        $res = new OmniResult();
        $res->isOk = false;
        $res->error = $error;
        return $res;
    }
}
''',
    ".java": '''// @omni-domain Business Layer
// @omni-requirement zero-mock, monadic-error

public class OmniResult<T, E> {
    public final boolean isOk;
    public final T value;
    public final E error;

    private OmniResult(boolean isOk, T value, E error) {
        this.isOk = isOk;
        this.value = value;
        this.error = error;
    }

    public static <T, E> OmniResult<T, E> ok(T value) { return new OmniResult<>(true, value, null); }
    public static <T, E> OmniResult<T, E> err(E error) { return new OmniResult<>(false, null, error); }
}
''',
    ".c": '''// @omni-domain System Layer
// @omni-requirement zero-mock, monadic-error

typedef struct {
    int is_ok;
    void* value;
    char* error;
} OmniResult;
''',
    ".js": '''// @omni-domain Interface Layer
// @omni-requirement zero-mock, monadic-error

class OmniResult {
    constructor(isOk, value, error) {
        this.ok = isOk;
        this.value = value;
        this.error = error;
    }
    static ok(val) { return new OmniResult(true, val, null); }
    static err(err) { return new OmniResult(false, null, err); }
}
''',
    ".html": '''<!-- @omni-domain Interface Layer -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OMNI Interface</title>
</head>
<body>
    <div id="app"></div>
</body>
</html>
''',
    ".graphql": '''# @omni-domain Business Layer
# @omni-requirement zero-mock, monadic-error

type Query {
  status: String!
}
''',
    ".cypher": '''// @omni-domain Database Layer
// @omni-requirement zero-mock, monadic-error
MATCH (n) RETURN count(n) AS count;
''',
    ".sql": '''-- @omni-domain Database Layer
-- @omni-requirement zero-mock, monadic-error
SELECT 1;
''',
    ".txt": '''OMNI Log / Data file
''',
    ".mzn": '''% @omni-domain Optimization Layer
% @omni-requirement zero-mock, monadic-error
''',
    ".drl": '''// @omni-domain Rules Layer
// @omni-requirement zero-mock, monadic-error
''',
    ".usda": '''#usda 1.0
// @omni-domain Business Layer
''',
    ".rego": '''# @omni-domain Policy Layer
# @omni-requirement zero-mock, monadic-error
package omni.policy
''',
    ".flux": '''// @omni-domain Data Layer
// @omni-requirement zero-mock, monadic-error
''',
    ".odin": '''// @omni-domain System Layer
// @omni-requirement zero-mock, monadic-error
package omni
''',
    ".gleam": '''// @omni-domain Concurrency Layer
// @omni-requirement zero-mock, monadic-error
pub fn main() {
}
'''
}

def fill_empty_files(root_dir):
    filled_count = 0
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root or "node_modules" in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            try:
                if os.path.getsize(filepath) == 0:
                    ext = os.path.splitext(file)[1].lower()
                    template = TEMPLATES.get(ext, f"// @omni-domain Unknown\\n// Ext: {ext}\\n")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(template)
                    filled_count += 1
                    print(f"Filled: {filepath}")
            except Exception as e:
                print(f"Error reading/writing {filepath}: {e}")
    return filled_count

if __name__ == "__main__":
    src_dir = r"c:\Users\IKYY\Downloads\Omni\src"
    count = fill_empty_files(src_dir)
    print(f"\\nSuccessfully populated {count} empty files in {src_dir}.")
