from setuptools import setup, find_packages

setup(
    name="hotel-booking-system",
    version="2.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.68.0",
        "uvicorn==0.15.0",
        "python-dotenv==0.19.0",
        "httpx==0.23.0",
        "pydantic==1.8.0",
        "Jinja2==3.0.1",
        "aiofiles==0.7.0",
        "python-multipart==0.0.5",
        "python-json-logger==2.0.2",
        "requests==2.26.0",
        "starlette==0.14.2",
        "typing-extensions==3.10.0.2",
        "slowapi==0.1.4",
        "email-validator==1.1.3",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4"
    ],
    python_requires=">=3.9.7",
) 