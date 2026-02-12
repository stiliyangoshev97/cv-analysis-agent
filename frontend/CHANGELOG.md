# Changelog

All notable changes to the CV Analysis Agent frontend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2025-02-12 🔐 AUTHENTICATION UI

### Added

**Auth Store (Zustand)**
- `useAuthStore` - Persistent auth state management
- Stores user, tokens, authentication status
- Persists to localStorage for session persistence
- Auto-rehydration on app load

**Auth API Integration**
- `register()` - Register new user
- `login()` - Login with email/password
- `refreshToken()` - Refresh access token
- `googleAuth()` - Google OAuth exchange
- `getMe()` - Get current user
- `logout()` - Server logout acknowledgement

**Auth Hooks**
- `useRegister()` - Registration mutation
- `useLogin()` - Login mutation
- `useLogout()` - Logout mutation
- `useGoogleAuth()` - Google OAuth mutation
- `useAuthState()` - Get auth state

**Auth Components**
- `LoginForm` - Email/password login form
- `RegisterForm` - User registration form with validation
- `AuthPage` - Combined auth page with form switching
- `UserMenu` - Dropdown menu with user info and logout
- `ProtectedRoute` - Route wrapper requiring authentication

**API Client Updates**
- Added auth token interceptor (auto-attach Bearer token)
- Added 401 response handler (auto-logout on expired token)

### Changed
- Wrapped main app in `ProtectedRoute`
- Added `UserMenu` to header for authenticated users

### Dependencies
- Added `zustand` for state management
- Added `react-router-dom` for routing
- Added `@react-oauth/google` for Google OAuth

---

## [0.1.0] - 2025-01-XX 🚀 MVP RELEASE

### Added

**File Upload Feature**
- `FileDropzone` component with drag-and-drop support
- Single file upload enforcement (explicit error for multiple files)
- PDF file type validation
- Visual feedback during drag hover state
- File icon display with selected filename

**Upload Progress**
- `UploadProgress` component showing real-time upload progress
- `useUploadCV` hook with TanStack Query mutation
- Axios-based upload with progress tracking

**Scorecard Display**
- `Scorecard` component for evaluation results
- `ScoreRing` circular score visualization with dynamic colors
- `CriteriaItem` component for individual criterion display
- Pass/Fail badge with appropriate coloring
- Score breakdown with met/unmet indicators

**Reusable UI Components**
- `Button` with CVA variants (primary, secondary, outline, ghost, danger)
- `Badge` with status variants (success, error, warning, info, neutral)
- `ProgressBar` for linear progress indication

**API Integration**
- Axios client with base URL configuration
- `uploadCV` function with progress callback support
- TypeScript interfaces matching backend schemas

**Project Configuration**
- Vite + React + TypeScript setup
- TailwindCSS with custom configuration
- TanStack Query for server state management
- Feature-based folder structure

### Changed

**Single CV Evaluation**
- Simplified from batch processing to single CV evaluation
- New upload replaces previous result (no accumulation)

### Fixed

**Multi-File Prevention**
- Added explicit error message when user attempts to upload multiple files
- Clear feedback: "Please upload only one PDF file at a time"

---

## [Unreleased]

### Planned - Phase 1: Authentication UI
- Login page with email/password
- Registration page
- Google OAuth button
- Auth context/store with Zustand
- Protected route wrapper
- JWT token management

### Planned - Phase 7: Frontend Enhancements
- Dashboard with CV history
- Candidate comparison view (Match-Up feature)
- Semantic search interface
- Notification preferences UI
- Chat interface for CV Q&A
- Batch upload with queue management
