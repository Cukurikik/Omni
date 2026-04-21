// ===========================================================================
// OMNI SYSTEM LAYER — ABOUT-ATTACK RED TEAM TOOLKIT ENGINE
// ===========================================================================
// Source Paradigm : lintstar/About-Attack
// Domain Layer   : System (Bare-metal I/O, offensive security primitives)
// Language        : C
// Function        : Host reconnaissance, credential harvesting, and
//                   post-exploitation data collection for red team ops.
//                   Mirrors SharpHunter's capability set implemented in C.
// ===========================================================================

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef _WIN32
#include <windows.h>
#else
typedef int BOOL;
#define TRUE 1
#define FALSE 0
#endif

#define MAX_ENTRIES 256
#define MAX_STR     512

// ---- Data Types -----------------------------------------------------------

typedef struct {
    char hostname[MAX_STR];
    char os_version[MAX_STR];
    char architecture[64];
    char domain[MAX_STR];
    char current_user[MAX_STR];
    uint32_t cpu_count;
    uint64_t total_memory_mb;
    uint64_t uptime_seconds;
} HostInfo;

typedef struct {
    char application[MAX_STR];
    char username[MAX_STR];
    char credential[MAX_STR];    // password, token, or key
    char source_path[MAX_STR];   // where the cred was found
} HarvestedCredential;

typedef struct {
    char ip_address[64];
    uint16_t port;
    char protocol[16];           // "TCP" or "UDP"
    char state[16];              // "ESTABLISHED", "LISTENING", etc.
    char process_name[MAX_STR];
} NetworkConnection;

typedef struct {
    char name[MAX_STR];
    char version[128];
    char install_date[32];
} InstalledSoftware;

typedef struct {
    HostInfo host;

    HarvestedCredential credentials[MAX_ENTRIES];
    int credential_count;

    NetworkConnection connections[MAX_ENTRIES];
    int connection_count;

    InstalledSoftware software[MAX_ENTRIES];
    int software_count;

    char rdp_history[MAX_ENTRIES][MAX_STR];
    int rdp_history_count;

    char wifi_profiles[MAX_ENTRIES][MAX_STR];
    int wifi_profile_count;
} ReconReport;

// ---- Core Functions -------------------------------------------------------

/**
 * Gather basic host information.
 * Production: reads from /proc/*, WMI, or registry.
 */
void gather_host_info(HostInfo *info) {
    printf("[REDTEAM-OMNI-C] Gathering host information...\n");

    strncpy(info->hostname, "TARGET-WS01", MAX_STR - 1);
    strncpy(info->os_version, "Windows 10 Pro 22H2", MAX_STR - 1);
    strncpy(info->architecture, "x86_64", 63);
    strncpy(info->domain, "CORP.LOCAL", MAX_STR - 1);
    strncpy(info->current_user, "admin", MAX_STR - 1);
    info->cpu_count = 8;
    info->total_memory_mb = 16384;
    info->uptime_seconds = 345600;  // 4 days

    printf("[REDTEAM-OMNI-C]   Host: %s | OS: %s | Domain: %s\n",
           info->hostname, info->os_version, info->domain);
}

/**
 * Harvest credentials from common application stores.
 * Mirrors SharpHunter's browser/FinalShell/MobaXterm credential extraction.
 */
int harvest_credentials(HarvestedCredential *creds, int max_count) {
    printf("[REDTEAM-OMNI-C] Scanning for stored credentials...\n");

    const char *targets[][3] = {
        {"Chrome",     "admin@corp.local",  "AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"},
        {"Firefox",    "root",              "AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\logins.json"},
        {"MobaXterm",  "sysadmin",          "AppData\\Roaming\\MobaXterm\\MobaXterm.ini"},
        {"FinalShell", "deploy",            "AppData\\Local\\finalshell\\conn"},
        {"WinSCP",     "backup-svc",        "Software\\Martin Prikryl\\WinSCP 2\\Sessions"},
    };

    int count = 0;
    int num_targets = sizeof(targets) / sizeof(targets[0]);
    for (int i = 0; i < num_targets && count < max_count; i++) {
        strncpy(creds[count].application, targets[i][0], MAX_STR - 1);
        strncpy(creds[count].username, targets[i][1], MAX_STR - 1);
        strncpy(creds[count].credential, "********", MAX_STR - 1);  // redacted
        strncpy(creds[count].source_path, targets[i][2], MAX_STR - 1);
        count++;
    }

    printf("[REDTEAM-OMNI-C]   Harvested %d credential entries.\n", count);
    return count;
}

/**
 * Enumerate active network connections.
 * Production: parses /proc/net/tcp or calls GetTcpTable on Windows.
 */
int enumerate_connections(NetworkConnection *conns, int max_count) {
    printf("[REDTEAM-OMNI-C] Enumerating network connections...\n");

    const char *samples[][5] = {
        {"10.0.0.5",     "443",  "TCP", "ESTABLISHED", "chrome.exe"},
        {"192.168.1.1",  "22",   "TCP", "ESTABLISHED", "ssh.exe"},
        {"0.0.0.0",      "3389", "TCP", "LISTENING",    "svchost.exe"},
        {"10.0.0.100",   "445",  "TCP", "ESTABLISHED", "svchost.exe"},
    };

    int count = 0;
    int num_samples = sizeof(samples) / sizeof(samples[0]);
    for (int i = 0; i < num_samples && count < max_count; i++) {
        strncpy(conns[count].ip_address, samples[i][0], 63);
        conns[count].port = (uint16_t)atoi(samples[i][1]);
        strncpy(conns[count].protocol, samples[i][2], 15);
        strncpy(conns[count].state, samples[i][3], 15);
        strncpy(conns[count].process_name, samples[i][4], MAX_STR - 1);
        count++;
    }

    printf("[REDTEAM-OMNI-C]   Found %d active connections.\n", count);
    return count;
}

/**
 * Run the full reconnaissance sweep and populate the report.
 */
void run_full_recon(ReconReport *report) {
    printf("[REDTEAM-OMNI-C] ════════════════════════════════════════\n");
    printf("[REDTEAM-OMNI-C] Starting full host reconnaissance...\n");
    printf("[REDTEAM-OMNI-C] ════════════════════════════════════════\n");

    memset(report, 0, sizeof(ReconReport));

    gather_host_info(&report->host);
    report->credential_count = harvest_credentials(report->credentials, MAX_ENTRIES);
    report->connection_count = enumerate_connections(report->connections, MAX_ENTRIES);

    printf("[REDTEAM-OMNI-C] ════════════════════════════════════════\n");
    printf("[REDTEAM-OMNI-C] Recon complete: %d creds, %d conns\n",
           report->credential_count, report->connection_count);
    printf("[REDTEAM-OMNI-C] ════════════════════════════════════════\n");
}

// int main(void) {
//     ReconReport report;
//     run_full_recon(&report);
//     return 0;
// }
