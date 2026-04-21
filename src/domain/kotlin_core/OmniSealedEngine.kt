// ===========================================================================
// OMNI SEALED ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Kotlin sealed classes + Arrow Either + exhaustive when
// Logic Inherited: Kotlin / Domain Layer (Algebraic Data Types & Pattern Matching)
// ===========================================================================
//
// By studying Kotlin sealed hierarchies and Arrow-kt, Mother learned:
//   1. Sealed classes restrict subclass set (closed hierarchy)
//   2. `when` expressions are exhaustive on sealed types
//   3. data class subtypes provide structural equality
//   4. Nested sealed hierarchies model complex domain states
//   5. Either<L,R> represents success/failure without exceptions

package omni.domain.kotlin

// ============================================================
// PART 1: Either Monad (Arrow-kt inspired)
// ============================================================

sealed class Either<out L, out R> {
    data class Left<L>(val value: L) : Either<L, Nothing>()
    data class Right<R>(val value: R) : Either<Nothing, R>()

    val isLeft: Boolean get() = this is Left
    val isRight: Boolean get() = this is Right

    fun <T> map(f: (R) -> T): Either<L, T> = when (this) {
        is Left -> this
        is Right -> Right(f(value))
    }

    fun <T> flatMap(f: (R) -> Either<L, T>): Either<L, T> = when (this) {
        is Left -> this
        is Right -> f(value)
    }

    fun <T> mapLeft(f: (L) -> T): Either<T, R> = when (this) {
        is Left -> Left(f(value))
        is Right -> this
    }

    fun <T> fold(onLeft: (L) -> T, onRight: (R) -> T): T = when (this) {
        is Left -> onLeft(value)
        is Right -> onRight(value)
    }

    fun getOrElse(default: @UnsafeVariance R): R = when (this) {
        is Left -> default
        is Right -> value
    }

    fun getOrNull(): R? = when (this) {
        is Left -> null
        is Right -> value
    }

    fun swap(): Either<R, L> = when (this) {
        is Left -> Right(value)
        is Right -> Left(value)
    }

    fun tap(f: (R) -> Unit): Either<L, R> {
        if (this is Right) f(value)
        return this
    }

    fun tapLeft(f: (L) -> Unit): Either<L, R> {
        if (this is Left) f(value)
        return this
    }

    companion object {
        fun <R> right(value: R): Either<Nothing, R> = Right(value)
        fun <L> left(value: L): Either<L, Nothing> = Left(value)

        inline fun <R> catch(block: () -> R): Either<Throwable, R> {
            return try {
                Right(block())
            } catch (e: Throwable) {
                Left(e)
            }
        }
    }
}

// ============================================================
// PART 2: Domain State Machine (Sealed Hierarchy)
// ============================================================

/** Order state machine using sealed class hierarchy. */
sealed class OrderState {
    abstract val orderId: String
    abstract val timestamp: Long

    data class Draft(
        override val orderId: String,
        val items: List<OrderItem> = emptyList(),
        override val timestamp: Long = System.currentTimeMillis()
    ) : OrderState() {
        fun addItem(item: OrderItem): Draft = copy(items = items + item)
        fun removeItem(itemId: String): Draft = copy(items = items.filter { it.id != itemId })
        fun submit(): Either<OrderError, Submitted> {
            if (items.isEmpty()) return Either.left(OrderError.EmptyOrder(orderId))
            return Either.right(Submitted(orderId, items, System.currentTimeMillis()))
        }
    }

    data class Submitted(
        override val orderId: String,
        val items: List<OrderItem>,
        override val timestamp: Long
    ) : OrderState() {
        fun approve(approver: String): Approved =
            Approved(orderId, items, approver, System.currentTimeMillis())
        fun reject(reason: String): Rejected =
            Rejected(orderId, reason, System.currentTimeMillis())
    }

    data class Approved(
        override val orderId: String,
        val items: List<OrderItem>,
        val approvedBy: String,
        override val timestamp: Long
    ) : OrderState() {
        fun ship(trackingNumber: String): Shipped =
            Shipped(orderId, items, trackingNumber, System.currentTimeMillis())
    }

    data class Shipped(
        override val orderId: String,
        val items: List<OrderItem>,
        val trackingNumber: String,
        override val timestamp: Long
    ) : OrderState() {
        fun deliver(): Delivered = Delivered(orderId, items, System.currentTimeMillis())
    }

    data class Delivered(
        override val orderId: String,
        val items: List<OrderItem>,
        override val timestamp: Long
    ) : OrderState()

    data class Rejected(
        override val orderId: String,
        val reason: String,
        override val timestamp: Long
    ) : OrderState()

    data class Cancelled(
        override val orderId: String,
        val reason: String,
        override val timestamp: Long
    ) : OrderState()
}

