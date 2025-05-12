# AI-BlueBirds Platform

AI-BlueBirds is a modern platform for creating, managing, and interacting with AI agents. The platform provides a user-friendly interface for generating various types of content using AI, including text, images, videos, and audio.

## Features

- Create and manage AI agents with specific capabilities
- Generate content using AI (text, images, videos, audio)
- Chat with AI agents
- Modern and responsive user interface
- Dark mode support
- Progress tracking for long-running tasks
- Cookie consent management

## Tech Stack

### Frontend
- Next.js 13+ (App Router)
- TypeScript
- Tailwind CSS
- React Hooks
- Modern ES6+ JavaScript

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT Authentication

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- PostgreSQL

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   yarn install
   ```

3. Start the development server:
   ```bash
   yarn dev
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

## Deployment

The platform is automatically deployed to production using GitHub Actions. The deployment pipeline:

1. Builds the frontend application
2. Deploys to the production server
3. Restarts necessary services

The deployment is triggered automatically when changes are pushed to the main branch.

## API Documentation

Once the backend server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Next.js](https://nextjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [PostgreSQL](https://www.postgresql.org/) 