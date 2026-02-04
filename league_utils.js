const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Parses the lockfile content.
 * Format: process:PID:port:password:protocol
 * @param {string} content
 * @returns {object|null} { process, pid, port, password, protocol } or null if invalid
 */
function parseLockfile(content) {
    if (!content) return null;
    const parts = content.trim().split(':');
    if (parts.length < 5) return null;
    return {
        process: parts[0],
        pid: parseInt(parts[1], 10),
        port: parseInt(parts[2], 10),
        password: parts[3],
        protocol: parts[4]
    };
}

/**
 * Attempts to find the League of Legends lockfile in common locations.
 * @returns {string|null} Path to the lockfile or null if not found.
 */
function findLockfile() {
    const commonPaths = [
        'C:\\Riot Games\\League of Legends\\lockfile', // Standard Windows
        '/Applications/League of Legends.app/Contents/LoL/lockfile', // Standard Mac
        // Add more paths if needed
    ];

    // Check for custom install location via environment variable if we want to be fancy,
    // but for now stick to hardcoded + maybe a passed argument?
    // In a real app, we might search drives, but that's slow.

    for (const p of commonPaths) {
        try {
            if (fs.existsSync(p)) {
                return p;
            }
        } catch (e) {
            // Ignore permission errors etc.
        }
    }

    return null;
}

/**
 * Reads and parses the lockfile.
 * @param {string} [customPath] Optional path to check directly.
 * @returns {object|null}
 */
function getLockfileData(customPath) {
    const lockfilePath = customPath || findLockfile();
    if (!lockfilePath) return null;

    try {
        const content = fs.readFileSync(lockfilePath, 'utf8');
        const data = parseLockfile(content);
        if (data) {
            data.path = lockfilePath; // Include path in result
        }
        return data;
    } catch (e) {
        console.error('Error reading lockfile:', e);
        return null;
    }
}

module.exports = {
    findLockfile,
    parseLockfile,
    getLockfileData
};
