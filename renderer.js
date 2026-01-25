const statusElement = document.getElementById('status');

if (window.electronAPI) {
    window.electronAPI.onStatusUpdate((message) => {
        const { status, data } = message;
        statusElement.innerText = `Status: ${status}`;

        if (status === 'Connected') {
            statusElement.classList.add('connected');
            statusElement.classList.remove('disconnected');
            // Optional: Show more info
            // console.log('Connected to LCU on port', data.port);
        } else {
            statusElement.classList.add('disconnected');
            statusElement.classList.remove('connected');
        }
    });
} else {
    console.error('Electron API not available');
}
