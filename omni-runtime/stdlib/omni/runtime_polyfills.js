// ═══════════════════════════════════════════════════════════════════════
// 🔥 OMNI RUNTIME POLYFILLS — V8 Native Bridge Layer
// ═══════════════════════════════════════════════════════════════════════
// This file is injected into V8 BEFORE any user code executes.
// It provides the JavaScript API surface for all 22 omni_modules.
//
// Architecture:
//   User .omni code → Transpile to JS → This polyfill layer → OmniNative.syscall → Rust → OS
//
// Node.js needs 60+ built-in C++ modules.
// OMNI needs THIS SINGLE FILE + Rust syscalls. That's the difference.
// ═══════════════════════════════════════════════════════════════════════

// ─── Global Guards ───
if (typeof globalThis.__OMNI_POLYFILLS_LOADED__ === 'undefined') {
  globalThis.__OMNI_POLYFILLS_LOADED__ = true;

  // ═══════════════════════════════════════════
  // 📟 omni-std — Standard Library
  // ═══════════════════════════════════════════
  
  const OmniStd = {
    Result: {
      Ok: (value) => ({ _tag: 'Ok', value, isOk: true, isErr: false,
        unwrap() { return value; },
        unwrapOr(_) { return value; },
        map(f) { return OmniStd.Result.Ok(f(value)); },
      }),
      Err: (error) => ({ _tag: 'Err', error, isOk: false, isErr: true,
        unwrap() { throw new Error('Unwrap on Err: ' + error); },
        unwrapOr(fallback) { return fallback; },
        map(_) { return OmniStd.Result.Err(error); },
      }),
    },
    Option: {
      Some: (value) => ({ _tag: 'Some', value, isSome: true, isNone: false,
        unwrap() { return value; },
        unwrapOr(_) { return value; },
        map(f) { return OmniStd.Option.Some(f(value)); },
      }),
      None: { _tag: 'None', value: undefined, isSome: false, isNone: true,
        unwrap() { throw new Error('Unwrap on None'); },
        unwrapOr(fallback) { return fallback; },
        map(_) { return OmniStd.Option.None; },
      },
    },
    Vec: class {
      constructor(items = []) { this.items = [...items]; }
      static new() { return new OmniStd.Vec(); }
      push(item) { this.items.push(item); }
      pop() { return this.items.length > 0 ? OmniStd.Option.Some(this.items.pop()) : OmniStd.Option.None; }
      len() { return this.items.length; }
      map(f) { return new OmniStd.Vec(this.items.map(f)); }
      filter(f) { return new OmniStd.Vec(this.items.filter(f)); }
      reduce(f, init) { return this.items.reduce(f, init); }
      forEach(f) { this.items.forEach(f); }
      [Symbol.iterator]() { return this.items[Symbol.iterator](); }
    },
    HashMap: class {
      constructor() { this.entries = new Map(); }
      static new() { return new OmniStd.HashMap(); }
      set(key, value) { this.entries.set(key, value); }
      get(key) { return this.entries.has(key) ? OmniStd.Option.Some(this.entries.get(key)) : OmniStd.Option.None; }
      has(key) { return this.entries.has(key); }
      delete(key) { return this.entries.delete(key); }
      keys() { return new OmniStd.Vec(Array.from(this.entries.keys())); }
      values() { return new OmniStd.Vec(Array.from(this.entries.values())); }
      len() { return this.entries.size; }
    },
    Queue: class {
      constructor() { this.items = []; }
      static new() { return new OmniStd.Queue(); }
      enqueue(item) { this.items.push(item); }
      dequeue() { return this.items.length > 0 ? OmniStd.Option.Some(this.items.shift()) : OmniStd.Option.None; }
      peek() { return this.items.length > 0 ? OmniStd.Option.Some(this.items[0]) : OmniStd.Option.None; }
      len() { return this.items.length; }
      isEmpty() { return this.items.length === 0; }
    },
    Stack: class {
      constructor() { this.items = []; }
      static new() { return new OmniStd.Stack(); }
      push(item) { this.items.push(item); }
      pop() { return this.items.length > 0 ? OmniStd.Option.Some(this.items.pop()) : OmniStd.Option.None; }
      peek() { return this.items.length > 0 ? OmniStd.Option.Some(this.items[this.items.length - 1]) : OmniStd.Option.None; }
      len() { return this.items.length; }
    },
    print: (msg) => OmniNative.syscall('print', { message: String(msg) }),
    println: (msg) => OmniNative.syscall('println', { message: String(msg) }),
    assert: (condition, msg = 'Assertion failed') => condition ? OmniStd.Result.Ok(undefined) : OmniStd.Result.Err(msg),
    panic: (msg) => OmniNative.syscall('panic', { message: msg }),
    inspect: (value) => JSON.stringify(value, null, 2),
    clone: (value) => JSON.parse(JSON.stringify(value)),
    range: (start, end, step = 1) => {
      const result = new OmniStd.Vec();
      for (let i = start; i < end; i += step) result.push(i);
      return result;
    },
  };

  // ═══════════════════════════════════════════
  // ⚡ omni-runtime — Runtime Engine
  // ═══════════════════════════════════════════
  
  const OmniRuntime = {
    EventLoop: {
      nextTick: (cb) => OmniNative.syscall('runtime_next_tick', { handler: 'callback' }),
      setTimeout: (cb, ms) => { const r = OmniNative.syscall('runtime_set_timeout', { delay: ms }); if (cb) cb(); return r.timerId; },
      setInterval: (cb, ms) => OmniNative.syscall('runtime_set_interval', { delay: ms }).timerId,
      clearTimer: (id) => OmniNative.syscall('runtime_clear_timer', { id }),
    },
    spawn: (task) => {
      const r = OmniNative.syscall('runtime_spawn', { task: 'async_task' });
      if (task) task();
      return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.taskId);
    },
    sleep: (ms) => OmniNative.syscall('runtime_sleep', { delay: ms }),
    exit: (code = 0) => OmniNative.syscall('runtime_exit', { code }),
    uptime: () => OmniNative.syscall('runtime_uptime', {}).uptime,
    version: () => 'omni-runtime v1.0.0',
  };

  // ═══════════════════════════════════════════
  // 📂 omni-fs — Filesystem Operations
  // ═══════════════════════════════════════════
  
  const OmniFs = {
    readFile: (path) => { const r = OmniNative.syscall('fs_read', { path }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.data); },
    writeFile: (path, data) => { const r = OmniNative.syscall('fs_write', { path, data }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(undefined); },
    exists: (path) => OmniNative.syscall('fs_exists', { path }).exists,
    mkdir: (path, recursive = true) => { const r = OmniNative.syscall('fs_mkdir', { path, recursive }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(undefined); },
    readdir: (path) => { const r = OmniNative.syscall('fs_readdir', { path }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(new OmniStd.Vec(r.entries)); },
    remove: (path) => { const r = OmniNative.syscall('fs_remove', { path }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(undefined); },
    stat: (path) => { const r = OmniNative.syscall('fs_stat', { path }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.stat); },
    glob: (pattern, dir = '.') => { const r = OmniNative.syscall('fs_glob', { pattern, dir }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(new OmniStd.Vec(r.files)); },
  };

  // ═══════════════════════════════════════════
  // 🌍 omni-env — Environment & Platform
  // ═══════════════════════════════════════════
  
  const OmniEnv = {
    get: (key) => { const r = OmniNative.syscall('std_env_get', { key }); return r.value ? OmniStd.Option.Some(r.value) : OmniStd.Option.None; },
    getOrDefault: (key, fallback) => { const r = OmniNative.syscall('std_env_get', { key }); return r.value ?? fallback; },
    set: (key, value) => OmniNative.syscall('env_set', { key, value }),
    platform: () => OmniNative.syscall('env_platform', {}).platform,
    arch: () => OmniNative.syscall('env_arch', {}).arch,
    cwd: () => OmniNative.syscall('env_cwd', {}).cwd,
    home: () => OmniNative.syscall('env_home', {}).home,
    args: () => new OmniStd.Vec(OmniNative.syscall('env_args', {}).args),
    isProduction: () => OmniEnv.getOrDefault('OMNI_ENV', 'development') === 'production',
    isDevelopment: () => !OmniEnv.isProduction(),
  };

  // ═══════════════════════════════════════════
  // 🔐 omni-crypto — Cryptography
  // ═══════════════════════════════════════════
  
  const OmniCrypto = {
    sha256: (data) => OmniNative.syscall('std_crypto_hash', { algo: 'sha256', payload: data }).result,
    md5: (data) => OmniNative.syscall('std_crypto_hash', { algo: 'md5', payload: data }).result,
    uuid: () => OmniNative.syscall('std_crypto_uuid', {}).uuid,
    randomBytes: (size = 32) => OmniNative.syscall('crypto_random', { size }).bytes,
    hmac: (key, data, algo = 'sha256') => OmniNative.syscall('crypto_hmac', { key, data, algo }).result,
    encrypt: (plaintext, key) => { const r = OmniNative.syscall('crypto_encrypt', { plaintext, key, algo: 'aes-256-gcm' }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.ciphertext); },
    decrypt: (ciphertext, key) => { const r = OmniNative.syscall('crypto_decrypt', { ciphertext, key, algo: 'aes-256-gcm' }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.plaintext); },
    hash: (data, algo = 'sha256') => OmniNative.syscall('std_crypto_hash', { algo, payload: data }).result,
    base64: (data) => typeof btoa !== 'undefined' ? btoa(data) : data,
    base64Decode: (data) => typeof atob !== 'undefined' ? atob(data) : data,
  };

  // ═══════════════════════════════════════════
  // 🌐 omni-net — Networking
  // ═══════════════════════════════════════════
  
  const OmniNet = {
    HttpResponse: class {
      constructor(status, headers, body) { this.status = status; this.headers = headers; this.body = body; }
      json() { try { return OmniStd.Result.Ok(JSON.parse(this.body)); } catch(e) { return OmniStd.Result.Err('Invalid JSON'); } }
      ok() { return this.status >= 200 && this.status < 300; }
    },
    fetch: (url, options = {}) => {
      const r = OmniNative.syscall('http_fetch', { url, method: options.method || 'GET', headers: options.headers || {}, body: options.body || '' });
      return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(new OmniNet.HttpResponse(r.status, r.headers, r.body));
    },
    get: (url) => OmniNet.fetch(url),
    post: (url, body) => OmniNet.fetch(url, { method: 'POST', body: JSON.stringify(body), headers: { 'Content-Type': 'application/json' } }),
    put: (url, body) => OmniNet.fetch(url, { method: 'PUT', body: JSON.stringify(body), headers: { 'Content-Type': 'application/json' } }),
    del: (url) => OmniNet.fetch(url, { method: 'DELETE' }),
    WebSocket: class {
      constructor(url) { this.url = url; }
      static connect(url) { const r = OmniNative.syscall('ws_connect', { url }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(new OmniNet.WebSocket(url)); }
      send(data) { OmniNative.syscall('ws_send', { data }); }
      close() { OmniNative.syscall('ws_close', {}); }
    },
  };

  // ═══════════════════════════════════════════
  // ⚙️ omni-process — Process Management
  // ═══════════════════════════════════════════
  
  const OmniProcess = {
    exec: (command, args = []) => {
      const r = OmniNative.syscall('process_exec', { command, args });
      return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok({ exitCode: r.exitCode, stdout: r.stdout, stderr: r.stderr });
    },
    spawn: (command, args = []) => {
      const r = OmniNative.syscall('process_spawn', { command, args });
      return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.pid);
    },
    kill: (pid, signal = 'SIGTERM') => {
      const r = OmniNative.syscall('process_kill', { pid, signal });
      return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(undefined);
    },
    pid: () => OmniNative.syscall('process_pid', {}).pid,
    ppid: () => OmniNative.syscall('process_ppid', {}).ppid,
    memoryUsage: () => OmniNative.syscall('process_memory', {}),
  };

  // ═══════════════════════════════════════════
  // 🗄️ omni-db — Database ORM
  // ═══════════════════════════════════════════
  
  const OmniDb = {
    Database: class {
      constructor(driver, connectionString) { this.driver = driver; this.connectionString = connectionString; this.connected = false; }
      static connect(driver, connectionString) {
        const r = OmniNative.syscall('db_connect', { driver, connectionString });
        if (r.error) return OmniStd.Result.Err(r.error);
        const db = new OmniDb.Database(driver, connectionString);
        db.connected = true;
        return OmniStd.Result.Ok(db);
      }
      query(sql, params = []) { const r = OmniNative.syscall('db_query', { sql, params }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(new OmniStd.Vec(r.rows)); }
      execute(sql, params = []) { const r = OmniNative.syscall('db_execute', { sql, params }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.affected); }
      close() { OmniNative.syscall('db_close', {}); }
    },
    Model: class {
      constructor(table, db) { this.table = table; this.db = db; }
      findAll() { return this.db.query('SELECT * FROM ' + this.table); }
      findById(id) { return this.db.query('SELECT * FROM ' + this.table + ' WHERE id = ?', [id]).map(rows => rows.len() > 0 ? OmniStd.Option.Some(rows.items[0]) : OmniStd.Option.None); }
      create(data) { const r = OmniNative.syscall('db_insert', { table: this.table, data }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.record); }
      update(id, data) { const r = OmniNative.syscall('db_update', { table: this.table, id, data }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.record); }
      delete(id) { return this.db.execute('DELETE FROM ' + this.table + ' WHERE id = ?', [id]).map(_ => undefined); }
    },
    postgres: (url) => OmniDb.Database.connect('postgres', url),
    sqlite: (path) => OmniDb.Database.connect('sqlite', path),
    redis: (url) => OmniDb.Database.connect('redis', url),
  };

  // ═══════════════════════════════════════════
  // 💾 omni-cache — Cache Layer
  // ═══════════════════════════════════════════
  
  const OmniCache = {
    Cache: class {
      constructor(maxSize = 1000, defaultTTL = 3600000) {
        this.store = new Map();
        this.maxSize = maxSize;
        this.defaultTTL = defaultTTL;
      }
      static new(maxSize, defaultTTL) { return new OmniCache.Cache(maxSize, defaultTTL); }
      get(key) {
        const entry = this.store.get(key);
        if (!entry) return OmniStd.Option.None;
        if (Date.now() > entry.expiresAt) { this.store.delete(key); return OmniStd.Option.None; }
        entry.hits++;
        return OmniStd.Option.Some(entry.value);
      }
      set(key, value, ttl) {
        if (this.store.size >= this.maxSize) this.evictLRU();
        this.store.set(key, { value, expiresAt: Date.now() + (ttl || this.defaultTTL), hits: 0, createdAt: Date.now() });
      }
      has(key) { return this.get(key).isSome; }
      delete(key) { return this.store.delete(key); }
      clear() { this.store.clear(); }
      size() { return this.store.size; }
      evictLRU() {
        let oldestKey = null, oldestTime = Infinity;
        for (const [k, v] of this.store) { if (v.createdAt < oldestTime) { oldestTime = v.createdAt; oldestKey = k; } }
        if (oldestKey) this.store.delete(oldestKey);
      }
    },
  };

  // ═══════════════════════════════════════════
  // 🌊 omni-stream — Data Streaming
  // ═══════════════════════════════════════════
  
  const OmniStream = {
    Stream: class {
      constructor(topic) { this.topic = topic; this.handlers = []; }
      static create(topic) { return new OmniStream.Stream(topic); }
      produce(data) { OmniNative.syscall('stream_produce', { topic: this.topic, data }); this.handlers.forEach(h => h(data)); return OmniStd.Result.Ok(undefined); }
      consume(handler) { this.handlers.push(handler); }
      pipe(target) { this.consume(data => target.produce(data)); }
    },
    PubSub: class {
      constructor() { this.channels = new Map(); }
      static new() { return new OmniStream.PubSub(); }
      subscribe(channel, handler) {
        if (!this.channels.has(channel)) this.channels.set(channel, []);
        this.channels.get(channel).push(handler);
      }
      publish(channel, data) { (this.channels.get(channel) || []).forEach(h => h(data)); }
      unsubscribe(channel) { this.channels.delete(channel); }
    },
  };

  // ═══════════════════════════════════════════
  // 🔐 omni-auth — Authentication
  // ═══════════════════════════════════════════
  
  const OmniAuth = {
    JWT: {
      sign: (payload, secret, expiresIn = 3600) => {
        const header = { alg: 'HS256', typ: 'JWT' };
        const claims = { ...payload, iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + expiresIn };
        const segments = [OmniCrypto.base64(JSON.stringify(header)), OmniCrypto.base64(JSON.stringify(claims))];
        const signature = OmniCrypto.hmac(secret, segments.join('.'));
        return segments.join('.') + '.' + signature;
      },
      verify: (token, secret) => {
        const parts = token.split('.');
        if (parts.length !== 3) return OmniStd.Result.Err('Invalid JWT format');
        const expectedSig = OmniCrypto.hmac(secret, parts[0] + '.' + parts[1]);
        if (expectedSig !== parts[2]) return OmniStd.Result.Err('Invalid signature');
        try {
          const payload = JSON.parse(OmniCrypto.base64Decode(parts[1]));
          if (payload.exp && payload.exp < Date.now() / 1000) return OmniStd.Result.Err('Token expired');
          return OmniStd.Result.Ok(payload);
        } catch(e) { return OmniStd.Result.Err('Invalid payload'); }
      },
      decode: (token) => {
        const parts = token.split('.');
        if (parts.length !== 3) return OmniStd.Result.Err('Invalid JWT format');
        try { return OmniStd.Result.Ok(JSON.parse(OmniCrypto.base64Decode(parts[1]))); }
        catch(e) { return OmniStd.Result.Err('Invalid payload'); }
      },
    },
    hashPassword: (password) => OmniCrypto.sha256(password + 'omni_salt_v1'),
    verifyPassword: (password, hash) => OmniAuth.hashPassword(password) === hash,
  };

  // ═══════════════════════════════════════════
  // 🌐 omni-http — HTTP Framework
  // ═══════════════════════════════════════════
  
  const OmniHttp = {
    App: class {
      constructor() { this.routes = []; this.middlewares = []; }
      static new() { return new OmniHttp.App(); }
      get(path, handler) { this.routes.push({ method: 'GET', path, handler }); }
      post(path, handler) { this.routes.push({ method: 'POST', path, handler }); }
      put(path, handler) { this.routes.push({ method: 'PUT', path, handler }); }
      delete(path, handler) { this.routes.push({ method: 'DELETE', path, handler }); }
      use(middleware) { this.middlewares.push(middleware); }
      listen(port) {
        OmniNative.syscall('http_serve', { port, routes: this.routes, middlewares: this.middlewares });
        OmniStd.println('🌐 OMNI Server listening on port ' + port);
        return OmniStd.Result.Ok(undefined);
      }
      group(prefix) { return { prefix, app: this }; }
    },
  };

  // ═══════════════════════════════════════════
  // 📊 omni-graphql — GraphQL Engine
  // ═══════════════════════════════════════════
  
  const OmniGraphQL = {
    GraphQLSchema: class {
      constructor() { this.types = []; this.queries = new Map(); this.mutations = new Map(); }
      static new() { return new OmniGraphQL.GraphQLSchema(); }
      type(name, fields) { this.types.push({ name, fields }); }
      query(name, resolver) { this.queries.set(name, resolver); }
      mutation(name, resolver) { this.mutations.set(name, resolver); }
      execute(query, variables = {}) { return OmniNative.syscall('graphql_execute', { schema: this, query, variables }); }
    },
  };

  // ═══════════════════════════════════════════
  // 📋 omni-queue — Job Queue
  // ═══════════════════════════════════════════
  
  const OmniQueue = {
    JobQueue: class {
      constructor(name, maxRetries = 3) { this.name = name; this.handlers = new Map(); this.maxRetries = maxRetries; }
      static new(name, maxRetries) { return new OmniQueue.JobQueue(name, maxRetries); }
      process(jobType, handler) { this.handlers.set(jobType, handler); }
      dispatch(jobType, payload) {
        const r = OmniNative.syscall('queue_dispatch', { name: jobType, payload, max_retry: this.maxRetries });
        return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.jobId);
      }
      schedule(jobType, payload, delayMs) { return OmniNative.syscall('queue_schedule', { name: jobType, payload, delay: delayMs }); }
      stats() { return OmniNative.syscall('queue_stats', { name: this.name }); }
    },
  };

  // ═══════════════════════════════════════════
  // 📝 omni-log — Structured Logging
  // ═══════════════════════════════════════════
  
  const LogLevel = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3, FATAL: 4 };
  
  const OmniLog = {
    LogLevel,
    Logger: class {
      constructor(name, level = LogLevel.INFO) { this.name = name; this.level = level; }
      static new(name, level) { return new OmniLog.Logger(name, level); }
      debug(msg, data = {}) { this._log(LogLevel.DEBUG, '🔍', msg, data); }
      info(msg, data = {}) { this._log(LogLevel.INFO, 'ℹ️', msg, data); }
      warn(msg, data = {}) { this._log(LogLevel.WARN, '⚠️', msg, data); }
      error(msg, data = {}) { this._log(LogLevel.ERROR, '❌', msg, data); }
      fatal(msg, data = {}) { this._log(LogLevel.FATAL, '💀', msg, data); }
      _log(level, icon, msg) { if (level >= this.level) OmniStd.println(icon + ' [' + this.name + '] ' + msg); }
      child(name) { return new OmniLog.Logger(this.name + ':' + name, this.level); }
    },
  };

  // ═══════════════════════════════════════════
  // ⚙️ omni-config — Configuration
  // ═══════════════════════════════════════════
  
  const OmniConfig = {
    Config: class {
      constructor() { this.data = new Map(); }
      static new() { return new OmniConfig.Config(); }
      static load(path) {
        const content = OmniFs.readFile(path);
        if (content.isErr) return content;
        try {
          const parsed = JSON.parse(content.value);
          const config = new OmniConfig.Config();
          for (const key of Object.keys(parsed)) config.data.set(key, parsed[key]);
          return OmniStd.Result.Ok(config);
        } catch(e) { return OmniStd.Result.Err('Invalid JSON config'); }
      }
      get(key) { return this.data.has(key) ? OmniStd.Option.Some(this.data.get(key)) : OmniStd.Option.None; }
      getOrDefault(key, fallback) { return this.data.has(key) ? this.data.get(key) : fallback; }
      set(key, value) { this.data.set(key, value); }
      has(key) { return this.data.has(key); }
      merge(other) { for (const [k, v] of other.data) this.data.set(k, v); return this; }
    },
  };

  // ═══════════════════════════════════════════
  // 🧪 omni-validate — Schema Validation
  // ═══════════════════════════════════════════
  
  const OmniValidate = {
    Schema: class {
      constructor(rules = [], fieldName = '') { this.rules = [...rules]; this.fieldName = fieldName; }
      static string(name = '') { return new OmniValidate.Schema([{ type: 'string' }], name); }
      static number(name = '') { return new OmniValidate.Schema([{ type: 'number' }], name); }
      static boolean(name = '') { return new OmniValidate.Schema([{ type: 'boolean' }], name); }
      required() { this.rules.push({ rule: 'required' }); return this; }
      min(val) { this.rules.push({ rule: 'min', value: val }); return this; }
      max(val) { this.rules.push({ rule: 'max', value: val }); return this; }
      email() { this.rules.push({ rule: 'email' }); return this; }
      validate(data) {
        const errors = [];
        for (const rule of this.rules) {
          if (rule.rule === 'required' && (data === null || data === undefined)) errors.push(this.fieldName + ' is required');
          if (rule.rule === 'min' && data < rule.value) errors.push(this.fieldName + ' must be >= ' + rule.value);
          if (rule.rule === 'max' && data > rule.value) errors.push(this.fieldName + ' must be <= ' + rule.value);
          if (rule.rule === 'email' && !String(data).includes('@')) errors.push(this.fieldName + ' must be a valid email');
        }
        return errors.length > 0 ? OmniStd.Result.Err(errors) : OmniStd.Result.Ok(data);
      }
    },
    sanitize: (input) => String(input).replace(/<script>/gi, '').replace(/javascript:/gi, '').replace(/onerror=/gi, ''),
  };

  // ═══════════════════════════════════════════
  // 🤖 omni-ai — AI & Machine Learning
  // ═══════════════════════════════════════════
  
  const OmniAI = {
    AI: {
      infer: (model, input, options = {}) => { const r = OmniNative.syscall('ai_infer', { model, input, options }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.output || r); },
      embed: (text, model = 'default') => { const r = OmniNative.syscall('ai_embed', { text, model }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(new OmniStd.Vec(r.embedding || [])); },
      generate: (prompt, options = {}) => { const r = OmniNative.syscall('ai_generate', { prompt, ...options }); return r.error ? OmniStd.Result.Err(r.error) : OmniStd.Result.Ok(r.text || ''); },
    },
    Pipeline: class {
      constructor() { this.steps = []; }
      static new() { return new OmniAI.Pipeline(); }
      add(name, processor) { this.steps.push({ name, processor }); return this; }
      run(input) { let result = input; for (const step of this.steps) result = step.processor(result); return OmniStd.Result.Ok(result); }
    },
    cosineSimilarity: (a, b) => {
      let dot = 0, magA = 0, magB = 0;
      for (let i = 0; i < a.length; i++) { dot += a[i] * b[i]; magA += a[i] * a[i]; magB += b[i] * b[i]; }
      return dot / (Math.sqrt(magA) * Math.sqrt(magB));
    },
  };

  // ═══════════════════════════════════════════
  // 📊 omni-monitor — Observability
  // ═══════════════════════════════════════════
  
  const OmniMonitor = {
    Metrics: class {
      constructor() { this.counters = new Map(); this.gauges = new Map(); this.histograms = new Map(); }
      static new() { return new OmniMonitor.Metrics(); }
      counter(name, value = 1) { this.counters.set(name, (this.counters.get(name) || 0) + value); }
      gauge(name, value) { this.gauges.set(name, value); }
      histogram(name, value) { if (!this.histograms.has(name)) this.histograms.set(name, []); this.histograms.get(name).push(value); }
      snapshot() { return { counters: Object.fromEntries(this.counters), gauges: Object.fromEntries(this.gauges), histograms: Object.fromEntries(this.histograms) }; }
    },
    HealthCheck: class {
      constructor() { this.checks = []; }
      static new() { return new OmniMonitor.HealthCheck(); }
      add(name, checker) { this.checks.push({ name, checker }); }
      run() {
        const results = []; let healthy = true;
        for (const check of this.checks) {
          const r = check.checker();
          if (r.isOk) results.push({ name: check.name, status: 'OK', message: r.value });
          else { results.push({ name: check.name, status: 'FAIL', message: r.error }); healthy = false; }
        }
        return { healthy, results };
      }
    },
    Tracer: class {
      constructor() { this.spans = []; }
      static new() { return new OmniMonitor.Tracer(); }
      span(name) { const s = { name, start: Date.now(), end: 0, finish() { this.end = Date.now(); } }; this.spans.push(s); return s; }
    },
  };

  // ═══════════════════════════════════════════
  // 🖥️ omni-cli — CLI Toolkit
  // ═══════════════════════════════════════════
  
  const OmniCli = {
    CLI: class {
      constructor(name, version = '1.0.0') { this.name = name; this.version = version; this.commands = new Map(); }
      static new(name, version) { return new OmniCli.CLI(name, version); }
      command(name, desc, handler) { this.commands.set(name, { name, description: desc, handler }); }
      run(argv) {
        if (argv.length < 1) { this.printHelp(); return; }
        const cmd = this.commands.get(argv[0]);
        if (cmd) cmd.handler({});
        else { OmniStd.println('Unknown command: ' + argv[0]); this.printHelp(); }
      }
      printHelp() {
        OmniStd.println(this.name + ' v' + this.version);
        for (const [, cmd] of this.commands) OmniStd.println('  ' + cmd.name + '  ' + cmd.description);
      }
    },
    color: (text, code) => '\x1b[' + code + 'm' + text + '\x1b[0m',
    red: (text) => OmniCli.color(text, '31'),
    green: (text) => OmniCli.color(text, '32'),
    yellow: (text) => OmniCli.color(text, '33'),
    blue: (text) => OmniCli.color(text, '34'),
    bold: (text) => OmniCli.color(text, '1'),
    spinner: (msg) => OmniStd.println('⏳ ' + msg + '...'),
    success: (msg) => OmniStd.println(OmniCli.green('✅ ' + msg)),
    error: (msg) => OmniStd.println(OmniCli.red('❌ ' + msg)),
  };

  // ═══════════════════════════════════════════
  // 📝 omni-types — Type System Helpers
  // ═══════════════════════════════════════════
  
  const OmniTypes = {
    Money: class {
      constructor(amount, currency = 'USD') { this.amount = amount; this.currency = currency; }
      static new(amount, currency) { return new OmniTypes.Money(amount, currency); }
      add(other) { return this.currency !== other.currency ? OmniStd.Result.Err('Currency mismatch') : OmniStd.Result.Ok(new OmniTypes.Money(this.amount + other.amount, this.currency)); }
      subtract(other) { return this.currency !== other.currency ? OmniStd.Result.Err('Currency mismatch') : OmniStd.Result.Ok(new OmniTypes.Money(this.amount - other.amount, this.currency)); }
      multiply(factor) { return new OmniTypes.Money(this.amount * factor, this.currency); }
      format() { return this.currency + ' ' + this.amount.toFixed(2); }
    },
    Duration: class {
      constructor(ms) { this.ms = ms; }
      static fromSeconds(s) { return new OmniTypes.Duration(s * 1000); }
      static fromMinutes(m) { return new OmniTypes.Duration(m * 60000); }
      static fromHours(h) { return new OmniTypes.Duration(h * 3600000); }
      toSeconds() { return this.ms / 1000; }
      toMinutes() { return this.ms / 60000; }
    },
    Range: class {
      constructor(start, end) { this.start = start; this.end = end; }
      contains(value) { return value >= this.start && value <= this.end; }
    },
  };

  // ═══════════════════════════════════════════
  // 🧪 omni-test — Testing Framework
  // ═══════════════════════════════════════════
  
  const OmniTest = {
    describe: (name, suite) => { OmniStd.println('  ' + name); suite(); },
    it: (name, test) => { try { test(); OmniStd.println('    ✅ ' + name); } catch(e) { OmniStd.println('    ❌ ' + name + ' — ' + e.message); } },
    expect: (value) => ({
      toBe: (expected) => { if (value !== expected) throw new Error('Expected ' + expected + ', got ' + value); },
      toEqual: (expected) => { if (JSON.stringify(value) !== JSON.stringify(expected)) throw new Error('Deep equality failed'); },
      toBeTrue: () => { if (value !== true) throw new Error('Expected true'); },
      toBeFalse: () => { if (value !== false) throw new Error('Expected false'); },
      toBeNull: () => { if (value !== null) throw new Error('Expected null'); },
      toContain: (item) => { if (!value.includes(item)) throw new Error('Expected to contain ' + item); },
      toBeGreaterThan: (n) => { if (!(value > n)) throw new Error('Expected > ' + n); },
      toBeLessThan: (n) => { if (!(value < n)) throw new Error('Expected < ' + n); },
      toHaveLength: (n) => { if (value.length !== n) throw new Error('Expected length ' + n + ', got ' + value.length); },
    }),
    mock: (impl = null) => ({ calls: [], impl }),
    beforeEach: (setup) => { setup(); },
    afterEach: (teardown) => { teardown(); },
  };

  // ═══════════════════════════════════════════
  // 🔗 GLOBAL MODULE REGISTRY
  // ═══════════════════════════════════════════
  // Make all modules available via import-like access
  
  globalThis.omni_std = OmniStd;
  globalThis.omni_runtime = OmniRuntime;
  globalThis.omni_fs = OmniFs;
  globalThis.omni_env = OmniEnv;
  globalThis.omni_crypto = OmniCrypto;
  globalThis.omni_net = OmniNet;
  globalThis.omni_process = OmniProcess;
  globalThis.omni_db = OmniDb;
  globalThis.omni_cache = OmniCache;
  globalThis.omni_stream = OmniStream;
  globalThis.omni_auth = OmniAuth;
  globalThis.omni_http = OmniHttp;
  globalThis.omni_graphql = OmniGraphQL;
  globalThis.omni_queue = OmniQueue;
  globalThis.omni_log = OmniLog;
  globalThis.omni_config = OmniConfig;
  globalThis.omni_validate = OmniValidate;
  globalThis.omni_ai = OmniAI;
  globalThis.omni_monitor = OmniMonitor;
  globalThis.omni_cli = OmniCli;
  globalThis.omni_types = OmniTypes;
  globalThis.omni_test = OmniTest;
  
  // Re-export core primitives to global scope for ergonomics
  globalThis.Ok = OmniStd.Result.Ok;
  globalThis.Err = OmniStd.Result.Err;
  globalThis.Some = OmniStd.Option.Some;
  globalThis.None = OmniStd.Option.None;
  globalThis.Vec = OmniStd.Vec;
  globalThis.HashMap = OmniStd.HashMap;
  globalThis.println = OmniStd.println;
  globalThis.print_ = OmniStd.print;
  
  // ═══════════════════════════════════════════
  // 🏁 OMNI RUNTIME READY
  // ═══════════════════════════════════════════
}
