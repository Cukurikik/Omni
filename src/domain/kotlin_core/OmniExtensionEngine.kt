// ===========================================================================
// OMNI EXTENSION ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Kotlin stdlib extensions + Arrow-kt + KotlinX
// Logic Inherited: Kotlin / Domain Layer (Extension Functions & DSL Builders)
// ===========================================================================
//
// By studying Arrow-kt and Kotlin stdlib, Mother learned:
//   1. Extension functions add methods without modifying classes
//   2. Lambda with receiver enables type-safe DSL builders
//   3. Inline functions eliminate lambda overhead
//   4. Reified type parameters enable runtime type inspection
//   5. Operator overloading makes domain types expressive

package omni.domain.kotlin

import java.time.*
import java.time.format.DateTimeFormatter
import java.util.concurrent.ConcurrentHashMap

// ============================================================
// PART 1: Collection Extensions
// ============================================================

/** Partition a list into chunks of equal size. */
fun <T> List<T>.chunkedPairs(): List<Pair<T, T?>> {
    return chunked(2).map { chunk ->
        chunk[0] to chunk.getOrNull(1)
    }
}

/** Find the most common element. */
fun <T> List<T>.mode(): T? {
    return groupBy { it }
        .maxByOrNull { it.value.size }
        ?.key
}

/** Running average of numeric list. */
fun List<Double>.runningAverage(): List<Double> {
    var sum = 0.0
    return mapIndexed { index, value ->
        sum += value
        sum / (index + 1)
    }
}

/** Interleave two lists. */
fun <T> List<T>.interleave(other: List<T>): List<T> {
    val result = mutableListOf<T>()
    val maxSize = maxOf(this.size, other.size)
    for (i in 0 until maxSize) {
        if (i < this.size) result.add(this[i])
        if (i < other.size) result.add(other[i])
    }
    return result
}

/** Sliding window over a list. */
fun <T> List<T>.slidingWindow(size: Int, step: Int = 1): List<List<T>> {
    return (0..this.size - size step step).map { i ->
        subList(i, i + size)
    }
}

// ============================================================
// PART 2: String Extensions
// ============================================================

/** Convert to title case. */
fun String.toTitleCase(): String {
    return split(" ").joinToString(" ") { word ->
        word.lowercase().replaceFirstChar { it.uppercase() }
    }
}

/** Truncate with ellipsis. */
fun String.truncate(maxLength: Int, suffix: String = "..."): String {
    return if (length <= maxLength) this
    else take(maxLength - suffix.length) + suffix
}

/** Check if string is a valid email format. */
fun String.isEmail(): Boolean {
    return matches(Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\$"))
}

/** Mask sensitive data (show first/last N chars). */
fun String.mask(visibleStart: Int = 2, visibleEnd: Int = 2, maskChar: Char = '*'): String {
    if (length <= visibleStart + visibleEnd) return String(CharArray(length) { maskChar })
    val start = take(visibleStart)
    val end = takeLast(visibleEnd)
    val masked = String(CharArray(length - visibleStart - visibleEnd) { maskChar })
    return "$start$masked$end"
}

/** Convert camelCase to snake_case. */
fun String.toSnakeCase(): String {
    return replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()
}

/** Convert snake_case to camelCase. */
fun String.toCamelCase(): String {
    return split("_").mapIndexed { index, word ->
        if (index == 0) word.lowercase()
        else word.lowercase().replaceFirstChar { it.uppercase() }
    }.joinToString("")
}

// ============================================================
// PART 3: Type-Safe DSL Builders
// ============================================================

/** HTML-like DSL builder. */
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun head(block: HeadBuilder.() -> Unit) {
        val builder = HeadBuilder()
        builder.block()
        elements.add("<head>${builder.build()}</head>")
    }

    fun body(block: BodyBuilder.() -> Unit) {
        val builder = BodyBuilder()
        builder.block()
        elements.add("<body>${builder.build()}</body>")
    }

    fun build(): String = "<html>${elements.joinToString("")}</html>"
}

@HtmlDsl
class HeadBuilder {
    private val elements = mutableListOf<String>()

