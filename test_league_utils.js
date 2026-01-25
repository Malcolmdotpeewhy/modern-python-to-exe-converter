const fs = require('fs');
const assert = require('assert');
const { parseLockfile, getLockfileData } = require('./league_utils');

console.log('Running tests for league_utils.js...');

// Test 1: parseLockfile
console.log('Test 1: parseLockfile');
const validContent = 'LeagueClient:1234:5678:password:https';
const parsed = parseLockfile(validContent);
assert.deepStrictEqual(parsed, {
    process: 'LeagueClient',
    pid: 1234,
    port: 5678,
    password: 'password',
    protocol: 'https'
}, 'Failed to parse valid lockfile content');
console.log('PASSED: parseLockfile valid');

const invalidContent = 'LeagueClient:1234';
const parsedInvalid = parseLockfile(invalidContent);
assert.strictEqual(parsedInvalid, null, 'Should return null for invalid content');
console.log('PASSED: parseLockfile invalid');

// Test 2: getLockfileData with custom path
console.log('Test 2: getLockfileData with custom path');
const tempPath = 'temp_lockfile';
fs.writeFileSync(tempPath, validContent);

try {
    const data = getLockfileData(tempPath);
    assert.ok(data, 'Should return data');
    assert.strictEqual(data.pid, 1234);
    assert.strictEqual(data.path, tempPath);
    console.log('PASSED: getLockfileData with valid file');
} catch (e) {
    console.error('FAILED: getLockfileData', e);
    process.exit(1);
} finally {
    if (fs.existsSync(tempPath)) {
        fs.unlinkSync(tempPath);
    }
}

// Test 3: getLockfileData with non-existent file
console.log('Test 3: getLockfileData with non-existent file');
const missingData = getLockfileData('non_existent_file');
assert.strictEqual(missingData, null, 'Should return null for missing file');
console.log('PASSED: getLockfileData missing file');

console.log('All tests passed!');
