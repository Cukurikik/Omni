// ===========================================================================
// OMNI DOMAIN LAYER — SYSBOT.NET REMOTE CONSOLE AUTOMATION
// ===========================================================================
// Source Paradigm : kwsch/SysBot.NET
// Domain Layer   : Domain (DDD aggregate, enterprise automation controller)
// Language        : C#
// Function        : Remote Nintendo Switch controller via sys-botbase protocol
//                   with button press commands, stick manipulation, screen
//                   capture, memory read/write, and routine orchestration
// ===========================================================================

using System;
using System.Collections.Generic;
using System.Text;

namespace OmniDomain.SysBot
{
    // ---- Enums ----------------------------------------------------------------

    public enum SwitchButton
    {
        A, B, X, Y,
        DUP, DDOWN, DLEFT, DRIGHT,
        L, R, ZL, ZR,
        PLUS, MINUS, HOME, CAPTURE,
        LSTICK, RSTICK
    }

    public enum BotStatus
    {
        Idle,
        Running,
        Paused,
        Error,
        Disconnected
    }

    public enum ConnectionType
    {
        WiFi,
        USB
    }

    // ---- Data Models ----------------------------------------------------------

    public class SwitchConnection
    {
        public string IpAddress { get; set; }
        public int Port { get; set; } = 6000;
        public ConnectionType Type { get; set; } = ConnectionType.WiFi;
        public bool IsConnected { get; set; }
        public DateTime? ConnectedAt { get; set; }

        /// <summary>Build sys-botbase command string.</summary>
        public string BuildCommand(string cmd)
        {
            return cmd + "\r\n";
        }
    }

    public class StickPosition
    {
        public short X { get; set; }  // -32768 to 32767
        public short Y { get; set; }
        public int DurationMs { get; set; }

        public static StickPosition Neutral => new() { X = 0, Y = 0, DurationMs = 0 };
        public static StickPosition Up => new() { X = 0, Y = 32767, DurationMs = 500 };
        public static StickPosition Down => new() { X = 0, Y = -32768, DurationMs = 500 };
        public static StickPosition Left => new() { X = -32768, Y = 0, DurationMs = 500 };
        public static StickPosition Right => new() { X = 32767, Y = 0, DurationMs = 500 };
    }

    public class MemoryRegion
    {
        public ulong Address { get; set; }
        public int Size { get; set; }
        public byte[] Data { get; set; }
    }

    // ---- Routine System -------------------------------------------------------

    public class RoutineStep
    {
        public string Description { get; set; }
        public Action<SysBotController> Execute { get; set; }
        public int DelayAfterMs { get; set; } = 100;
    }

    public class BotRoutine
    {
        public string Name { get; set; }
        public List<RoutineStep> Steps { get; set; } = new();
        public int RepeatCount { get; set; } = 1;
        public bool StopOnError { get; set; } = true;
    }

    // ---- Core Controller ------------------------------------------------------

    public class SysBotController
    {
        private readonly SwitchConnection _connection;
        private BotStatus _status = BotStatus.Disconnected;
        private readonly List<string> _commandLog = new();

        public SysBotController(string ip, int port = 6000)
        {
            _connection = new SwitchConnection
            {
                IpAddress = ip,
                Port = port,
                Type = ConnectionType.WiFi
            };
            Console.WriteLine($"[SYSBOT-OMNI-CS] Controller created for {ip}:{port}");
        }

        // ---- Connection -------------------------------------------------------

        public bool Connect()
        {
            Console.WriteLine($"[SYSBOT-OMNI-CS] Connecting to {_connection.IpAddress}:{_connection.Port}...");
            // Production: TcpClient connect to sys-botbase
            _connection.IsConnected = true;
            _connection.ConnectedAt = DateTime.UtcNow;
            _status = BotStatus.Idle;
            Console.WriteLine("[SYSBOT-OMNI-CS] Connected successfully.");
            return true;
        }