data class OrderItem(val id: String, val name: String, val price: Double, val quantity: Int)

sealed class OrderError {
    data class EmptyOrder(val orderId: String) : OrderError()
    data class InvalidTransition(val from: String, val to: String) : OrderError()
    data class ItemNotFound(val itemId: String) : OrderError()
    data class InsufficientStock(val itemId: String, val available: Int) : OrderError()
}

// Exhaustive when expression (compiler-checked)
fun OrderState.describe(): String = when (this) {
    is OrderState.Draft -> "Draft order with ${items.size} items"
    is OrderState.Submitted -> "Submitted for approval"
    is OrderState.Approved -> "Approved by $approvedBy"
    is OrderState.Shipped -> "Shipped (tracking: $trackingNumber)"
    is OrderState.Delivered -> "Delivered"
    is OrderState.Rejected -> "Rejected: $reason"
    is OrderState.Cancelled -> "Cancelled: $reason"
}

// ============================================================
// PART 3: Validated (Accumulating Errors)
// ============================================================

/** Accumulates all validation errors instead of short-circuiting. */
sealed class Validated<out E, out A> {
    data class Valid<A>(val value: A) : Validated<Nothing, A>()
    data class Invalid<E>(val errors: List<E>) : Validated<E, Nothing>()

    fun <B> map(f: (A) -> B): Validated<E, B> = when (this) {
        is Valid -> Valid(f(value))
        is Invalid -> this
    }

    fun isValid(): Boolean = this is Valid
    fun isInvalid(): Boolean = this is Invalid

    companion object {
        fun <A> valid(value: A): Validated<Nothing, A> = Valid(value)
        fun <E> invalid(vararg errors: E): Validated<E, Nothing> = Invalid(errors.toList())

        /** Combine multiple validations — accumulate ALL errors. */
        fun <E, A, B, C> zip(
            va: Validated<E, A>,
            vb: Validated<E, B>,
            f: (A, B) -> C
        ): Validated<E, C> {
            return when {
                va is Valid && vb is Valid -> Valid(f(va.value, vb.value))
                va is Invalid && vb is Invalid -> Invalid(va.errors + vb.errors)
                va is Invalid -> va
                else -> vb as Invalid
            }
        }

        fun <E, A, B, C, D> zip3(
            va: Validated<E, A>,
            vb: Validated<E, B>,
            vc: Validated<E, C>,
            f: (A, B, C) -> D
        ): Validated<E, D> {
            val allErrors = listOfNotNull(
                (va as? Invalid)?.errors,
                (vb as? Invalid)?.errors,
                (vc as? Invalid)?.errors
            ).flatten()

            return if (allErrors.isEmpty() && va is Valid && vb is Valid && vc is Valid) {
                Valid(f(va.value, vb.value, vc.value))
            } else {
                Invalid(allErrors)
            }
        }
    }
}

// ============================================================
// PART 4: Option Type
// ============================================================

sealed class Option<out T> {
    object None : Option<Nothing>() {
        override fun toString() = "None"
    }
    data class Some<T>(val value: T) : Option<T>()

    fun <R> map(f: (T) -> R): Option<R> = when (this) {
        is None -> None
        is Some -> Some(f(value))
    }

    fun <R> flatMap(f: (T) -> Option<R>): Option<R> = when (this) {
        is None -> None
        is Some -> f(value)
    }

    fun getOrElse(default: @UnsafeVariance T): T = when (this) {
        is None -> default
        is Some -> value
    }

    fun filter(predicate: (T) -> Boolean): Option<T> = when (this) {
        is None -> None
        is Some -> if (predicate(value)) this else None
    }

    fun toEither(ifEmpty: () -> Any): Either<Any, T> = when (this) {
        is None -> Either.left(ifEmpty())
        is Some -> Either.right(value)
    }

    companion object {
        fun <T> of(value: T?): Option<T> = if (value != null) Some(value) else None
        fun <T> empty(): Option<T> = None
    }
}

// ============================================================
// Diagnostics
// ============================================================

fun sealedDiagnostics(): Map<String, Any> = mapOf(
    "engine" to "OmniSealedEngine",
    "layer" to "Kotlin Domain",
    "components" to listOf(
        "Either<L,R>", "Option<T>", "Validated<E,A>",
        "OrderState (sealed hierarchy)", "OrderError (sealed)"
    ),
    "monadic_ops" to listOf("map", "flatMap", "fold", "getOrElse", "swap", "tap"),
    "learned_logic" to listOf(
        "sealed-class-closed-hierarchy",
        "exhaustive-when-compiler-check",
        "either-monad-error-handling",
        "validated-accumulate-all-errors",
        "option-null-safety-encoding",
        "state-machine-sealed-transitions",
        "data-class-structural-equality",
        "companion-factory-methods"
    )
)
