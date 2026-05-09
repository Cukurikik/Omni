// OMNI Framework Actor Model in Pony
// Guarantees zero data races at compile time

actor OmniMailbox
  var _message_count: U64 = 0
  let _env: Env

  new create(env: Env) =>
    _env = env

  be receive_event(id: String, payload: String) =>
    _message_count = _message_count + 1
    _env.out.print("OMNI Actor " + id + " received: " + payload)

  be get_stats() =>
    _env.out.print("Total messages processed: " + _message_count.string())