        public void Disconnect()
        {
            _connection.IsConnected = false;
            _status = BotStatus.Disconnected;
            Console.WriteLine("[SYSBOT-OMNI-CS] Disconnected.");
        }

        // ---- Button Commands --------------------------------------------------

        public void Click(SwitchButton button, int holdMs = 50)
        {
            string cmd = $"click {button}";
            SendCommand(cmd);
            Console.WriteLine($"[SYSBOT-OMNI-CS] Click: {button} (hold {holdMs}ms)");
        }

        public void Press(SwitchButton button, int holdMs = 500)
        {
            SendCommand($"press {button}");
            Console.WriteLine($"[SYSBOT-OMNI-CS] Press & hold: {button} ({holdMs}ms)");
        }

        // ---- Stick Commands ---------------------------------------------------

        public void SetStick(string stick, StickPosition pos)
        {
            string cmd = $"setStick {stick} {pos.X} {pos.Y} {pos.DurationMs}";
            SendCommand(cmd);
            Console.WriteLine($"[SYSBOT-OMNI-CS] Stick {stick}: ({pos.X}, {pos.Y}) for {pos.DurationMs}ms");
        }

        public void ResetStick(string stick)
        {
            SetStick(stick, StickPosition.Neutral);
        }

        // ---- Memory Operations ------------------------------------------------

        public byte[] ReadMemory(ulong address, int size)
        {
            string cmd = $"peek 0x{address:X} {size}";
            SendCommand(cmd);
            Console.WriteLine($"[SYSBOT-OMNI-CS] Read {size} bytes from 0x{address:X}");
            // Production: parse hex response from sys-botbase
            return new byte[size];
        }

        public void WriteMemory(ulong address, byte[] data)
        {
            string hexData = BitConverter.ToString(data).Replace("-", "");
            string cmd = $"poke 0x{address:X} 0x{hexData}";
            SendCommand(cmd);
            Console.WriteLine($"[SYSBOT-OMNI-CS] Wrote {data.Length} bytes to 0x{address:X}");
        }

        // ---- Screen Control ---------------------------------------------------

        public void SetScreenOn() => SendCommand("screenOn");
        public void SetScreenOff() => SendCommand("screenOff");

        public byte[] CaptureScreen()
        {
            SendCommand("screenCapture");
            Console.WriteLine("[SYSBOT-OMNI-CS] Screen captured.");
            // Production: receive JPEG data
            return Array.Empty<byte>();
        }

        // ---- Routine Execution ------------------------------------------------

        public void ExecuteRoutine(BotRoutine routine)
        {
            Console.WriteLine($"[SYSBOT-OMNI-CS] ═════ Executing routine: {routine.Name} ═════");
            _status = BotStatus.Running;

            for (int rep = 0; rep < routine.RepeatCount; rep++)
            {
                Console.WriteLine($"[SYSBOT-OMNI-CS] Iteration {rep + 1}/{routine.RepeatCount}");

                foreach (var step in routine.Steps)
                {
                    Console.WriteLine($"[SYSBOT-OMNI-CS]   Step: {step.Description}");
                    try
                    {
                        step.Execute(this);
                        // Production: Task.Delay(step.DelayAfterMs)
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[SYSBOT-OMNI-CS]   ERROR: {ex.Message}");
                        if (routine.StopOnError)
                        {
                            _status = BotStatus.Error;
                            return;
                        }
                    }
                }
            }

            _status = BotStatus.Idle;
            Console.WriteLine($"[SYSBOT-OMNI-CS] ═════ Routine complete ═════");
        }

        // ---- Internal ---------------------------------------------------------

        private void SendCommand(string cmd)
        {
            string full = _connection.BuildCommand(cmd);
            _commandLog.Add(full);
            // Production: stream.Write(Encoding.UTF8.GetBytes(full))
        }

        public BotStatus Status => _status;
        public int CommandCount => _commandLog.Count;
    }
}
