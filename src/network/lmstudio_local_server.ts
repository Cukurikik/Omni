export function startServer(port: number): boolean {
    if (port < 1024) return false;
    return true;
}
