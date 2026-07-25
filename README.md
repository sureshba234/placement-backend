# Campus Placement Command Center

> A production-grade, multi-tenant placement management platform with AI-powered resume parsing, semantic job-matching, real-time notifications, and role-based dashboards — built to replace the WhatsApp groups and Excel sheets that run most Indian college placement cells.

[![Django](https://img.shields.io/badge/Django-6.0.7-green)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-teal)](https://fastapi.tiangolo.com)
[![Celery](https://img.shields.io/badge/Celery-5.6-orange)](https://docs.celeryq.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-red)](https://redis.io)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama3-purple)](https://groq.com)

**Live Demo:** https://placement-frontend-weld.vercel.app  
**Backend API:** https://placement-backend-vput.onrender.com  
**Admin Panel:** https://placement-backend-vput.onrender.com/admin/

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Why This Project](#3-why-this-project)
4. [Architecture Overview](#4-architecture-overview)
5. [Technology Stack](#5-technology-stack)
6. [Key Features](#6-key-features)
7. [User Roles](#7-user-roles)
8. [System Design](#8-system-design)
9. [Backend — Django REST Framework](#9-backend--django-rest-framework)
10. [Database Models](#10-database-models)
11. [Eligibility Rule Engine](#11-eligibility-rule-engine)
12. [Resume Parsing Pipeline](#12-resume-parsing-pipeline)
13. [AI Matching Service](#13-ai-matching-service)
14. [Async Task Pipeline (Celery)](#14-async-task-pipeline-celery)
15. [Redis Caching Layer](#15-redis-caching-layer)
16. [Email Notification System](#16-email-notification-system)
17. [Recruiter Approval Workflow](#17-recruiter-approval-workflow)
18. [Frontend — React](#18-frontend--react)
19. [Student Dashboard](#19-student-dashboard)
20. [TPO Dashboard](#20-tpo-dashboard)
21. [Recruiter Portal](#21-recruiter-portal)
22. [Analytics Dashboard](#22-analytics-dashboard)
23. [Authentication & Security](#23-authentication--security)
24. [API Reference](#24-api-reference)
25. [Project Structure](#25-project-structure)
26. [Local Development Setup](#26-local-development-setup)
27. [Environment Variables](#27-environment-variables)
28. [Deployment Guide](#28-deployment-guide)
29. [Architectural Decisions](#29-architectural-decisions)
30. [Future Improvements](#30-future-improvements)

---

## 1. Project Overview

The **Campus Placement Command Center** is a full-stack web application that digitizes and automates the entire campus placement lifecycle — from drive creation and eligibility filtering to resume parsing, AI-powered job matching, and real-time student notifications.

The platform serves three distinct user roles:

- **Students** — view eligible drives, upload resumes, apply, and track match scores
- **TPO Admins** — create drives with complex eligibility rules, manage applicants, approve recruiter submissions, and view placement analytics
- **Recruiters** — post job descriptions, view shortlisted candidates, and track match scores

Every component is built production-shaped: JWT authentication, role-based permissions, async background processing, Redis caching, real email notifications, and full deployment on Render + Vercel.

---

## 2. Problem Statement

Every placement season at Indian colleges runs on chaos:

- TPOs blast drive announcements over WhatsApp groups to 200+ students
- Students don't know their eligibility (CGPA cutoffs, backlog rules, branch restrictions) until after applying
- Resumes arrive as random PDFs with no structure or standardization
- TPOs manually cross-check eligibility in Excel spreadsheets
- There is no centralized way to track application statuses, shortlists, or placement rates by branch

This project automates all of it — and adds AI-powered features (resume parsing and job-match scoring) that simply weren't possible with a WhatsApp + Excel workflow.

---

## 3. Why This Project

90% of fresher portfolio projects are single-user apps (todo lists, blogs, e-commerce clones) with one role and no real complexity. This project was deliberately designed to require justifying:

**Multi-tenant, multi-role auth** — three distinct permission layers (TPO, Student, Recruiter) enforced at both the DRF permission class level and React route guard level.

**A real rule engine** — eligibility filtering isn't `is_admin=True`. It's a configurable set of rules per drive (CGPA floor, backlog ceiling, allowed branches, graduation year range) evaluated against each student's stored profile in Python, not in raw SQL.

**Async/background processing** — resume parsing and job-match scoring are naturally async. Uploading a resume triggers a Celery task that calls the Groq LLM API and stores structured data back. Applying to a drive triggers a separate Celery task that computes and stores a match score. Neither blocks the user's request.

**A domain interviewers instantly understand** — every interviewer was once a placement candidate. The conversation flows naturally.

---

## 4. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     React SPA (Vercel)                       │
│         JWT auth │ Role-based routing │ React Query          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS (JWT Bearer token)
┌──────────────────────────▼──────────────────────────────────┐
│              Django REST Framework (Render)                   │
│   Auth │ Drives │ Applications │ Resumes │ Analytics         │
└──────┬────────────────────────────────────┬─────────────────┘
       │                                    │
       ▼                                    ▼
┌─────────────┐                   ┌──────────────────────┐
│  PostgreSQL │                   │  Redis               │
│  (Render)   │                   │  Cache + Celery      │
└─────────────┘                   │  Broker (Render)     │
                                  └──────────┬───────────┘
                                             │
                                  ┌──────────▼───────────┐
                                  │  Celery Workers       │
                                  │  - Resume parsing     │
                                  │  - Job matching       │
                                  │  - Email notify       │
                                  └──────────┬───────────┘
                                             │
                                  ┌──────────▼───────────┐
                                  │  Groq LLM API         │
                                  │  (llama-3.1-8b)       │
                                  └──────────────────────┘
```

---

## 5. Technology Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend API | Django 6.0 + DRF | Batteries-included ORM, admin, auth — saves weeks vs Flask |
| Background jobs | Celery 5.6 | Industry-standard async task queue |
| Message broker | Redis 7 | Also used as cache backend — one service, two purposes |
| Database | PostgreSQL 16 | Production-grade RDBMS; JSON columns for resume data |
| LLM integration | Groq (Llama 3.1 8B) | Free tier, 500 req/min, fast inference for parsing + matching |
| Frontend | React 18 + Vite | Modern SPA; Vite for fast dev builds |
| Server state | React Query (@tanstack) | Smart caching, polling, invalidation — no boilerplate |
| UI state | Zustand | Minimal auth store; avoiding Redux for project this size |
| Charts | Recharts | Composable chart library, no config overhead |
| Routing | React Router v6 | Nested routes, route guards |
| HTTP client | Axios | Interceptors for JWT auto-refresh |
| Deployment (backend) | Render | Free PostgreSQL + Redis + web service |
| Deployment (frontend) | Vercel | Zero-config Vite deployment |
| Email | Gmail SMTP | Free, zero configuration |

---

## 6. Key Features

### Core MVP
- **Multi-role JWT auth** — student, tpo_admin, recruiter with permission classes enforced server-side
- **Drive creation with eligibility rule builder** — CGPA floor, backlog ceiling, allowed branches, graduation year range
- **Student eligibility feed** — each student sees only the drives they actually qualify for, computed by the rule engine, cached per-student in Redis
- **Resume upload + AI parsing** — PDF/DOCX resumes are parsed by Groq LLM into structured JSON (name, skills, education, projects)
- **AI job-match scoring** — Groq LLM computes a semantic match score (0–100) and a missing-skills gap list between each application's resume and the drive's job description
- **Application management** — students apply, TPOs manage status (applied → shortlisted → selected/rejected), CSV export
- **Real email notifications** — Gmail SMTP, triggered when a drive opens, notifying all eligible students
- **Recruiter → TPO approval workflow** — recruiter-posted drives sit in `pending_approval` state until a TPO explicitly approves them

### Analytics & Extras
- **Placement rate by branch** — bar chart showing selected/total per branch, TPO-only
- **Drive-wise applicant stats** — total and selected count per drive in a table
- **Per-drive applicant breakdown** — color-coded bar chart (applied/shortlisted/rejected/selected)
- **Student score history** — line chart showing match score trend across applications over time
- **Student profile completion** — students can update CGPA, branch, backlog count, graduation year from the dashboard
- **Self-registration** — students and recruiters can sign up; TPO admin accounts created by existing admins

---

## 7. User Roles

### Student
- Registers via `/register` (role: student)
- Completes profile (branch, CGPA, backlogs, graduation year) — required for eligibility engine
- Uploads PDF/DOCX resume — triggers async LLM parsing
- Views only eligible drives (filtered by rule engine)
- Applies to drives with a selected resume — triggers async match scoring
- Views application history with match scores and missing skills
- Sees score trend chart over time

### TPO Admin
- Created by existing admin via Django admin panel
- Creates drives with nested eligibility rules in a single form
- Views all drives regardless of eligibility
- Manages applicant lists with inline status updates and CSV export
- Views pending recruiter-submitted drives and approves them
- Accesses placement analytics dashboard (by branch, by drive)

### Recruiter
- Self-registers via `/register` (role: recruiter)
- Posts job descriptions — drive goes to `pending_approval` automatically
- Views only their own drives
- Views shortlisted candidates with match scores (not the full raw applicant pool)

---

## 8. System Design

### Eligibility Rule Engine

Eligibility rules are stored per-drive as a separate `EligibilityRule` model rather than inline fields on `Drive`. This allows one drive to have multiple rules (e.g. different CGPA cutoffs per branch in future extensions).

The check is a Python method (`is_student_eligible`) on the model itself — not a raw SQL filter — because rule logic (JSON branch lists, multi-field conditionals) doesn't map cleanly to ORM filters and is more readable, testable, and extensible as Python.

```python
def is_student_eligible(self, student):
    if self.min_cgpa and (not student.cgpa or student.cgpa < self.min_cgpa):
        return False
    if self.max_backlogs is not None and student.backlog_count > self.max_backlogs:
        return False
    if self.allowed_branches and student.branch not in self.allowed_branches:
        return False
    if self.min_graduation_year and student.graduation_year < self.min_graduation_year:
        return False
    if self.max_graduation_year and student.graduation_year > self.max_graduation_year:
        return False
    return True
```

The `EligibleDrivesView` fetches all open, non-expired drives, runs each through the rule engine in Python, and returns only the matching IDs.

### Async Task Pipeline

Three distinct async workflows:

1. **Resume parsing** — triggered on upload, calls Groq LLM to extract structured data from raw PDF/DOCX text
2. **Match scoring** — triggered on application, calls Groq LLM to compute semantic similarity between resume and job description
3. **Email notifications** — triggered on drive open/approval, loops through eligible students and sends real SMTP emails

All three are Celery shared tasks with retry logic (max 3 retries, exponential backoff).

### Caching Strategy

Redis caches two things with different TTLs:

- **Eligible drives per student** — 5 minute TTL, keyed as `placement:1:eligible_drives:v{version}:student:{id}`. Cache is invalidated via a version bump (Django signal on Drive/EligibilityRule save) rather than per-key deletion — old versioned keys expire naturally.
- **Drive analytics** — 2 minute TTL, per-drive status breakdown. Allows dashboard polling without hitting the database on every request.

---

## 9. Backend — Django REST Framework

### App Structure

```
backend/
├── config/               # Django project settings, URLs, Celery config
├── accounts/             # Custom User model, JWT auth, registration, profile
├── colleges/             # College model (referenced by User)
├── drives/               # Drive, EligibilityRule models, views, signals, tasks
├── applications/         # Application model, apply/manage views, analytics
└── resumes/              # Resume model, file upload, LLM parsing pipeline
```

### Key Design Decisions

**Custom User model** — `AbstractUser` extended with a `role` field (`TextChoices`: student/tpo_admin/recruiter) plus student-specific fields (CGPA, branch, backlog count, graduation year) and recruiter-specific field (company name). Using `AbstractUser` rather than `AbstractBaseUser` keeps Django's built-in auth machinery intact.

**DRF permission classes** — three custom permission classes (`IsStudent`, `IsTPOAdmin`, `IsRecruiter`) in `accounts/permissions.py`, imported by all other apps. Every view declares exactly which role(s) can access it.

**JWT via SimpleJWT** — access tokens (5 min expiry) + refresh tokens (1 day). Frontend Axios interceptor automatically calls `/api/auth/token/refresh/` on 401, retries original request, and logs out on second failure.

**`unique_together` constraint** — `Application` has `unique_together = ('student', 'drive')` so a student can't apply twice. Returns a 409-equivalent IntegrityError caught as a 400 DRF validation error.

---

## 10. Database Models

### User (accounts)
| Field | Type | Notes |
|-------|------|-------|
| username | CharField | Unique, inherited from AbstractUser |
| role | CharField | TextChoices: student/tpo_admin/recruiter |
| branch | CharField | e.g. CSE, ECE, AIML |
| cgpa | DecimalField | 4 digits, 2 decimal places |
| backlog_count | PositiveIntegerField | Default 0 |
| graduation_year | PositiveIntegerField | Used by eligibility engine |
| college | ForeignKey → College | Nullable |
| company_name | CharField | Recruiter-specific |

### Drive (drives)
| Field | Type | Notes |
|-------|------|-------|
| title | CharField | e.g. "TCS Ninja 2026" |
| company_name | CharField | |
| job_description | TextField | Full JD text, used for AI matching |
| status | CharField | draft/pending_approval/open/closed |
| application_deadline | DateTimeField | Drives past deadline excluded from eligible feed |
| created_by | ForeignKey → User | TPO who created it |
| recruiter | ForeignKey → User | Recruiter who submitted it (nullable) |

### EligibilityRule (drives)
| Field | Type | Notes |
|-------|------|-------|
| drive | ForeignKey → Drive | Cascade delete |
| min_cgpa | DecimalField | Nullable = no floor |
| max_backlogs | PositiveIntegerField | Nullable = no limit |
| allowed_branches | JSONField | Empty list = all branches |
| min_graduation_year | PositiveIntegerField | Nullable |
| max_graduation_year | PositiveIntegerField | Nullable |

### Resume (resumes)
| Field | Type | Notes |
|-------|------|-------|
| student | ForeignKey → User | |
| file | FileField | Stored in `media/resumes/YYYY/MM/` |
| parsed_data | JSONField | Structured data from LLM (skills, education, projects) |
| is_parsed | BooleanField | Flipped to True after task completes |

### Application (applications)
| Field | Type | Notes |
|-------|------|-------|
| student | ForeignKey → User | |
| drive | ForeignKey → Drive | |
| resume | ForeignKey → Resume | The specific resume used |
| status | CharField | applied/shortlisted/rejected/selected |
| match_score | FloatField | 0–100, written by Celery task |
| missing_skills | JSONField | List of skills in JD but absent from resume |

---

## 11. Eligibility Rule Engine

The rule engine is the core differentiator of this project from a standard CRUD app.

### How it works

1. `EligibleDrivesView.get_queryset()` fetches all `Drive` objects with `status='open'` and `application_deadline >= now`, prefetching related `eligibility_rules`.

2. For each drive, it calls `rule.is_student_eligible(student)` for every attached rule. A drive is eligible only if **all** rules pass (AND logic).

3. If a drive has **no rules**, it's eligible for everyone (open drive).

4. The result is a list of eligible drive IDs, cached in Redis under a versioned key for 5 minutes.

### Cache invalidation

A Django signal on `Drive.post_save` and `EligibilityRule.post_save/post_delete` calls `cache.incr('drives_cache_version')`. The eligible drives cache key includes this version number, so after any drive or rule change, the next request automatically computes fresh results rather than serving stale cached data.

### Double-validation on apply

The eligibility check runs **twice** — once when filtering the student's feed (what they see) and again at write time in `ApplicationCreateSerializer.validate()`. This prevents a student from bypassing the eligibility filter by sending a direct POST to the apply endpoint.

---

## 12. Resume Parsing Pipeline

### Flow

```
Student uploads PDF/DOCX
        ↓
ResumeUploadView.perform_create()
        ↓
Resume object saved to DB (is_parsed=False)
        ↓
parse_resume_task.delay(resume.id)  ← Celery task dispatched
        ↓
[Background] text_extraction.extract_text_from_resume()
        ↓
[Background] llm_parser.parse_resume_text(raw_text)
        ↓
Groq API call → structured JSON
        ↓
resume.parsed_data = result
resume.is_parsed = True
resume.save()
```

### Text Extraction

`pypdf` for PDF, `python-docx` for DOCX. Raw text is extracted page by page (PDF) or paragraph by paragraph (DOCX), joined with newlines.

### LLM Parsing Prompt

The extracted text (capped at 6000 characters) is sent to `llama-3.1-8b-instant` on Groq with a structured prompt requesting **only valid JSON** — no preamble, no markdown fences. The response is defensively cleaned (stripping triple-backtick fences if present) before `json.loads()`.

### Output Schema

```json
{
  "name": "Bathina Suresh",
  "email": "suresh@example.com",
  "phone": "9876543210",
  "skills": ["Python", "Django", "React", "PostgreSQL", "Docker"],
  "education": [{"degree": "B.Tech", "institution": "Saveetha Engineering", "year": "2025"}],
  "projects": [{"title": "Job Portal", "description": "...", "tech_stack": ["Django", "React"]}],
  "experience_years": 0
}
```

### Frontend polling

`ResumeUploader` uses React Query's `refetchInterval` — it polls `/api/resumes/mine/` every 3 seconds while any resume has `is_parsed: false`, automatically stopping once all resumes are parsed. The UI flips from "⏳ Parsing..." to "✅ Parsed" without any manual refresh.

---

## 13. AI Matching Service

### Approach

When a student applies to a drive, a Celery task calls Groq LLM with both the student's parsed resume data (flattened to text: skills, education, projects) and the drive's full job description. The LLM returns a match score (0–100) and a list of missing skills.

### Why LLM over embeddings

The original design used `sentence-transformers` (BERT-based embeddings + cosine similarity). This was refactored to use Groq LLM for two reasons:

1. **Deployment constraint** — `sentence-transformers` pulls in PyTorch (~500MB), which exceeds Render's free-tier 512MB RAM limit. The service crashed on startup before serving a single request.

2. **Quality improvement** — LLM semantic matching understands context ("experience with distributed systems" matches "system design" on a resume). Pure vector similarity would have missed this.

### Matching Prompt

```
Given a resume and a job description, return ONLY valid JSON:
{
  "match_score": number between 0 and 100,
  "missing_skills": [list of skills in the JD but missing from the resume]
}
```

Temperature is set to 0.1 for deterministic, consistent scoring.

### Score interpretation

| Score | Meaning |
|-------|---------|
| 80–100 | Strong match — most JD requirements covered |
| 60–79 | Good match — core skills present, some gaps |
| 40–59 | Partial match — relevant background, significant gaps |
| 0–39 | Weak match — different technology stack |

---

## 14. Async Task Pipeline (Celery)

### Configuration

```python
CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = config('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

Redis serves as both the message broker and the result backend — one infrastructure component instead of two.

### Task registry (four tasks)

| Task | Trigger | Retries |
|------|---------|---------|
| `resumes.tasks.parse_resume_task` | Resume upload | 2, 10s/20s backoff |
| `applications.tasks.trigger_match_scoring` | Application submitted | 3, 10s/20s/30s backoff |
| `drives.tasks.notify_eligible_students` | Drive opened/approved | 0 (fire and forget) |
| `config.celery.debug_task` | Manual testing | 0 |

### Retry strategy

Tasks use `bind=True` and `self.retry(exc=exc, countdown=10 * (self.request.retries + 1))` — exponential-ish backoff. After `max_retries` exhausted, the exception propagates and the task enters FAILURE state in Redis. `is_parsed` and `match_score` stay at their default values (False/null), allowing the frontend to detect and surface a "failed" state.

### Production mode (no worker)

In production (Render free tier, which doesn't offer free background workers), tasks are called **synchronously** via a `USE_CELERY` environment variable:

```python
if settings.USE_CELERY:
    parse_resume_task.delay(resume.id)
else:
    parse_resume_task(resume.id)  # synchronous call
```

This keeps the architecture async-capable for production scale while working within free-tier constraints for the demo deployment.

---

## 15. Redis Caching Layer

### Setup

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'KEY_PREFIX': 'placement',
    }
}
```

### Two cached endpoints

**Eligible drives feed** (5 min TTL)
```
Key: placement:1:eligible_drives:v{version}:student:{student_id}
Value: list of eligible drive IDs
```

**Drive analytics** (2 min TTL)
```
Key: placement:1:drive_analytics:{drive_id}
Value: {applied: N, shortlisted: N, selected: N, rejected: N, total: N}
```

### Version-based invalidation

Rather than tracking which student keys to delete when a drive changes:

1. A `post_save`/`post_delete` Django signal on `Drive` and `EligibilityRule` calls `cache.incr('drives_cache_version')`
2. The cache key includes `v{version}` — after a bump, all old keys become unreachable (they'll expire naturally within 5 minutes)
3. The first request after a drive change computes fresh results and stores under the new version key

This avoids the need to maintain a registry of all active student cache keys.

---

## 16. Email Notification System

### Flow

When a drive opens (either TPO creates with status `open`, or TPO approves a recruiter submission), `notify_eligible_students.delay(drive.id)` is dispatched.

The task:
1. Fetches all users with `role='student'`
2. Runs each through `EligibilityRule.is_student_eligible()` — same logic as the feed
3. Calls `send_notification(student, drive)` for each eligible student

### Email content

```
Subject: New Placement Drive: {drive.title} at {drive.company_name}

Hi {student.first_name or username},

A new drive you're eligible for has just opened:

Position: {drive.title}
Company: {drive.company_name}
Deadline: {drive.application_deadline}

Log in to the Placement Command Center to apply.

— Placement Cell
```

### SMTP configuration

Gmail SMTP on port 587 with TLS. Uses a Gmail App Password (not the account password — Google requires App Passwords for programmatic SMTP access).

### Error handling

Each `send_mail()` call is wrapped in `try/except` so a single student's invalid email address doesn't crash the entire batch notification task for everyone else.

---

## 17. Recruiter Approval Workflow

### Problem solved

Without an approval step, a recruiter could post any content as a drive and it would immediately be visible to all eligible students, trigger notification emails, and appear in their feed. The approval gate lets TPOs review recruiter submissions before they go live.

### Status flow

```
Recruiter posts JD
        ↓
Drive created with status='pending_approval'
(NOT visible to students, NOT in eligible feed, NO notifications sent)
        ↓
TPO reviews in "Pending Submissions" panel
        ↓
TPO clicks "Approve & Open"
        ↓
Drive status → 'open'
notify_eligible_students task fired
Drive appears in student eligible feeds
```

### Implementation

`RecruiterDriveCreateView.perform_create()` overrides the status field regardless of what the client sends:

```python
serializer.save(
    recruiter=self.request.user,
    created_by=self.request.user,
    status=Drive.Status.PENDING_APPROVAL,
)
```

`ApproveDriveView` is a TPO-only POST endpoint that validates the drive is in `pending_approval` state, flips it to `open`, and fires the notification task.

---

## 18. Frontend — React

### Structure

```
frontend/src/
├── api/              # All API calls — auth, drives, applications, resumes, analytics
├── components/       # Shared UI components
│   ├── ApplicantList.jsx
│   ├── CreateDriveForm.jsx
│   ├── DriveAnalyticsChart.jsx
│   ├── DriveCard.jsx
│   ├── OverallAnalyticsPanel.jsx
│   ├── PendingDrivesPanel.jsx
│   ├── ProfileForm.jsx
│   ├── ResumeUploader.jsx
│   └── ScoreHistoryChart.jsx
├── pages/
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── student/StudentDashboard.jsx
│   ├── tpo/TPODashboard.jsx
│   └── recruiter/RecruiterDashboard.jsx
├── routes/
│   └── ProtectedRoute.jsx   # Role-based route guard
├── store/
│   └── authStore.js         # Zustand auth state
└── App.jsx                  # React Router setup
```

### State management split

| State type | Library | Why |
|-----------|---------|-----|
| Server state (drives, applications, resumes) | React Query | Automatic caching, background refetch, polling |
| Auth state (tokens, user profile) | Zustand | Simple, synchronous, persisted to localStorage |

Redux was deliberately avoided — for a project this size it would be over-engineering. React Query handles the majority of state that typically ends up in Redux (async server data).

### Role-based routing

```javascript
function ProtectedRoute({ children, allowedRoles }) {
  const user = useAuthStore((state) => state.user);
  const accessToken = useAuthStore((state) => state.accessToken);

  if (!accessToken || !user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role))
    return <Navigate to={`/${user.role}`} replace />;

  return children;
}
```

Role value and URL segment are identical strings (`student`, `tpo_admin`, `recruiter`), so the redirect `/${user.role}` works without a lookup table.

### JWT auto-refresh

Axios response interceptor catches 401 errors, attempts a token refresh, retries the original request with the new token, and logs out the user if refresh fails:

```javascript
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const { access } = await refreshAccessToken(refreshToken);
      // retry...
    }
  }
);
```

---

## 19. Student Dashboard

### Features

- **Resume uploader** with real-time parsing status (polls every 3s until parsed)
- **Eligible drives feed** — only shows drives the student qualifies for
- **Apply button** — disabled after applying, shows "Applied ✓" state
- **My Applications list** — status badges, match scores, missing skills
- **Score history chart** — line chart of match score trend across all applications
- **Edit Profile** — collapsible form for CGPA, branch, backlogs, graduation year

### Polling strategy

React Query's `refetchInterval` is used for two polling scenarios:

1. Resumes: polls every 3s while any resume has `is_parsed: false`
2. Applications: polls every 4s while any application has `match_score: null`

Polling stops automatically once all items reach their final state — no manual cleanup needed.

---

## 20. TPO Dashboard

### Features

- **Drive creation form** with nested eligibility rule builder (one form, one request)
- **Pending recruiter submissions** panel — highlighted in amber, approve with one click
- **All drives list** — click any drive to load its applicant table
- **Applicant table** — name, email, branch, CGPA, match score %, inline status dropdown
- **CSV export** — downloads all applicants for a drive as a spreadsheet
- **Per-drive analytics chart** — color-coded bar chart (applied/shortlisted/selected/rejected)
- **Placement rate by branch** — bar chart showing % placed per branch
- **Drive-wise stats table** — total applicants and selected count per drive

### Nested rule creation

The eligibility rule builder is a separate form section within `CreateDriveForm.jsx`. On submit, eligibility rules are packaged into the same JSON body as the drive:

```json
{
  "title": "Python Developer",
  "company_name": "TCS",
  "status": "open",
  "application_deadline": "2026-08-01T18:00:00Z",
  "eligibility_rules": [{
    "min_cgpa": 7.0,
    "max_backlogs": 2,
    "allowed_branches": ["CSE", "ECE"],
    "min_graduation_year": 2024,
    "max_graduation_year": 2026
  }]
}
```

`DriveSerializer.create()` pops the nested `eligibility_rules` data, creates the Drive, then creates each EligibilityRule with a FK to the new Drive — all in one transaction.

---

## 21. Recruiter Portal

### Features

- **Post JD form** — title, company, job description, deadline
- **My Posted Drives** — list of drives submitted by this recruiter, with status indicators
- **Shortlisted Candidates** — visible only for approved drives, shows only `shortlisted` and `selected` applications (not the raw full applicant pool, which is TPO-only)

### Design constraint

Recruiters see a curated view of candidates rather than the full applicant list. This was a deliberate design decision:

- Full applicant management is the TPO's responsibility (they know the students)
- Recruiters care about final shortlists, not intermediate screening
- It also prevents recruiters from seeing students' personal contact information en masse

---

## 22. Analytics Dashboard

### Branch placement rate

```sql
SELECT student__branch, COUNT(*) as total,
       COUNT(*) FILTER (WHERE status='selected') as selected
FROM applications_application
JOIN accounts_user ON student_id = accounts_user.id
GROUP BY student__branch
```

Rendered as a blue bar chart with percentage labels.

### Drive-wise stats

```sql
SELECT drive__title, drive__company_name,
       COUNT(*) as total,
       COUNT(*) FILTER (WHERE status='selected') as selected
FROM applications_application
GROUP BY drive_id, drive__title, drive__company_name
ORDER BY total DESC
```

Rendered as a sortable table.

Both are cached for 2 minutes in Redis and refetch every 30 seconds on the client, so the dashboard stays reasonably fresh without hammering the database.

---

## 23. Authentication & Security

### JWT Configuration

- **Access token lifetime**: 5 minutes
- **Refresh token lifetime**: 1 day
- **Algorithm**: HS256
- **Auto-refresh**: Axios interceptor handles silently; user never sees a session expiry

### Permission enforcement

Every API endpoint enforces permissions at two levels:

1. **DRF permission class** — server-side, non-negotiable
2. **React route guard** — client-side, prevents wrong-role users from even reaching the wrong dashboard

### CORS

`django-cors-headers` configured with an explicit allowlist (`CORS_ALLOWED_ORIGINS`). In production, only the Vercel frontend domain is allowed.

### Password validation

Django's built-in validators enforce minimum length (8 chars), common password detection, and numeric-only prevention. The registration serializer adds `min_length=8` at the field level.

### Role protection

`tpo_admin` accounts cannot be self-registered. The `RegisterSerializer.validate_role()` method raises a validation error for privileged roles. TPO admin accounts must be created by an existing admin via the Django admin panel.

---

## 24. API Reference

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/token/` | None | Login — returns access + refresh tokens |
| POST | `/api/auth/token/refresh/` | None | Refresh access token |
| GET | `/api/auth/me/` | Any | Get current user profile |
| PATCH | `/api/auth/profile/update/` | Any | Update profile fields |
| POST | `/api/auth/register/` | None | Register new student/recruiter |

### Drives

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/drives/create/` | TPO | Create drive + eligibility rules |
| GET | `/api/drives/all/` | TPO | All drives (management view) |
| GET | `/api/drives/eligible/` | Student | Student's eligible drives |
| GET | `/api/drives/pending/` | TPO | Drives awaiting approval |
| POST | `/api/drives/{id}/approve/` | TPO | Approve recruiter submission |
| GET/PUT/DELETE | `/api/drives/{id}/` | Auth | Drive detail |
| POST | `/api/drives/recruiter/create/` | Recruiter | Submit JD for approval |
| GET | `/api/drives/recruiter/mine/` | Recruiter | My posted drives |

### Applications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/applications/apply/` | Student | Apply to a drive |
| GET | `/api/applications/mine/` | Student | My applications |
| GET | `/api/applications/score-history/` | Student | Match score history |
| GET | `/api/applications/drive/{id}/applicants/` | TPO | All applicants for a drive |
| PATCH | `/api/applications/{id}/status/` | TPO | Update application status |
| GET | `/api/applications/drive/{id}/export/` | TPO | CSV export |
| GET | `/api/applications/drive/{id}/analytics/` | TPO | Status breakdown chart data |
| GET | `/api/applications/analytics/overall/` | TPO | Branch + drive-wise stats |
| GET | `/api/applications/drive/{id}/shortlist/` | Recruiter | Shortlisted candidates |

### Resumes

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/resumes/upload/` | Student | Upload PDF/DOCX resume |
| GET | `/api/resumes/mine/` | Student | My resumes + parsing status |

---

## 25. Project Structure

```
placement-command-center/
├── backend/                          # Django project
│   ├── accounts/                     # User model, auth, registration
│   │   ├── management/commands/      # create_admin command
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
│   ├── colleges/                     # College reference model
│   ├── drives/                       # Drive + EligibilityRule
│   │   ├── models.py                 # Rule engine logic lives here
│   │   ├── serializers.py            # Nested rule creation
│   │   ├── views.py                  # Eligible feed, approval flow
│   │   ├── tasks.py                  # notify_eligible_students
│   │   ├── signals.py                # Cache invalidation
│   │   └── apps.py                   # Signal registration via ready()
│   ├── applications/                 # Application lifecycle
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py                  # Apply, manage, export, analytics
│   │   ├── tasks.py                  # trigger_match_scoring
│   │   └── matching.py               # Groq LLM match scoring logic
│   ├── resumes/                      # Resume upload + parsing
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── tasks.py                  # parse_resume_task
│   │   ├── text_extraction.py        # PDF/DOCX → raw text
│   │   └── llm_parser.py             # Raw text → structured JSON via Groq
│   ├── config/                       # Project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   ├── requirements.txt
│   ├── Procfile                      # gunicorn start command
│   └── runtime.txt                   # Python version pin
│
├── matching-service/                 # (Legacy) FastAPI microservice
│   └── app/                          # Replaced by Groq in applications/matching.py
│
└── frontend/                         # React + Vite
    ├── src/
    │   ├── api/                      # All API call functions
    │   ├── components/               # Shared UI components
    │   ├── pages/                    # Role-specific page components
    │   ├── routes/                   # ProtectedRoute component
    │   ├── store/                    # Zustand auth store
    │   └── App.jsx                   # Router + QueryClient setup
    ├── vercel.json                   # SPA routing config
    ├── .env.production               # Production API URL
    └── .env.development              # Local API URL
```

---

## 26. Local Development Setup

### Prerequisites

- Python 3.14+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/sureshba234/placement-backend.git
git clone https://github.com/sureshba234/placement-frontend.git
```

### 2. Backend setup

```bash
cd placement-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Environment Variables section)
cp .env.example .env
# Edit .env with your values

# Database setup
sudo -iu postgres psql
# CREATE DATABASE placement_db;
# CREATE USER placement_user WITH PASSWORD 'yourpassword';
# GRANT ALL ON SCHEMA public TO placement_user;
# ALTER SCHEMA public OWNER TO placement_user;

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django dev server
python manage.py runserver
```

### 3. Celery worker (separate terminal)

```bash
cd placement-backend
source venv/bin/activate
celery -A config worker --loglevel=info
```

### 4. Frontend setup

```bash
cd placement-frontend
npm install
npm run dev
```

### 5. Access the app

- Frontend: http://localhost:5173
- Django API: http://localhost:8000
- Django Admin: http://localhost:8000/admin/

### Services required

All four must be running simultaneously for full functionality:
1. `python manage.py runserver` — Django web server
2. `celery -A config worker` — Background task worker
3. `redis-server` — Message broker + cache (usually via systemctl)
4. PostgreSQL — Database (usually via systemctl)

---

## 27. Environment Variables

### Backend `.env`

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=placement_db
DB_USER=placement_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS (comma-separated for multiple origins)
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

# External services
MATCHING_SERVICE_URL=http://localhost:8001
GROQ_API_KEY=gsk_your_groq_api_key

# Email (Gmail SMTP)
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password
DEFAULT_FROM_EMAIL=your@gmail.com

# Production flag
USE_CELERY=True
```

### Frontend `.env.development`

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Frontend `.env.production`

```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

---

## 28. Deployment Guide

### Backend — Render

1. Create a PostgreSQL database on Render (free tier)
2. Create a Redis Key Value store on Render (free tier)
3. Create a Web Service connecting `sureshba234/placement-backend`
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn config.wsgi --log-file -`
4. Set all environment variables (see above) using production values:
   - `DATABASE_URL` — from Render Postgres (Internal URL)
   - `REDIS_URL` — from Render Redis (Internal URL)
   - `DEBUG=False`
   - `USE_CELERY=False` (no free background worker tier)
   - `ALLOWED_HOSTS=your-service-name.onrender.com`
   - `CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app`

### Frontend — Vercel

1. Import `sureshba234/placement-frontend` on Vercel
2. Framework preset: Vite (auto-detected)
3. No environment variables needed — `VITE_API_BASE_URL` is in `.env.production` which is committed

### Production notes

- Render's free web service sleeps after 15 minutes of inactivity. First request after sleep takes 30–60 seconds to wake up.
- Render's free PostgreSQL has a 1GB storage limit.
- Render's free Redis has a 25MB limit.
- Without a Celery worker, tasks run synchronously in the web process. For production scale, upgrade to a paid background worker.

---

## 29. Architectural Decisions

### Why Django over FastAPI for the main API?

Django was chosen for the "boring but critical" parts — auth, admin, ORM, migrations — because it saves weeks of boilerplate. FastAPI would require building all of that from scratch. The original design included FastAPI as a separate microservice for AI matching, but this was refactored to a Groq API call inside Django to eliminate the deployment complexity (and memory constraints) of a separate service.

### Why Groq over OpenAI/Anthropic for LLM calls?

Groq provides a free tier (14,400 requests/day) with no credit card required, which aligns with the portfolio project constraint of zero operational cost. The API interface is OpenAI-compatible, so swapping to a different LLM provider later requires only changing the base URL and model name.

### Why sentence-transformers was replaced

The original FastAPI matching service used `sentence-transformers` (BERT-based embeddings) for resume-JD similarity. This was replaced with Groq LLM for two reasons: PyTorch's 500MB footprint exceeded Render's free-tier RAM limit, and LLM-based matching produces more semantically meaningful results since it understands context rather than just computing vector distances.

### Why Redis for both cache and Celery broker?

One service instead of two. At this scale there's no reason to run separate Redis instances. In production at scale, you'd separate them — but for a portfolio project, the shared instance simplifies deployment and reduces cost.

### Why `unique_together` instead of application-level deduplication?

Database constraints are more reliable than application-level checks. A race condition could allow two simultaneous applications from the same student before either check completes. The `unique_together = ('student', 'drive')` constraint on the Application model makes duplicate applications physically impossible at the database level.

### Why no Redux?

React Query handles server state (which is the majority of what ends up in Redux in most React apps). Zustand handles auth state (synchronous, simple). Redux would add significant boilerplate without adding capability for a project this size. Using Redux here would actually be a minor red flag — it signals cargo-culting a pattern without understanding when it's appropriate.

---

## 30. Future Improvements

### Short term
- **Resume score history improvement tracking** — show progress over time as students improve their resumes and apply to more drives
- **Bulk application status updates** — TPO can shortlist/reject multiple applicants in one action
- **Drive search and filtering** — students can filter eligible drives by company, deadline, or role type
- **Notification preferences** — students opt in/out of email notifications per drive type

### Medium term
- **Real Celery workers in production** — upgrade to a paid Render plan for the background worker; the architecture is already fully async-ready
- **Resume version management** — students can maintain multiple resume versions and select which version to use per application
- **Recruiter analytics** — recruiter dashboard showing how their JDs perform (applicant volume, match score distribution)
- **OAuth login** — "Login with Google" for students to reduce friction

### Long term
- **Mobile-responsive redesign** — current UI is functional but not optimized for mobile; students primarily access placement platforms on phones
- **Real-time updates via WebSockets** — replace polling with server-sent events or WebSockets for instant match score and parsing status updates
- **Advanced NLP features** — keyword extraction from JDs, auto-suggest skills for students to add based on drive eligibility patterns
- **Multi-college support** — full multi-tenancy where multiple colleges run separate placement cells on the same platform

---

## Demo Credentials

For testing the live demo:

| Role | Username | Password |
|------|----------|----------|
| TPO Admin | admin | Admin@12345 |
| Student | Create via /register | — |
| Recruiter | Create via /register | — |

**Live URL:** https://placement-frontend-weld.vercel.app

---

## Author

**Bathina Suresh**  
Full Stack Developer | Campus Placement 2026  
GitHub: [@sureshba234](https://github.com/sureshba234)  
Email: suresh1234bathina@gmail.com

---

## License

MIT License — free to use, modify, and distribute with attribution.
