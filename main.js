const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { getLockfileData } = require('./league_utils');
// We will need https to make requests later, handling self-signed certs
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

let mainWindow;
let connectionInterval;
let lastStatus = null;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 400,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    mainWindow.loadFile('index.html');

    // Open DevTools for debugging
    // mainWindow.webContents.openDevTools();

    startConnectionCheck();
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
    clearInterval(connectionInterval);
});

function startConnectionCheck() {
    // Ensure we don't have multiple intervals
    if (connectionInterval) clearInterval(connectionInterval);

    // Check immediately then every 2 seconds
    checkConnection();
    connectionInterval = setInterval(checkConnection, 2000);
}

function checkConnection() {
    if (!mainWindow || mainWindow.isDestroyed()) return;

    const lockfileData = getLockfileData();
    let status = 'Waiting for Client';
    let data = null;

    if (lockfileData) {
        status = 'Connected';
        data = {
            port: lockfileData.port,
            protocol: lockfileData.protocol,
            pid: lockfileData.pid
        };
    }

    // Only send update if status changed to avoid spamming (though UI might want fresh data?)
    // For now, simple state check
    // Actually, sending it every time ensures UI is in sync if it reloads
    mainWindow.webContents.send('status-update', { status, data });
}
