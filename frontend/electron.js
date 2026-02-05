const { app, BrowserWindow, Tray, Menu, globalShortcut } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;
let tray;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        icon: path.join(__dirname, 'public/logo192.png'),
        title: "Mind-Q Agent"
    });

    const startUrl = isDev
        ? 'http://localhost:5173'
        : `file://${path.join(__dirname, '../dist/index.html')}`;

    mainWindow.loadURL(startUrl);

    mainWindow.on('closed', () => (mainWindow = null));

    // Minimize to tray logic
    mainWindow.on('minimize', function (event) {
        event.preventDefault();
        mainWindow.hide();
    });

    mainWindow.on('close', function (event) {
        if (!app.isQuiting) {
            event.preventDefault();
            mainWindow.hide();
        }
        return false;
    });
}

function createTray() {
    const iconPath = path.join(__dirname, 'public/favicon.ico'); // Ensure this exists
    tray = new Tray(iconPath);
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show App', click: function () {
                mainWindow.show();
            }
        },
        {
            label: 'Quit', click: function () {
                app.isQuiting = true;
                app.quit();
            }
        }
    ]);
    tray.setToolTip('Mind-Q Agent');
    tray.setContextMenu(contextMenu);
}

app.on('ready', () => {
    createWindow();
    // createTray(); // Commented until icon exists

    // Global Shortcut: CommandOrControl+Shift+M to toggle window
    globalShortcut.register('CommandOrControl+Shift+M', () => {
        if (mainWindow.isVisible()) {
            mainWindow.hide();
        } else {
            mainWindow.show();
            mainWindow.focus();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});
