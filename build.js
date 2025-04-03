const fs = require('fs-extra');
const path = require('path');

async function build() {
    try {
        // Clean dist directory
        await fs.emptyDir('dist');
        
        // Copy public files
        await fs.copy('public', 'dist/public');
        
        // Ensure src directory exists
        if (!fs.existsSync('src')) {
            await fs.mkdir('src');
        }
        
        console.log('Build completed successfully!');
    } catch (err) {
        console.error('Build failed:', err);
        process.exit(1);
    }
}

build(); 