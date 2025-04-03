# Hotel Booking System Configuration Guide

## Version Information
- Version: v3-0304250-1320
- Release Date: March 4, 2025
- Base Tag: v3-0304250-1320

## Configuration Files Overview

### 1. TypeScript Configuration (tsconfig.json)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "lib": ["ES2020", "DOM"],
    "baseUrl": ".",
    "paths": {
      "*": ["node_modules/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 2. Environment Variables (.env)
```env
# Development Environment
PORT=3000
NODE_ENV=development

# Production Environment (Render.com)
PORT=10000
NODE_ENV=production
```

### 3. Build Configuration (build.js)
```javascript
const fs = require('fs-extra');
const path = require('path');

async function build() {
    try {
        await fs.emptyDir('dist');
        await fs.copy('public', 'dist/public');
        if (!fs.existsSync('src')) {
            await fs.mkdir('src');
        }
        console.log('Build completed successfully!');
    } catch (err) {
        console.error('Build failed:', err);
        process.exit(1);
    }
}
```

### 4. Package Dependencies (package.json)
```json
{
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.0.3",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "@types/cors": "^2.8.13",
    "@types/express": "^4.17.17",
    "@types/node": "^18.15.11",
    "nodemon": "^2.0.22",
    "typescript": "^5.0.3"
  }
}
```

## Directory Structure
```
hotel-booking-system/
├── src/
│   └── server.ts
├── public/
│   ├── index.html
│   └── js/
│       └── main.js
├── docs/
│   ├── deployment/
│   ├── configuration/
│   └── scripts/
├── dist/
├── node_modules/
├── .env
├── .gitignore
├── package.json
├── tsconfig.json
├── build.js
└── render.yaml
```

## Configuration Parameters

### 1. Server Configuration
- Port: Configurable via PORT environment variable
- Environment: Set via NODE_ENV environment variable
- CORS: Enabled for all origins in development
- Static Files: Served from 'public' directory

### 2. Frontend Configuration
- Tailwind CSS: Loaded via CDN
- JavaScript: Modular structure in public/js
- Assets: Stored in public directory

### 3. Development Tools
- nodemon: Configured for TypeScript
- TypeScript: Strict mode enabled
- Build Process: Custom build script

## Security Configuration

### 1. CORS Settings
```typescript
app.use(cors());
```

### 2. Content Security Policy
Recommended headers for production:
```typescript
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; img-src 'self' https://images.unsplash.com"
  );
  next();
});
```

### 3. Security Headers
Recommended security headers:
```typescript
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  next();
});
```

## Development Configuration

### 1. VS Code Settings
Recommended .vscode/settings.json:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### 2. Git Configuration
Recommended .gitignore entries:
```gitignore
node_modules/
dist/
.env
*.log
```

## Deployment Configuration

### 1. Render.com Settings
See render.yaml for complete configuration

### 2. Build Process
1. TypeScript compilation
2. Static file copying
3. Environment variable injection

## Maintenance

### 1. Logging Configuration
- Development: Console logging
- Production: Error logging only

### 2. Performance Configuration
- Static file caching
- GZIP compression
- Rate limiting

## Troubleshooting

### 1. Build Issues
- Clear dist directory
- Remove node_modules and reinstall
- Check TypeScript version

### 2. Runtime Issues
- Verify environment variables
- Check port conflicts
- Review CORS settings

## Version Control

### 1. Git Configuration
```bash
git config core.autocrlf true  # Windows
git config core.autocrlf input # Mac/Linux
```

### 2. Branch Protection
- Require pull request reviews
- Enforce status checks
- Protect version tags 