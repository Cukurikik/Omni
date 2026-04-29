// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Gleam Language — Concurrency & Networking Layer (OMNI Zero-Mock Implementation)
// Implements deterministic Actor Mailbox dispatch with priority queue ordering.
// Absorbs patterns from: github.com/gleam-lang/gleam, github.com/gleam-lang/otp

import gleam/list
import gleam/result
import gleam/option.{type Option, None, Some}
import gleam/order.{type Order, Gt, Lt, Eq}

/// Represents a typed message in the actor mailbox with priority weighting.
pub type MailboxMessage {
  MailboxMessage(
    priority: Int,
    payload_tag: String,
    sequence_id: Int,
  )
}

/// Result type for mailbox operations — monadic error handling.
pub type MailboxResult(a) {
  MailboxOk(value: a)
  MailboxErr(reason: String)
}

/// Compares two messages by priority (descending), breaking ties by sequence_id (ascending).
/// This is the exact ordering used by Erlang/OTP selective receive semantics.
pub fn compare_priority(a: MailboxMessage, b: MailboxMessage) -> Order {
  case a.priority > b.priority {
    True -> Lt  // Higher priority sorts first
    False ->
      case a.priority < b.priority {
        True -> Gt
        False ->
          // Equal priority: FIFO by sequence_id
          case a.sequence_id < b.sequence_id {
            True -> Lt
            False ->
              case a.sequence_id > b.sequence_id {
                True -> Gt
                False -> Eq
              }
          }
      }
  }
}

/// Inserts a message into a sorted mailbox maintaining priority order.
/// Returns the new sorted mailbox state.
pub fn mailbox_enqueue(
  mailbox: List(MailboxMessage),
  msg: MailboxMessage,
) -> MailboxResult(List(MailboxMessage)) {
  case msg.priority < 0 {
    True ->
      MailboxErr("Gleam actor mailbox rejects negative priority values.")
    False -> {
      let new_mailbox = list.sort([msg, ..mailbox], compare_priority)
      MailboxOk(new_mailbox)
    }
  }
}

/// Dequeues the highest-priority message from the mailbox.
/// Returns the message and the remaining mailbox.
pub fn mailbox_dequeue(
  mailbox: List(MailboxMessage),
) -> MailboxResult(#(MailboxMessage, List(MailboxMessage))) {
  case mailbox {
    [] -> MailboxErr("Gleam actor mailbox is empty — no messages to dispatch.")
    [head, ..tail] -> MailboxOk(#(head, tail))
  }
}

/// Filters mailbox by payload tag, returning only matching messages.
pub fn mailbox_filter_by_tag(
  mailbox: List(MailboxMessage),
  target_tag: String,
) -> List(MailboxMessage) {
  list.filter(mailbox, fn(msg) { msg.payload_tag == target_tag })
}

/// Returns the current depth of the mailbox.
pub fn mailbox_depth(mailbox: List(MailboxMessage)) -> Int {
  list.length(mailbox)
}
