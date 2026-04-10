// omni-velocity-js â€” Client-Side Logger

export enum LogLevel { DEBUG = 0, INFO = 1, WARN = 2, ERROR = 3, FATAL = 4 }

export class Logger {
  private level: LogLevel;
  private prefix: string;
  constructor(prefix: string = 'omni-velocity-js', level: LogLevel = LogLevel.INFO) { this.prefix = prefix; this.level = level; }
  private log(lvl: LogLevel, msg: string, ...args: unknown[]) { if (lvl >= this.level) console.log('[' + this.prefix + '][' + LogLevel[lvl] + '] ' + msg, ...args); }
  debug(msg: string, ...args: unknown[]) { this.log(LogLevel.DEBUG, msg, ...args); }
  info(msg: string, ...args: unknown[]) { this.log(LogLevel.INFO, msg, ...args); }
  warn(msg: string, ...args: unknown[]) { this.log(LogLevel.WARN, msg, ...args); }
  error(msg: string, ...args: unknown[]) { this.log(LogLevel.ERROR, msg, ...args); }
  fatal(msg: string, ...args: unknown[]) { this.log(LogLevel.FATAL, msg, ...args); }
}