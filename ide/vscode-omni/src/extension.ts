import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('🚀 [OMNI-INTELLISENSE] Ekstensi VS Code Aktif.');

    // Hubungkan VS Code ke omnils daemon di TCP :4002
    const serverOptions: ServerOptions = () => {
        return new Promise((resolve) => {
            const net = require('net');
            const socket = net.connect({ port: 4002, host: '127.0.0.1' });
            resolve({
                reader: socket,
                writer: socket
            });
        });
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'omni' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.clientrc')
        }
    };

    client = new LanguageClient(
        'omniLanguageServer',
        'OMNI Universal AST Server',
        serverOptions,
        clientOptions
    );

    client.start();
    console.log('📡 [OMNI-INTELLISENSE] IPC Bridge ke OMNILS Engine tercipta!');
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
