# CV Screening Agent - Frontend

React-based frontend for uploading PDF CVs and displaying AI-powered evaluation results.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Utility-first styling
- **TanStack Query** - Server state management
- **Axios** - HTTP client with upload progress
- **class-variance-authority** - Variant-based component styling

## Project Structure

```
src/
├── components/ui/       # Reusable UI components (Button, Badge, ProgressBar)
├── features/
│   ├── cv-upload/       # File upload feature (dropzone, progress, hooks)
│   └── scorecard/       # Results display feature (scorecard, score ring)
├── lib/                 # API client configuration
├── types/               # TypeScript interfaces
├── App.tsx              # Main application
└── main.tsx             # Entry point
```

## Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Features

- Drag & drop PDF upload
- Real-time upload progress indicator
- Multiple CV evaluation support
- Visual scorecard with pass/fail status
- Circular score ring visualization
- Detailed criteria breakdown

## API Integration

The frontend communicates with the backend via REST API using Axios.

### Configuration

API client is configured in `src/lib/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});
```

### Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cv/upload` | POST | Upload PDF and receive evaluation |
| `/api/cv/health` | GET | Check backend service status |

### Data Flow

1. **Upload** - User drops/selects a PDF file
2. **Request** - Axios sends `multipart/form-data` POST to `/api/cv/upload`
3. **Progress** - `onUploadProgress` callback updates UI with upload percentage
4. **Response** - Backend returns JSON with evaluation results
5. **Display** - TanStack Query mutation handles state, UI renders scorecard

### Response Type

```typescript
interface UploadResponse {
  success: boolean;
  message: string;
  evaluation: {
    status: 'pass' | 'fail';
    match_score: number;
    reasoning: string;
    criteria: Array<{
      name: string;
      passed: boolean;
      details: string;
    }>;
    candidate_name: string | null;
  } | null;
}
```

### Custom Hook

The `useUploadCV` hook (TanStack Query mutation) manages:
- Upload state (`isUploading`)
- Progress tracking (`progress`)
- Error handling (`error`)
- Success callbacks
