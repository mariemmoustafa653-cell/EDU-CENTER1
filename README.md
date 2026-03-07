<<<<<<< HEAD
# Text Summarization Platform

Production-grade microservices system for extracting and summarizing text from PDF documents.

## Architecture

```
                        ┌─────────────┐
        Client ──────►  │    Nginx    │  (port 80 — production)
                        │   Reverse   │
                        │    Proxy    │
                        └──────┬──────┘
                               │
┌──────────────┐       HTTP    │        ┌──────────────┐
│              │  ◄────────────┘  ───►  │              │
│  API Gateway │   POST /api/v1/        │ NLP Service  │
│  (Express)   │   summarize            │  (FastAPI)   │
│  Port 3000   │  ◄──────────────────   │  Port 8000   │
│              │   JSON response        │              │
└──────┬───────┘                        └──────┬───────┘
       │                                       │
  PDF Upload                           Summarization
  Validation                           HuggingFace or
  Text Extraction                      OpenAI Provider
  Rate Limiting
  API Key Auth
```

### API Gateway (Node.js / Express)
- PDF upload via Multer (10 MB limit, PDF only)
- Page-range validation and text extraction
- Text cleaning and sanitization
- Request ID tracking, Winston logging
- Helmet + CORS security, configurable timeout
- Rate limiting (configurable window & max)
- API key authentication (`x-api-key` header)

### NLP Service (Python / FastAPI)
- Clean Architecture with dependency injection
- Swappable providers: HuggingFace (BART) / OpenAI (GPT-4o-mini)
- Token-based chunking for long documents
- Async processing, structured logging

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Development

```bash
docker compose up --build
```

> First startup downloads the BART model (~1.6 GB). Allow 2-3 minutes.

### Production (with Nginx)

```bash
# Set your API key and allowed origins
export API_KEY=your-secret-api-key
export ALLOWED_ORIGINS=https://your-frontend.com

# Start with production overlay
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Or use the deployment script:

```bash
# Development
bash deploy.sh dev

# Production
API_KEY=your-secret-key bash deploy.sh prod
```

### Verify

```bash
# Development
curl http://localhost:3000/health

# Production (through Nginx)
curl http://localhost:80/health
```

## API Reference

### Live Environment (Railway)

The core NLP Service has been deployed separately to a public live environment and is accessible directly at:
**`https://edu-center1-nlp-production.up.railway.app`**

### Interactive Docs

```
GET /api/v1/docs    → OpenAPI 3.0 JSON specification
```

### POST /api/v1/summarize

**Headers:**

| Header    | Required      | Description               |
|-----------|---------------|---------------------------|
| x-api-key | If configured | Your API key              |

**Request** (multipart/form-data):

| Field      | Type   | Required | Description          |
|------------|--------|----------|----------------------|
| file       | File   | Yes      | PDF file (max 10 MB) |
| start_page | number | Yes      | First page (1-based) |
| end_page   | number | Yes      | Last page (1-based)  |

**Example:**

```bash
curl -X POST http://localhost:3000/api/v1/summarize \
  -H "x-api-key: your-api-key" \
  -F "file=@document.pdf" \
  -F "start_page=1" \
  -F "end_page=3"
```

**Response:**

```json
{
  "status": "success",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "original_length": 4523,
  "summary_length": 312,
  "compression_ratio": 0.931,
  "summary_text": "The document discusses..."
}
```

If you wish to hit the deployed NLP Service directly (bypassing the API gateway and PDF extraction), you must send the text as a `multipart/form-data` file upload.

**Request (multipart/form-data):**

| Field      | Type   | Required | Description                     |
|------------|--------|----------|---------------------------------|
| file       | File   | Yes      | Text file to summarize          |
| request_id | string | No       | Optional tracing ID             |

**Example (Python):**

```python
import requests

url = "https://edu-center1-nlp-production.up.railway.app/api/v1/summarize"

# Send text as an in-memory file
files = {
    'file': ('document.txt', 'Artificial intelligence is a branch of computer science that deals with the simulation of intelligent behavior in computers. It includes machine learning, natural language processing, and robotics.', 'text/plain')
}

response = requests.post(url, files=files)
print(response.json())
```

### Error Responses

| Code | Meaning                     |
|------|----------------------------:|
| 400  | Invalid file / page range   |
| 401  | Missing API key             |
| 403  | Invalid API key             |
| 413  | Text too long               |
| 422  | No text in selected pages   |
| 429  | Rate limit exceeded         |
| 504  | Request timeout             |

## Configuration

### Environment Variables (API Gateway)

| Variable              | Default        | Description                        |
|-----------------------|----------------|------------------------------------|
| `PORT`                | `3000`         | Server port                        |
| `NLP_SERVICE_URL`     | `localhost:8000` | NLP service address              |
| `NODE_ENV`            | `development`  | Environment                        |
| `ALLOWED_ORIGINS`     | `*`            | CORS origins (comma-separated)     |
| `API_KEY`             | *(empty)*      | API key (empty = auth disabled)    |
| `RATE_LIMIT_WINDOW_MS`| `60000`       | Rate limit window (ms)             |
| `RATE_LIMIT_MAX`      | `30`           | Max requests per window            |
| `REQUEST_TIMEOUT_MS`  | `120000`       | Request timeout (ms)               |
| `MAX_FILE_SIZE_MB`    | `10`           | Max upload file size               |

### Switch Provider

Set the `SUMMARIZATION_PROVIDER` environment variable in `docker-compose.yml`:

```yaml
# HuggingFace (default, free, local)
SUMMARIZATION_PROVIDER=huggingface

# OpenAI (requires API key)
SUMMARIZATION_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

Restart after changing:

```bash
docker compose down && docker compose up --build
```

## Project Structure

```
summarization/
├── api-gateway/
│   ├── src/
│   │   ├── config/         env.js, multer.js
│   │   ├── controllers/    summarize.controller.js
│   │   ├── middleware/      error-handler, request-id, timeout, validator,
│   │   │                    rate-limiter, api-key-auth
│   │   ├── routes/          health, summarize, docs
│   │   ├── services/        nlp-client, pdf-extractor, text-cleaner
│   │   └── utils/           logger, file-cleanup
│   ├── server.js
│   └── Dockerfile
├── nlp-service/
│   ├── app/
│   │   ├── application/     interfaces, use_cases
│   │   ├── domain/          entities
│   │   ├── infrastructure/  providers (huggingface, openai, factory), text_processor
│   │   ├── presentation/    routes, health
│   │   └── utils/           logger, exceptions
│   ├── main.py
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── deploy.sh
└── README.md
# EDU-CENTER1