    fun title(text: String) { elements.add("<title>$text</title>") }
    fun meta(name: String, content: String) {
        elements.add("<meta name=\"$name\" content=\"$content\">")
    }
    fun build(): String = elements.joinToString("")
}

@HtmlDsl
class BodyBuilder {
    private val elements = mutableListOf<String>()

    fun h1(text: String) { elements.add("<h1>$text</h1>") }
    fun h2(text: String) { elements.add("<h2>$text</h2>") }
    fun p(text: String) { elements.add("<p>$text</p>") }
    fun div(cssClass: String = "", block: BodyBuilder.() -> Unit) {
        val inner = BodyBuilder()
        inner.block()
        val classAttr = if (cssClass.isNotEmpty()) " class=\"$cssClass\"" else ""
        elements.add("<div$classAttr>${inner.build()}</div>")
    }
    fun ul(block: ListBuilder.() -> Unit) {
        val builder = ListBuilder()
        builder.block()
        elements.add("<ul>${builder.build()}</ul>")
    }
    fun build(): String = elements.joinToString("")
}

@HtmlDsl
class ListBuilder {
    private val items = mutableListOf<String>()
    fun li(text: String) { items.add("<li>$text</li>") }
    fun build(): String = items.joinToString("")
}

fun html(block: HtmlBuilder.() -> Unit): String {
    val builder = HtmlBuilder()
    builder.block()
    return builder.build()
}

/** Config DSL builder. */
@DslMarker
annotation class ConfigDsl

@ConfigDsl
class ConfigBuilder {
    private val settings = mutableMapOf<String, Any>()
    private val sections = mutableMapOf<String, ConfigBuilder>()

    fun set(key: String, value: Any) { settings[key] = value }
    fun section(name: String, block: ConfigBuilder.() -> Unit) {
        val builder = ConfigBuilder()
        builder.block()
        sections[name] = builder
    }

    fun build(): Map<String, Any> {
        val result = mutableMapOf<String, Any>()
        result.putAll(settings)
        sections.forEach { (name, builder) ->
            result[name] = builder.build()
        }
        return result
    }
}

fun config(block: ConfigBuilder.() -> Unit): Map<String, Any> {
    val builder = ConfigBuilder()
    builder.block()
    return builder.build()
}

// ============================================================
// PART 4: Inline + Reified Utilities
// ============================================================

/** Safe cast with reified type. */
inline fun <reified T> Any?.safeCast(): T? = this as? T

/** Measure execution time. */
inline fun <T> measureTimeAndResult(block: () -> T): Pair<T, Long> {
    val start = System.nanoTime()
    val result = block()
    val elapsed = (System.nanoTime() - start) / 1_000_000
    return result to elapsed
}

/** Retry with condition. */
inline fun <T> retry(
    maxAttempts: Int = 3,
    delayMs: Long = 100,
    block: (attempt: Int) -> T
): T {
    var lastException: Exception? = null
    repeat(maxAttempts) { attempt ->
        try {
            return block(attempt + 1)
        } catch (e: Exception) {
            lastException = e
            Thread.sleep(delayMs * (attempt + 1))
        }
    }
    throw lastException!!
}

// ============================================================
// Diagnostics
// ============================================================

fun extensionDiagnostics(): Map<String, Any> = mapOf(
    "engine" to "OmniExtensionEngine",
    "layer" to "Kotlin Domain",
    "extensions" to mapOf(
        "collection" to listOf("chunkedPairs", "mode", "runningAverage", "interleave", "slidingWindow"),
        "string" to listOf("toTitleCase", "truncate", "isEmail", "mask", "toSnakeCase", "toCamelCase"),
        "dsl" to listOf("html{}", "config{}"),
        "inline" to listOf("safeCast", "measureTimeAndResult", "retry")
    ),
    "learned_logic" to listOf(
        "extension-function-augmentation",
        "lambda-with-receiver-dsl",
        "dsl-marker-scope-control",
        "inline-no-lambda-overhead",
        "reified-type-parameter-runtime",
        "operator-overloading-domain",
        "builder-pattern-type-safe",
        "sliding-window-sublist"
    )
)
