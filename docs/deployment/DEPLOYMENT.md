# Hotel Booking System Deployment Guide

## Version Information
- Version: v3-0304250-1320
- Release Date: March 4, 2025
- Base Tag: v3-0304250-1320

## Prerequisites
- Node.js (v14.0.0 or higher)
- npm (v6.0.0 or higher)
- Git

## Environment Setup

### Local Development
1. Clone the repository:
```bash
git clone https://github.com/SankarNag23/hotel-booking-system.git
cd hotel-booking-system
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```env
PORT=3000
NODE_ENV=development
```

4. Start development server:
```bash
npm run dev
```

### Production Deployment (Render.com)

1. Prerequisites:
   - Render.com account
   - GitHub repository access

2. Deployment Steps:
   a. Log in to Render.com
   b. Click "New +" and select "Web Service"
   c. Connect your GitHub repository
   d. Configure the following settings:
      - Name: hotel-booking-system
      - Environment: Node
      - Build Command: `npm install && npm run build`
      - Start Command: `npm start`
      - Environment Variables:
        ```
        NODE_ENV=production
        PORT=10000
        ```

3. Click "Create Web Service"

## Configuration Files

### render.yaml
```yaml
services:
  - type: web
    name: hotel-booking-system
    runtime: node
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 10000
    staticPublishPath: ./public
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

### package.json Scripts
```json
{
  "scripts": {
    "start": "node dist/server.js",
    "dev": "nodemon src/server.ts",
    "build": "node build.js && tsc",
    "test": "jest"
  }
}
```

## Rollback Procedures

### To Rollback to This Version
```bash
git fetch origin
git checkout v3-0304250-1320
npm install
npm run build
npm start
```

### Emergency Rollback on Render.com
1. Go to your service on Render.com
2. Navigate to "Manual Deploy"
3. Select "Deploy existing commit"
4. Choose tag "v3-0304250-1320"
5. Click "Deploy"

## Health Checks

1. Frontend Health Check:
   - Access the application URL
   - Verify the hotel search form loads
   - Confirm featured hotels are displayed

2. Backend Health Check:
   - Test API endpoint: `/api/hotels`
   - Expected response: JSON array of hotels
   - HTTP Status: 200 OK

## Troubleshooting

### Common Issues

1. Build Failures:
   - Verify Node.js version compatibility
   - Check for missing dependencies
   - Review build logs for syntax errors

2. Runtime Errors:
   - Check environment variables
   - Verify port availability
   - Review application logs

3. Static File Issues:
   - Verify public directory structure
   - Check file permissions
   - Confirm static file middleware configuration

### Support Contacts

For deployment issues:
1. GitHub Repository: https://github.com/SankarNag23/hotel-booking-system
2. Create an issue ticket for technical support

## Monitoring

1. Application Metrics:
   - Server response time
   - Error rates
   - Request volume

2. System Metrics:
   - CPU usage
   - Memory utilization
   - Disk space

## Security Considerations

1. Environment Variables:
   - Never commit .env files
   - Use secure environment variable management
   - Rotate sensitive credentials regularly

2. Access Control:
   - Implement rate limiting
   - Use HTTPS only
   - Configure CORS appropriately

## License
MIT License - See LICENSE file for details 