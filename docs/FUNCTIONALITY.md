# Conquest Portal — Comprehensive Functionality Overview

**Last updated:** April 2026  
**Scope:** Backend (Django + DRF) + Frontend (React/Vite) — full startup accelerator platform

---

## Table of Contents

1. [Roles](#1-roles)
2. [Pages & Frontend Routes](#2-pages--frontend-routes)
3. [API Endpoints](#3-api-endpoints)
4. [Database Models](#4-database-models)
5. [Feature Flows](#5-feature-flows)
6. [Permissions Matrix](#6-permissions-matrix)
7. [Forms System (Deep Dive)](#7-forms-system-deep-dive)
8. [Meeting System (Deep Dive)](#8-meeting-system-deep-dive)
9. [Admin-Only Features & Customizations](#9-admin-only-features--customizations)
10. [Integrations](#10-integrations)
11. [Known Issues & Incomplete Features](#11-known-issues--incomplete-features)

---

## 1. Roles

The system defines 14 roles, stored in `UserProfile.role`. Each role has specific visibility, connection, and data access permissions.

### Startup
A founding team member launching a company within the accelerator cohort. Can fill out their company profile (product, funding stage, team, vision), book calls with mentors/coaches/experts, submit forms, view and request connections with other professionals, and track their guided mentors. Cannot see admin announcements unless explicitly targeted. **Can see:** Mentors, Function Experts, Coaches, Partners, Angels, Consultants. **Can request:** Partners, Alumni, Communities. **Actions:** complete profile, book 2–4 mentors, submit forms, request/accept connections, capture interest in consultants/resources.

### Mentor
Experienced founder or operator who publishes available time slots, accepts meeting requests from startups, and optionally provides feedback after meetings. Mentors have a profile with company, title, description, expertise domains (sector/function), and optionally resume/LinkedIn. **Can see:** Mentors, Function Experts, Coaches, Partners, Communities, Angels, Consultants, Partner - Individual Connected. **Can request:** N/A. **Actions:** publish meeting slots, accept/reject meeting requests, provide post-meeting feedback, edit profile, view startups they guide.

### Coach
Operational or interpersonal specialist (e.g., fundraising coach, go-to-market coach) who runs slots and meets with startups similarly to mentors, with optional domain-of-expertise fields. **Can see:** same as Mentor. **Can request:** N/A. **Actions:** same as Mentor.

### Function Expert (Functional Expert)
Domain specialist in a specific business function (e.g., growth, product, legal). Publishes slots and accepts meetings. Stores function-of-expertise field. **Can see:** same as Mentor. **Actions:** same as Mentor.

### Angel
Early-stage investor or high-net-worth individual interested in startups in the cohort. Can view startups, publish slots (optional), request connections. **Can see:** Mentors, Function Experts, Coaches, Partners, Communities, Partner - Individual Connected, Consultants. **Can request:** N/A. **Actions:** view/book meetings, send/accept connection requests.

### Consultant
Business advisor or operational specialist (e.g., tax, IP). Can view startups, accept meeting requests, and be tagged by startups as interested in their challenges. **Can see:** same as Angel. **Actions:** view startups, accept/reject meetings, receive interest-capture notifications.

### Alumni
Founder or early employee of a company that has exited the cohort or graduated. Can view and request connections with specific roles (Mentor, Function Expert, Coach, Startup, Community, Alumni). **Can see:** Partner - Company, Partner - Individual Connected only. **Can request:** Mentors, Function Experts, Coaches, Startups, Communities, Angels. **Actions:** browse startups, request/accept connections.

### Partner - Company
Corporate sponsor, vendor, or enterprise partner. Can see startups and all other partners. Can publish slots (optional). **Can see:** Mentors, Function Experts, Coaches, Partner - Company, Community, Partner - Individual Connected, Angel, Consultant. **Can request:** N/A. **Actions:** view startups, offer resources/discounts, publish calls, mark startup interest in company programs.

### Partner - Individual Connected
Individual from a partner company or ecosystem player. Similar visibility to Partner - Company. **Can see:** same as Partner - Company. **Can request:** N/A. **Actions:** same as Partner - Company.

### Community
Ecosystem builder, journalist, or community leader (e.g., event organizer). Can view startups and most other roles. Cannot request connections. **Can see:** Mentors, Function Experts, Coaches, Partner - Company, Community, Alumni, Partner - Individual Connected, Angel, Consultant. **Can request:** Startups only. **Actions:** view/browse startups and mentors, limited interaction.

### Guest - Tier 1
Low-friction invite-only access (e.g., from a web landing page). Can view startups and many roles but cannot fully interact. Restricted from core dashboard (cannot see Home, Experts, Mentors, Coaches, Connections, Forms sections). **Can see:** Mentors, Function Experts, Coaches, Partner - Company, Community, Alumni, Partner - Individual Connected, Angel, Consultant, Startup. **Can request:** N/A. **Actions:** view profiles, limited to Meetings, Resources, Startups, Partners, Angels, Consultants routes.

### Guest - Tier 2
Lowest-access role. Automatically assigned to new Google OAuth sign-ups. No data completion required. Redirected to Meetings route if they try to access restricted paths. **Can see:** Startups only. **Can request:** N/A. **Actions:** browse startups, sign up for global events, cannot create meetings or forms.

### CEL Admin (Accelerator Admin)
Staff user (Django `is_staff=True`) who runs the cohort: approves/rejects connection requests, broadcasts announcements to targeted role groups, manages forms (create, edit, view responses), approves startup-to-mentor meetings, and manages global events. Typically a Django superuser. **Actions:** all dashboard access, admin panel full access, approve/reject connections, create announcements, manage forms & answers, CEL-approve meetings, manage global events.

### DVM Admin (Data/System Admin)
Superuser with full Django admin access. Can create/modify users, change role assignments, edit all records (startup profiles, answers), export forms data, manage all settings. Typically Django `is_superuser=True`. **Actions:** full Django admin, add/remove users, change role assignments, edit all user/startup/form data, export via `django-import-export`, manage database directly.

---

## 2. Pages & Frontend Routes

All routes render under `NullUserAuth` wrapper, meaning any authenticated user can access them. Within the Dashboard, `RequireAuth` restricts specific tabs (Home, Experts, Mentors, Coaches, Connections, Forms) — accessible to all non-Guest-Tier-2 roles.

### Landing Page
**Route:** `/`  
**Component:** `LandingPage`  
**Auth:** None (public)  
**Purpose:** Marketing/signup entry point. Shows "Sign In with Google" or username/password login form. Redirects authenticated users to dashboard.

### Login
**Route:** `/login`  
**Component:** `Login`  
**Auth:** None (public)  
**Purpose:** Dual login: Google OAuth (calls `/api/users/login/google/`) or username/password (calls `/api/users/login/username/`). On success, stores JWT tokens + user profile in localStorage and redirects to `/dashboard`.

### Unauthorised
**Route:** `/unauthorised`  
**Component:** `Unauthorised`  
**Auth:** None  
**Purpose:** Shown when a user lacks permission for a route (e.g., Guest - Tier 2 trying to access Home).

### Dashboard (Parent)
**Route:** `/dashboard`  
**Component:** `Dashboard`  
**Auth:** `NullUserAuth` (any authenticated user)  
**Purpose:** Main navigation hub. Renders sidebar (role-aware menu) and outlet for child routes. Sidebar shows links based on user role (Guest - Tier 2 hides Experts, Mentors, Coaches, Connections, Forms).

### Dashboard / Home
**Route:** `/dashboard` (index child)  
**Component:** `Home`  
**Auth:** `RequireAuth` (blocks Guest - Tier 2)  
**Purpose:** Role-specific dashboard landing. For Startups: shows stats, upcoming meetings, guided mentors, pending connection requests. For Mentors/Coaches/Experts: shows recent startups they've met, peer mentors, stats. Calls:
- `GET /api/users/guided_startups/` (mentor's mentees)
- `GET /api/users/startup_list/` (for stats/overview)
- `GET /api/meetings/meetings/upcoming/`

### Dashboard / Meetings
**Route:** `/dashboard/meetings`  
**Component:** `Meetings`  
**Auth:** `NullUserAuth`  
**Purpose:** Core scheduling interface. **For Startups:** browse available mentor/coach/expert slots (via `/api/meetings/user/<id>/meeting-slots/`), select 2–4, and request meetings (POST `/api/meetings/requests/`). Can see pending, upcoming, and past meetings. **For Mentors/Coaches/Experts:** publish available time slots (POST `/api/meetings/slots/`), manage pending requests (accept/reject via PATCH `/api/meetings/requests/<id>/`), view accepted meetings, edit/delete slots. Calls multiple meeting endpoints.

### Dashboard / Resources
**Route:** `/dashboard/resources`  
**Component:** `Resources`  
**Auth:** `NullUserAuth`  
**Purpose:** Browse and interact with partners (Partner - Company, Partner - Individual Connected). Startups can mark interest in a partner's resources/programs (POST `/api/users/consultant-resource/interestcapture/`). Partners can see who's interested. View partner profiles.

### Dashboard / Startups
**Route:** `/dashboard/startups`  
**Component:** `Startups`  
**Auth:** `NullUserAuth`  
**Purpose:** Global searchable list of all startups. Anyone can click to view a startup's profile (company description, funding stage, product, team). Shows logo, stage, industry, location, pitch deck link. Non-Startup roles cannot edit.

### Dashboard / Startup Profile
**Route:** `/dashboard/startup-profile/:id?`  
**Component:** `StartupProfile`  
**Auth:** `NullUserAuth`  
**Purpose:** Detailed view + edit form for a startup. If `:id` is omitted, shows the logged-in user's startup (if role is Startup). Otherwise shows read-only view of another startup. Fields: name, description, stage, industry, HQ location, problem statement, target audience, USP, revenue streams, vision, competitors, TAM/SAM/SOM, funding stage, valuation, team members (name/position/LinkedIn/photo), investors, pitch deck, video pitch, website, Twitter, LinkedIn. Calls:
- `GET /api/users/profile/startup/` (own startup)
- `GET /api/users/startup_detail/` (another startup)
- `PATCH /api/users/profile/startup/` (edit own)

### Dashboard / Partners (Investors, Angels, Consultants)
**Routes:** `/dashboard/partners`, `/dashboard/angels`, `/dashboard/consultants`  
**Components:** `Investors`, `Angels`, `Consultants`  
**Auth:** `NullUserAuth`  
**Purpose:** Filtered views of Partner - Company, Angel, and Consultant roles respectively. Browse profiles, see expertise/offerings, view/request connections. Calls `GET /api/users/expert_list/` (for partners and experts).

### Dashboard / Mentors
**Route:** `/dashboard/mentors`  
**Component:** `Mentors`  
**Auth:** `RequireAuth`  
**Purpose:** Browse mentors (Mentor role). Shows name, company, designation, description, expertise (sector/domain/function), LinkedIn, resume link. Startups can click to view slots and book. Calls:
- `GET /api/users/expert_list/` (filter by Mentor)
- `GET /api/meetings/user/<id>/meeting-slots/`

### Dashboard / Coaches
**Route:** `/dashboard/coaches`  
**Component:** `Coaches`  
**Auth:** `RequireAuth`  
**Purpose:** Browse coaches (Coach role). Similar to Mentors: name, designation, expertise, slots. Calls same endpoints.

### Dashboard / Experts
**Route:** `/dashboard/experts`  
**Component:** `Experts`  
**Auth:** `RequireAuth`  
**Purpose:** Browse Function Experts. Similar to Mentors. Calls same endpoints.

### Dashboard / Profile (Mentor/Coach/Expert)
**Route:** `/dashboard/profile/:id?`  
**Component:** `MentorProfile`  
**Auth:** `NullUserAuth`  
**Purpose:** Detailed view of a mentor/coach/expert. If `:id` omitted, shows logged-in user's own profile (editable). Otherwise read-only. Fields: name, company, designation, LinkedIn, location, description, resume, sector/domain/function of expertise, offering, comments, no_of_calls. Calls:
- `GET /api/users/profile/` (own)
- `GET /api/users/profile_detail/` (another user)
- `PATCH /api/users/profile/` (edit own)

### Dashboard / Connections
**Route:** `/dashboard/connections`  
**Component:** `Connections`  
**Auth:** `RequireAuth`  
**Purpose:** Manage connection requests (follow relationship system). Startup or other roles can send, receive, accept, delete connection requests. Shows pending (not yet approved by CEL) and approved connections. Calls:
- `GET /api/users/connections/list/`
- `POST /api/users/connections/send/` (request new)
- `POST /api/users/connections/accept/` (accept pending)
- `DELETE /api/users/connections/delete/` (withdraw)

### Dashboard / Forms
**Route:** `/dashboard/forms`  
**Component:** `Forms`  
**Auth:** `RequireAuth`  
**Purpose:** View and fill out forms assigned to the user. Shows list of unanswered forms (calls `GET /api/forms/list/`), click to open modal with all question types (subjective, scoring, file upload, preference ranking). Submit answers (POST `/api/forms/<id>/answers/`). CEL Admin sees Form Management tab in admin panel instead.

---

## 3. API Endpoints

### Users App (`/api/users/`)

#### Authentication

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| POST | `/login/google/` | `GoogleLogin` | None | Accept Google access token, verify with Google API, create/login user, return JWT tokens |
| POST | `/login/username/` | `UsernameLogin` | None | Accept username + password, authenticate, return JWT + user profile |
| POST | `/logout/` | `GoogleLogout` | JWT | Blacklist refresh token, logout |
| POST | `/token/` | DRF `TokenObtainPairView` | None | (Standard JWT endpoint) Obtain initial tokens from username/password |
| POST | `/token/refresh/` | DRF `TokenRefreshView` | None | Refresh access token using refresh token |

**GoogleLogin request/response:**
```json
POST /api/users/login/google/
{ "access_token": "..." }

Response:
{
  "message": "user verified and data complete" | "new guest user created",
  "tokens": { "refresh": "...", "access": "...", "access_token_lifetime": 3600000 },
  "user_profile_obj": { UserProfile fields },
  "user_pfp_url": "..."
}
```

**UsernameLogin request/response:**
```json
POST /api/users/login/username/
{ "username": "...", "password": "..." }

Response:
{
  "message": "Startup user logged in successfully.",
  "tokens": { ... },
  "user_profile_obj": { ... },
  "startup_profile": { ... }
}
```

#### Profile Management

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/profile/` | `RetrieveEditProfileView` | JWT | Get logged-in user's profile (UserProfile) |
| PATCH | `/profile/` | `RetrieveEditProfileView` | JWT | Edit logged-in user's profile (name, company, designation, description, etc.) |
| GET | `/profile/startup/` | `RetrieveEditStartupView` | JWT | Get logged-in startup's Startup record |
| PATCH | `/profile/startup/` | `RetrieveEditStartupView` | JWT | Edit startup profile (product, funding, vision, team, etc.) |
| GET | `/profile_detail/?username=...` | `UserProfileDetailView` | JWT | Get another user's profile by username |
| POST | `/update-email/` | `UpdateEmail` | JWT | Update email address (username login users only) |

#### Listings & Search

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/startup_list/` | `StartupListView` | JWT | List all startups visible to logged-in user (respects CAN_VIEW permissions) |
| GET | `/expert_list/` | `ExpertListView` | JWT | List all mentors, coaches, experts, partners, angels visible to user |
| GET | `/startup_detail/?id=...` | `StartupDetailView` | JWT | Get a specific startup's full profile by ID |
| GET | `/search/?username=...&role=...` | `SearchProfile` | JWT | Search for users by username/role |
| GET | `/role-list/` | `RoleList` | JWT | Get all role options (ALL_ROLES) |

#### Connections

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/connections/list/` | `ListConnections` | JWT | List all connection requests (sent + received) for user |
| POST | `/connections/send/` | `SendConnectionView` | JWT | Send connection request to another user (must be in can_view list) |
| POST | `/connections/accept/` | `AcceptConnectionView` | JWT | Accept a pending connection request (if CEL admin approves first) |
| DELETE | `/connections/delete/` | `DeleteConnectionView` | JWT | Delete/withdraw a connection request |

**Request format:**
```json
POST /api/users/connections/send/
{ "username": "target_username" }

Response:
{ "success": "connection request sent", "connection": { Connection fields } }
```

#### Mentor Guidance

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/guided_startups/` | `StartupsUnderMentorView` | JWT | Get startups under mentorship of logged-in mentor/coach |

**Response:**
```json
[
  {
    "id": 1,
    "startup_name": "...",
    "stage": "...",
    "industry": "...",
    ...
  }
]
```

#### Interest Capture (Startups marking interest in Consultants/Resources)

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| POST | `/consultant-resource/interestcapture/` | `InterestCaptureView` | JWT | Startup marks interest in a Consultant or Partner - Company resource |

**Request:**
```json
{
  "for_consultant": 123,    // optional, UserProfile ID
  "for_resource": 456       // optional, UserProfile ID
}
```

---

### Meetings App (`/api/meetings/`)

#### Meeting Slots (Mentor/Coach/Expert publish availability)

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/slots/` | `MeetingSlotCreate` | JWT | List user's own meeting slots |
| POST | `/slots/` | `MeetingSlotCreate` | JWT | Create a new meeting slot (user extracted from token) |
| GET | `/slots/<id>/` | `MeetingSlotDetail` | JWT | Retrieve a specific slot |
| PATCH | `/slots/<id>/` | `MeetingSlotDetail` | JWT | Update a slot (e.g., change time) |
| DELETE | `/slots/<id>/` | `MeetingSlotDetail` | JWT | Delete a slot |
| GET | `/user/<user_id>/meeting-slots/` | `UserMeetingSlotsView` | None | Get free slots for a specific user (used by Startups browsing) |

**Slot schema:**
```json
{
  "id": 1,
  "user": 123,                    // UserProfile ID
  "start_time": "2024-06-05T10:00:00Z",
  "end_time": "2024-06-05T11:00:00Z",
  "free": true
}
```

#### Meeting Requests (Startup requests mentor, or vice versa)

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/requests/` | `MeetingRequestCreate` | JWT | List meeting requests received by user |
| POST | `/requests/` | `MeetingRequestCreate` | JWT | Create a meeting request (from Startup to Mentor, or CME to Startup) |
| GET | `/requests/<id>/` | `MeetingRequestDetail` | JWT | Get a specific request |
| PATCH | `/requests/<id>/` | `MeetingRequestDetail` | JWT | Accept/reject request (status='accepted'/'rejected'), CEL approval auto-generates meet link |

**Request schema:**
```json
{
  "id": 1,
  "requester": 1,                         // UserProfile ID (Startup or CME user)
  "requested": 2,                         // UserProfile ID (CME user or Startup)
  "slot": 10,                             // MeetingSlot ID (optional if Flow2)
  "slot_start_time": "...",               // DateTime (used if slot is null)
  "slot_end_time": "...",                 // DateTime (used if slot is null)
  "status": "pending" | "accepted" | "rejected",
  "meet_link": "https://...",             // Generated on accept
  "recording": "https://...",             // Post-meeting
  "minutes_of_meet": "...",               // Post-meeting notes
  "requester_feedback_score": 8,          // 0-10, post-meeting
  "requested_feedback_score": 9,          // 0-10, post-meeting
  "cel_approved": false
}
```

#### Meeting Views (Dashboards)

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/meetings/upcoming/` | `upcoming_meetings` | JWT | Get future meetings (slot_start_time >= now, status='accepted', cel_approved=true) |
| GET | `/meetings/past/` | `past_meetings` | JWT | Get past meetings (slot_end_time < now, status='accepted') |
| GET | `/meetings/pending/` | `pending_meetings` | JWT | Get unresponded requests (status='pending', slot not past) |
| GET | `/all_meetings/` | `all_meetings` | JWT | Get all meeting requests (sent + received) |
| GET | `/requested_meetings/` | `requested_meetings` | JWT | Get all requests sent by user |

#### Global Events (Company-wide calls, webinars)

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/event/` | `GlobalEventCreate` | JWT | List all global events |
| POST | `/event/` | `GlobalEventCreate` | JWT | Create a global event (CEL admin only in practice) |
| GET | `/event/<id>/` | `GlobalEventDetail` | JWT | Get a specific event |
| PATCH | `/event/<id>/` | `GlobalEventDetail` | JWT | Update event |
| DELETE | `/event/<id>/` | `GlobalEventDetail` | JWT | Delete event |

**Schema:**
```json
{
  "id": 1,
  "name": "Demo Day",
  "description": "...",
  "slot_start_time": "2024-06-05T18:00:00Z",
  "slot_end_time": "2024-06-05T19:00:00Z",
  "meet_link": "https://...",
  "recording": "https://..."
}
```

#### Booking Portal Control

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/portal_state/` | `portal_state_view` | None | Check if booking portal is active (Boolean) |

---

### Forms App (`/api/forms/`)

#### Form Assignment & Answering

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/list/` | `GetForms` | JWT | Get all forms available to user that they haven't answered yet |
| GET | `/<id>/questions/` | `GetFormQuestions` | JWT | Get all questions (all types) for a form |
| POST | `/<id>/answers/` | `AddAnswers` | JWT | Submit answers to a form (all question types) |
| POST | `/send-email/` | `send_resource_email` | JWT | Send resource email to startup (CEL admin only) |

**Form question structure (GET response):**
```json
{
  "form_id": 1,
  "form_name": "Pitch Evaluation",
  "subjective_questions": [
    { "id": 1, "question": "...", "type": "Long" | "Short" | "Single Line" }
  ],
  "file_upload_questions": [
    { "id": 2, "question": "..." }
  ],
  "scoring_questions": [
    { "id": 3, "question": "..." }
  ],
  "preference_questions": [
    {
      "id": 4,
      "question": "Rank these verticals:",
      "preferences": [
        { "id": 100, "preference_name": "B2B SaaS" },
        { "id": 101, "preference_name": "DeepTech" }
      ]
    }
  ]
}
```

**Submit answers (POST):**
```json
{
  "subjective_questions": [
    { "id": 1, "ans": "Product solves X problem..." }
  ],
  "file_upload_questions": [
    { "id": 2, "ans": "https://drive.google.com/..." }
  ],
  "scoring_questions": [
    { "id": 3, "ans": 8 }
  ],
  "preference_questions": [
    {
      "id": 4,
      "preferences": [
        { "id": 100, "position": 1 },
        { "id": 101, "position": 2 }
      ]
    }
  ]
}

Response:
{ "success": "answers saved successfully" }
```

---

### Staff App (`/api/staff/`)

#### Notifications

| Method | Path | View | Auth | Purpose |
|--------|------|------|------|---------|
| GET | `/notifications/` | `GetNotifications` | JWT | List all notifications for user (unread count included) |

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "user": 123,
      "message": "Connection request from ...",
      "read": false,
      "attachment": "https://...",
      "timestamp": "2024-06-05T10:00:00Z"
    }
  ],
  "unread_count": 5
}
```

---

## 4. Database Models

### Users App

**UserProfile**
- `user` (1:1 to Django User)
- `role` (CharField, choices = ALL_ROLES)
- `profile_logo` (URLField)
- `google_email`, `google_user_id` (OAuth identifiers)
- `name`, `company_name`, `designation` (profile info)
- `linkedin`, `website`, `resume` (URLs)
- `location`, `description` (text)
- `sector_of_expertise`, `domain_of_expertise`, `function_of_expertise` (specialization)
- `type_of_partner` (for partners: Corporate, Investment, Outreach, Ecosystem, Knowledge, Community)
- `verticals`, `horizontals`, `business_models`, `offering` (additional fields for experts/partners)
- `data_complete` (Boolean, gates login redirect to onboarding)
- `no_of_calls`, `comments` (admin fields)
- **Methods:** `can_view()` (returns queryset of users this role can see based on CAN_VIEW/CAN_CREATE/CAN_REQUEST dicts), `can_create()`, `can_request()`

**Startup**
- `user_profile` (1:1 to UserProfile, nullable)
- `startup_name`, `description`, `stage`, `industry`, `functional_areas`, `location_hq`
- `pitch_deck`, `video_pitch`, `website_url`, `linkedin`, `twitter` (URLs)
- `contact_email` (contact)
- `team` (string, ideally comma-separated), `investors`, `track` (narrative)
- `problem_statement`, `target_audience`, `revenue_stream`, `usp` (pitch fields)
- `short_term_vision`, `long_term_vision` (vision)
- `competitors`, `tam`, `sam`, `som` (market sizing)
- `funding`, `fund_stage`, `valuation` (funding details)
- `profile_logo` (company logo)
- `startup_champion`, `startup_poc` (ForeignKey to UserProfile, assigned CEL admin to mentor this startup)
- `under_guidance_of` (M2M to UserProfile — mentors guiding this startup)
- `data_complete`, `registration_steps_completed` (onboarding progress)

**Connection**
- `from_user`, `to_user` (ForeignKey to UserProfile) — directional request
- `approved` (Boolean, set by CEL admin after vetting)
- `accepted` (Boolean, set by recipient after accepting)
- Validation: no self-connections, no duplicate requests (either direction)

**StartUpMember**
- `position`, `name`, `linkedin`, `profile_pic` (team member details)
- `under_startup` (ForeignKey to Startup)

**InterestCapture**
- `from_startup` (ForeignKey to Startup)
- `for_consultant` (ForeignKey to UserProfile, limit Consultant role, nullable)
- `for_resource` (ForeignKey to UserProfile, limit Partner - Company role, nullable)
- `interest_captured` (Boolean, default True)

---

### Meetings App

**MeetingSlot**
- `user` (ForeignKey to UserProfile — mentor/coach/expert)
- `start_time`, `end_time` (DateTimeField, UTC)
- `free` (Boolean, True if unbooked)
- One mentor can have many slots; slots represent their published availability

**MeetingRequest**
- `requester` (ForeignKey, related_name='sent_requests')
- `requested` (ForeignKey, related_name='received_requests')
- `slot` (ForeignKey to MeetingSlot, nullable — null means Flow 2, CME proposes time)
- `slot_start_time`, `slot_end_time` (cached copy of slot times if slot is null)
- `status` (pending, accepted, rejected)
- `meet_link` (URLField, auto-generated on CEL approval)
- `recording`, `minutes_of_meet` (post-meeting fields)
- `requester_feedback_score`, `requested_feedback_score` (1-10, post-meeting)
- `cel_approved` (Boolean, gates meeting from pending to accepted if true)
- **Business logic:** When CEL approves (cel_approved=True), status auto-set to 'accepted', slot.free set to False, meet link generated

**GlobalEvent**
- `name`, `description` (CharField, TextField)
- `slot_start_time`, `slot_end_time`
- `meet_link`, `recording`
- Represents company-wide webinars, demo days, speaker sessions

**BookingPortal**
- `is_active` (Boolean) — gates whether startups can book mentor meetings on the frontend

---

### Forms App

**Form**
- `available_to` (M2M to UserProfile — which roles get this form)
- `form_name` (CharField)

**SubjectiveQuestion**
- `form` (ForeignKey to Form, related_name='subjective_questions')
- `question` (TextField)
- `type` (CharField, choices: Single Line, Short, Long) — validation currently disabled in views

**FileUploadQuestion**
- `form`, `question` (same as above)

**ScoringQuestion**
- `form`, `question` (same as above)
- Expects integer 1–10 answer

**PreferenceQuestion**
- `form`, `question`
- M2M to `Preference` (via related_name 'preferences')

**Preference**
- `under_question` (ForeignKey to PreferenceQuestion)
- `preference_name` (TextField) — e.g., "B2B SaaS", "DeepTech"

**Answer**
- `form` (ForeignKey, related_name='answers')
- `answered_by` (ForeignKey to UserProfile)
- Parent record for a user's form submission

**SubjectiveAns**
- `under_answer` (ForeignKey to Answer)
- `subjective_question` (ForeignKey to SubjectiveQuestion)
- `answer` (TextField)

**ScoreAns**
- `under_answer`, `scoring_question`, `answer` (IntegerField, 1-10)

**FileAns**
- `under_answer`, `file_question`, `answer` (URLField)

**PreferenceAnsMain**
- `under_answer` (ForeignKey to Answer)
- `preference_question` (ForeignKey to PreferenceQuestion)
- Container for ranked preferences for a single preference question

**PreferenceAns**
- `preference_ans` (ForeignKey to PreferenceAnsMain)
- `preference_obj` (ForeignKey to Preference)
- `position` (IntegerField, rank 1, 2, 3, etc.)
- One row per preference, repeats with different positions

---

### Staff App

**Announcement**
- `roles` (CharField, comma-separated string of role names)
- `message` (TextField, up to 1000 chars)
- `attachment` (URLField, optional)
- CEL admin creates via Django admin, specifies which roles see it
- Not accessible via REST API (admin-only)

**Notification**
- `user` (ForeignKey to UserProfile)
- `message` (CharField)
- `read` (Boolean, default False)
- `attachment` (URLField, optional)
- `timestamp` (auto_now_add)
- Created whenever a relevant event happens (e.g., connection request, meeting acceptance)

---

## 5. Feature Flows

### 5.1 Startup Onboarding & Profile Completion

**Trigger:** New user signs up via Google OAuth.

**Steps:**
1. Frontend calls POST `/api/users/login/google/` with access token
2. Backend verifies token with Google API, creates User + UserProfile (role='Guest - Tier 2', data_complete=False)
3. Returns tokens + profile in `data_complete=False` state
4. Frontend checks `data_complete`; if False, redirects to onboarding flow (not a dedicated page, implied from context)
5. Startup fills out profile (name, company, industry, funding stage, vision, team) and calls PATCH `/api/users/profile/startup/`
6. Startup fills mentor/coach availability (optional) and calls PATCH `/api/users/profile/` (name, sector, domain fields)
7. Backend updates UserProfile with data_complete=True
8. On next login, data_complete=True skips onboarding, redirects to dashboard

**DB state changes:**
- UserProfile.data_complete: False → True
- UserProfile.name, company_name, role: populated
- Startup: record created/populated

---

### 5.2 Mentor Publishes Slots → Startup Selects → CEL Approves → Meet Link Generated

**Trigger:** Mentor wants to offer meeting availability.

**Steps:**
1. Mentor logs in, goes to Meetings page
2. Calls POST `/api/meetings/slots/` with start_time, end_time
3. Backend creates MeetingSlot(user=mentor, free=True, start_time=..., end_time=...)
4. Mentor can edit/delete slots on the UI
5. **Startup's turn:** Startup browses Mentors page, clicks on Mentor name
6. Calls GET `/api/meetings/user/<mentor_id>/meeting-slots/` (returns only free=True slots)
7. Startup selects 2–4 mentor slots (business logic in frontend; no enforcement in backend)
8. For each slot, Startup calls POST `/api/meetings/requests/` with requester=Startup, requested=Mentor, slot=<MeetingSlotID>
9. Backend creates MeetingRequest(requester=Startup, requested=Mentor, slot=..., status='pending', cel_approved=False)
10. **CEL approval:** CEL admin (Django admin user) navigates to Django admin, finds the pending requests, clicks to view
11. CEL admin clicks "Approve" button (custom admin action or form field edit) to set cel_approved=True
12. Signals or admin save hook triggers: sets status='accepted', slot.free=False, generates meet_link via create_google_meet_event()
13. Startup sees meeting in "Upcoming Meetings" (GET `/api/meetings/meetings/upcoming/`)

**DB state changes:**
- MeetingSlot: free=True → False
- MeetingRequest: status=pending → accepted, cel_approved=False → True, meet_link populated

**Notifications:** When request created, Notification added for Mentor. When CEL approves, Notification added for Startup.

---

### 5.3 Coach/Expert Meeting Flows

**Identical to Mentor flow** — Coach and Function Expert roles publish slots and receive requests the same way. The only distinction is role name (used for profile-display purposes).

---

### 5.4 Reverse Flow: CME (Coach/Mentor/Expert) Proposes Meeting Time to Startup

**Trigger:** Mentor wants to initiate a meeting with a Startup rather than waiting for the Startup to book.

**Steps:**
1. Mentor calls POST `/api/meetings/requests/` with requester=Mentor, requested=Startup, slot=null, slot_start_time=..., slot_end_time=...
2. Backend logic in perform_create(): if slot is null, creates a new MeetingSlot for Mentor at that time (or finds an existing free one)
3. Creates MeetingRequest with cel_approved=True (no CEL approval needed for CME-initiated meetings)
4. Startup sees the request in "Pending Meetings" and can accept/reject via PATCH `/api/meetings/requests/<id>/` with status='accepted'/'rejected'
5. On accept, meet_link is auto-generated, Notification sent to Mentor

**DB state:** No CEL approval needed, flow is immediate.

---

### 5.5 Startup-to-Alumni Connection Request (Approval Chain)

**Trigger:** Startup wants to connect with an Alumni to get guidance.

**Steps:**
1. Startup calls POST `/api/users/connections/send/` with to_user=Alumni_username
2. Backend checks: Alumni must be in Startup.can_request() (Alumni is in CAN_REQUEST['Startup'])
3. Creates Connection(from_user=Startup, to_user=Alumni, approved=False, accepted=False)
4. Notification sent to Alumni: "Startup X wants to connect"
5. **Alumni's turn:** Alumni sees connection request in Connections page
6. **CEL approval (optional path):** If CEL approval is enforced (currently in models but not in views), CEL admin must first approve (set approved=True)
7. Alumni calls POST `/api/users/connections/accept/` (or PATCH in some implementations)
8. Connection(accepted=True) — now the connection is live, both can see each other

**Current code note:** No explicit CEL approval API for connections; the `approved` field exists in the model but is only set in Django admin. Frontend does not enforce a CEL-approval step.

---

### 5.6 Form Distribution & Submission & Admin Review

**Trigger:** CEL admin creates a form with questions and assigns it to specific roles.

**Steps:**
1. **CEL admin in Django admin:** Creates Form, adds SubjectiveQuestions, ScoringQuestions, FileUploadQuestions, PreferenceQuestions with Preferences
2. Sets Form.available_to = [Startup role, Mentor role, etc.] (M2M filter_horizontal in admin)
3. Saves form
4. **Startup/Mentor logs in:** Calls GET `/api/forms/list/` — returns only unanswered forms (filters out forms they've already answered)
5. Clicks form, frontend calls GET `/api/forms/<id>/questions/` — returns all questions grouped by type
6. User fills out the form:
   - Subjective: text input
   - Scoring: numeric 1-10
   - FileUpload: Google Drive link
   - Preference: drag-and-drop ranking
7. Calls POST `/api/forms/<id>/answers/` with all answers grouped by type
8. Backend creates Answer(form=..., answered_by=user), then creates SubjectiveAns, ScoreAns, FileAns, PreferenceAns* records
9. Form is now marked as answered; user no longer sees it in GET `/api/forms/list/`
10. **CEL admin review:** Goes to Django admin Answer list, filters by form, opens an answer
11. Admin can view all responses, see subjective answers with original text (read-only for CEL admin unless is_superuser), and export via import_export action
12. **DVM admin (superuser):** Can edit subjective answers inline for corrections/notes

**Scoring/Grading note:** Forms don't auto-calculate scores. Admin must manually review scoring answers and compute summary scores offline (or add custom admin action).

---

### 5.7 Admin Broadcast Announcement to Specific Roles

**Trigger:** CEL admin wants to notify Startups about Demo Day.

**Steps:**
1. CEL admin goes to Django admin Announcement section
2. Fills form: roles (multi-select checkboxes), message, optional attachment
3. Saves announcement
4. Announcement.roles stored as comma-separated string: "Startup,Mentor,Coach"
5. **No automatic notification created yet** — the system stores announcement but does not push it to users automatically
6. Alternative: CEL admin manually creates Notification records for each user (or via custom manage.py command/signal)
7. When user calls GET `/api/staff/notifications/`, they see their notifications (not announcements directly)

**Current gap:** Announcements are not automatically broadcast via Notifications. To be fully functional, a signal or cron job should listen for new Announcements and create Notification records for users in the target roles.

---

### 5.8 Notification Lifecycle

**Notification creation triggers:**
- Connection request sent → Notification("Connection request from X")
- Connection accepted → Notification("Connection with X approved")
- Meeting request received → Notification("Meeting request from X")
- Meeting accepted → Notification("Your meeting with X was approved")
- (Announcements — currently manual or incomplete)

**User view:**
1. GET `/api/staff/notifications/` returns list + unread_count
2. Frontend displays notifications in a dropdown or page
3. User marks as read (currently no PATCH endpoint; read field is managed in admin only)
4. Unread notifications trigger a badge or alert in UI

---

### 5.9 File Upload Flow (Firebase Storage)

**Trigger:** User uploads resume/pitch deck in profile, or submits form with file answers.

**Steps:**
1. Frontend detects file input (in profile edit or file-upload-question component)
2. Reads file from browser
3. Calls Firebase Storage `uploadBytes(ref(storage, path), file)` to upload directly to Firebase bucket
4. Firebase returns download URL
5. Frontend stores URL in form state
6. On PATCH `/api/users/profile/` or POST `/api/forms/answers/`, sends URL string (not the file binary)
7. Backend stores URLField

**Credentials needed:** `VITE_FIREBASE_*` env vars in frontend/.env (apiKey, authDomain, projectId, storageBucket, messagingSenderId, appId).

---

### 5.10 Login Flows

**Username/Password:**
1. User enters username + password on Login page
2. Frontend calls POST `/api/users/login/username/`
3. Backend authenticates via Django auth, fetches UserProfile + Startup (if Startup role)
4. Returns JWT tokens + user profile
5. Frontend stores in localStorage: userData (full profile + tokens), lastSessionCall (timestamp), tokens (jwt)
6. Redirects to /dashboard
7. App.jsx checks lastSessionCall on load; if > 3 hours old, refreshes token

**Google OAuth:**
1. User clicks "Sign in with Google"
2. Google login popup (from @react-oauth/google)
3. Frontend calls POST `/api/users/login/google/` with access_token
4. Backend verifies token with Google API, looks up user by email
5. If new user: creates User + UserProfile(role='Guest - Tier 2', data_complete=False)
6. Returns tokens + profile
7. Frontend checks data_complete; if False, implies onboarding needed (though no explicit redirect)
8. If data_complete=False and role!='Guest - Tier 2', user stays on frontend but can't access restricted routes
9. Guest - Tier 2 navigates to /dashboard/meetings only

**Token Refresh:**
1. App.jsx on mount: checks localStorage.lastSessionCall
2. If > 3 hours old (10800000 ms), calls POST `/api/users/token/refresh/` with refresh token
3. Backend returns new access token
4. Frontend updates localStorage.tokens.access + localStorage.lastSessionCall
5. Sets up interval to refresh again in 3 hours (or after 3-hour timeout from last session call)

---

### 5.11 Search & Discovery

**Startup Browse Other Startups:**
1. Calls GET `/api/users/startup_list/` (respects CAN_VIEW permissions)
2. Returns filtered list based on logged-in user's role
3. Example: Mentor can see all Startups; Guest - Tier 1 can see all Startups; Community can see all Startups, etc.

**Search by Name/Username:**
1. Calls GET `/api/users/search/?username=...&role=...`
2. Returns UserProfile(s) matching filters

---

## 6. Permissions Matrix

| Role | Book Mentor Call | Publish Slots | Accept Meeting | Approve Connections | Broadcast Announcement | Submit Forms | View All Startups | View Mentors | See Own Profile Edit | See Home/Dashboard |
|------|---|---|---|---|---|---|---|---|---|---|
| Startup | ✓ | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mentor | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Coach | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Function Expert | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Angel | partial | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Consultant | — | — | ✓ | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Alumni | — | — | — | — | — | — | ✓ | — | ✓ | ✓ |
| Partner - Company | — | partial | partial | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Partner - Individual | — | partial | partial | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Community | — | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Guest - Tier 1 | — | — | — | — | — | — | ✓ | — | ✓ | — |
| Guest - Tier 2 | — | — | — | — | — | — | — | — | — | — |
| CEL Admin | — | — | ✓ (approve) | ✓ | ✓ | view/grade | ✓ | ✓ | ✓ | ✓ |
| DVM Admin | ✓ (full) | ✓ (full) | ✓ (full) | ✓ | ✓ | create/edit/export | ✓ | ✓ | ✓ | ✓ |

**Notes:**
- "—" = cannot do
- "✓" = can do
- "partial" = limited context (e.g., Angels can publish slots but choose; Partners can accept meetings they receive)
- "view/grade" = CEL Admin can view answers in admin but not edit (unless superuser)
- Guest - Tier 2 redirected to /dashboard/meetings only; cannot see Home, Experts, Mentors, Coaches, Connections, Forms

---

## 7. Forms System (Deep Dive)

### Question Types

**SubjectiveQuestion:**
- `type`: Single Line | Short | Long (validation disabled in views, all treated as Long)
- Answer stored in SubjectiveAns.answer (TextField)
- No length enforcement in current code

**ScoringQuestion:**
- Answer: IntegerField, validated 1–10
- ScoreAns.answer

**FileUploadQuestion:**
- Answer: URLField (expects Google Drive link or Firebase URL)
- FileAns.answer

**PreferenceQuestion:**
- Contains multiple Preference options (e.g., ["B2B SaaS", "DeepTech", "HealthTech"])
- User ranks preferences by position (1, 2, 3...)
- Stored as PreferenceAnsMain (container) + PreferenceAns (one row per ranked preference)
- Position must be valid (1 to num_preferences)

### Answer Structure

An Answer record is a parent container. Depending on form composition:
- Answer.form → Form
- Answer.answered_by → UserProfile
- Answer → SubjectiveAns (multiple)
- Answer → ScoreAns (multiple)
- Answer → FileAns (multiple)
- Answer → PreferenceAnsMain (multiple) → PreferenceAns (multiple)

### Form Workflow in Code

1. **Admin creates form in Django admin:**
   ```
   Form "Pitch Evaluation"
   ├─ SubjectiveQuestion: "Tell us about your product" (type=Long)
   ├─ ScoringQuestion: "Rate your market opportunity" (1-10)
   ├─ FileUploadQuestion: "Upload your pitch deck"
   ├─ PreferenceQuestion: "Rank these verticals" 
   │  ├─ Preference: "B2B SaaS"
   │  ├─ Preference: "DeepTech"
   │  └─ Preference: "HealthTech"
   └─ available_to: [Startup, Mentor]
   ```

2. **Startup fetches form:**
   ```
   GET /api/forms/list/ → [{ id: 1, form_name: "Pitch Evaluation" }]
   GET /api/forms/1/questions/ → full structure above
   ```

3. **Startup submits:**
   ```
   POST /api/forms/1/answers/
   {
     "subjective_questions": [
       { "id": Q1_id, "ans": "We build AI for X" }
     ],
     "file_upload_questions": [
       { "id": Q3_id, "ans": "https://firebaseUrl/..." }
     ],
     "scoring_questions": [
       { "id": Q2_id, "ans": 8 }
     ],
     "preference_questions": [
       {
         "id": Q4_id,
         "preferences": [
           { "id": Pref_B2B, "position": 1 },
           { "id": Pref_DeepTech, "position": 2 },
           { "id": Pref_HealthTech, "position": 3 }
         ]
       }
     ]
   }
   ```

4. **Backend processing:**
   - Creates Answer(form=1, answered_by=Startup)
   - For each subjective_question: creates SubjectiveAns(under_answer=Answer, subjective_question=..., answer="...")
   - For each file_upload_question: creates FileAns(...)
   - For each scoring_question: validates 1-10, creates ScoreAns(...)
   - For each preference_question: creates PreferenceAnsMain(...), then for each ranked pref: creates PreferenceAns(..., position=1/2/3)

5. **Admin review:**
   - GET /api/forms/list/ no longer returns form (filtered where answered_by != user)
   - In Django admin Answer list: searches by form name or user username
   - Opens Answer, views all SubjectiveAns (read-only for CEL staff), ScoreAns, FileAns, PreferenceAns in nested inlines
   - Can export via django-import-export action → CSV with all answers

### Admin Permissions

- **CEL Admin (is_staff=True):**
  - Can view Form, Answer
  - Cannot add/change/delete Form
  - Cannot add/delete Answer
  - In Answer inline, can view subjective answers but not edit (readonly via formfield_for_dbfield logic)
  - Cannot edit ScoreAns, FileAns, PreferenceAns

- **DVM Admin (is_superuser=True):**
  - Full access to Form, Answer
  - Can edit all inline answers
  - Can add/delete/change
  - Export available

---

## 8. Meeting System (Deep Dive)

### Slot Publishing (CME Availability)

**MeetingSlot fields:**
- `user` → Mentor/Coach/Expert
- `start_time`, `end_time` → UTC DateTimeField
- `free` → Boolean, True if no meeting request is using it

**Publishing process:**
1. CME calls POST `/api/meetings/slots/` with start_time, end_time
2. Backend creates MeetingSlot(user=CME, free=True, ...)
3. CME can list their slots: GET `/api/meetings/slots/` (filtered by request.user.profile)
4. CME can update (PATCH `/api/meetings/slots/<id>/`) or delete (DELETE)

### Slot Booking by Startup

**Get available slots:**
1. Startup browses Mentors page, selects a mentor
2. Calls GET `/api/meetings/user/<mentor_id>/meeting-slots/` (no auth required)
3. Returns only MeetingSlot where user=mentor AND free=True
4. Frontend displays slots as selectable options

**Book slots:**
1. Startup selects 2–4 slots (enforced on frontend only; no backend validation)
2. For each slot, calls POST `/api/meetings/requests/`:
   ```json
   {
     "requested": mentor_profile_id,
     "slot": slot_id,
     "slot_start_time": null,
     "slot_end_time": null
   }
   ```
3. Backend creates MeetingRequest(requester=Startup, requested=Mentor, slot=..., status='pending', cel_approved=False)
4. Validation: no duplicate requests for same slot to same mentor

### Request Approval Chain

**Pending state:**
- Startup makes request → status='pending'
- Mentor sees in GET `/api/meetings/all_meetings/` (returns requests received by mentor)
- CEL admin goes to Django admin, finds request, views details

**CEL approval:**
- In Django admin MeetingRequest admin, toggles `cel_approved=False → True`
- On save: signal or custom save() logic sets status='accepted', slot.free=False, meet_link generated
- Startup sees in GET `/api/meetings/meetings/upcoming/` (only status='accepted' + cel_approved=True + slot_start_time >= now)

**Mentor acceptance (alternative if CEL approval skipped):**
- Mentor can call PATCH `/api/meetings/requests/<id>/` with status='accepted'
- Same logic: slot.free=False, meet_link generated
- But only if cel_approved=True (or cel_approved auto-set on mentor accept)

**Current code flow in MeetingRequest.save():**
```python
if self.pk is not None and self.requester.role == 'Startup':
    old_approval = MeetingRequest.objects.get(pk=self.pk).cel_approved
    if old_approval != True and self.cel_approved == True:
        self.status = 'accepted'
        self.slot.free = False
        self.slot.save()
```
This means: when CEL admin sets cel_approved=True for a Startup request, status auto-becomes 'accepted' and slot is marked taken.

### Reverse Flow: CME Proposes Time

1. CME calls POST `/api/meetings/requests/`:
   ```json
   {
     "requested": startup_profile_id,
     "slot": null,
     "slot_start_time": "2024-06-05T10:00:00Z",
     "slot_end_time": "2024-06-05T11:00:00Z"
   }
   ```
2. Backend perform_create() logic:
   - If slot is null: checks for clashing meetings or free slots for CME
   - If free slot exists: reuses it
   - Otherwise: creates new MeetingSlot(user=CME, free=True, start_time=..., end_time=...)
   - Creates MeetingRequest with cel_approved=True (skips CEL approval)
3. Startup sees request in pending meetings, calls PATCH to accept/reject
4. On accept, meet_link generated
5. No CEL bottleneck for CME-initiated meetings

### Meeting Views & Filtering

- `GET /api/meetings/meetings/upcoming/` → status='accepted' AND cel_approved=True AND slot_start_time >= now
- `GET /api/meetings/meetings/past/` → status='accepted' AND slot_end_time < now
- `GET /api/meetings/meetings/pending/` → status='pending' AND slot_start_time >= now (unresponded requests)
- `GET /api/meetings/all_meetings/` → all MeetingRequests (sent + received)
- `GET /api/meetings/requested_meetings/` → requests sent by user

### Meet Link Generation

**When:** On CEL approval (Startup request) or on mentor accept (CME request).

**How:** `create_google_meet_event()` utility function (imported from .utils) generates a Google Meet link.

**Implementation hint:** Likely uses Google Calendar API to create event and extract meet link. Requires Google service account credentials.

**URL stored in:** MeetingRequest.meet_link

### Post-Meeting Fields

- `recording` (URLField) → admin fills in after recording posted
- `minutes_of_meet` (TextField) → admin or meeting owner notes key points
- `requester_feedback_score` (1-10) → either party can set post-meeting
- `requested_feedback_score` (1-10) → either party can set post-meeting

**No enforcement:** Users are not prompted in the UI to fill these; likely manual in future or admin-only.

### BookingPortal Control

- `BookingPortal.is_active` (Boolean) → gates whether startup UI allows booking
- `GET /api/meetings/portal_state/` → returns { is_active: true/false }
- Frontend can use this to show "Booking Closed" banner or disable buttons
- No validation in request creation; portal_state is informational only

---

## 9. Admin-Only Features & Customizations

### Django Admin Customizations

All admin panels require `is_staff=True` or `is_superuser=True`. Route: `/api/admin/`.

#### Users Admin
- **UserProfileAdmin:** list_display = (user, role, profile_logo, google_email, google_user_id)
  - list_filter by role
  - search_fields by name
  - Readonly for staff (non-superuser): user, profile_logo, google_email, google_user_id
  - Inlines: ToConnectionInline, FromConnectionInline (view connections)
  - Only superuser can add/change/delete UserProfile

- **UserAdmin:** (Django User model, customized)
  - Prevents non-superuser staff from creating/modifying superusers
  - Readonly is_superuser field for staff

- **ConnectionAdmin:**
  - list_display = (from_user, to_user, approved, accepted)
  - list_editable = (approved, accepted) — CEL admin can toggle these inline
  - No API endpoint for this; only Django admin

- **InterestCaptureAdmin:**
  - list_display = (from_startup, get_target, interest_captured)
  - list_filter = (interest_captured)
  - Shows which startup interested in which consultant/resource

- **StartupAdmin:** (basic, no custom)
  - list_display auto-generated

#### Forms Admin
- **FormAdmin:** (uses NestedModelAdmin for complex inlines)
  - Inlines: SubjectiveQuesAdmin, ScoreQuesAdmin, FileQuesAdmin, PreferenceQuesAdmin (which contains PreferenceAdmin)
  - list_display = (form_name, answered_by [computed as len(answers)])
  - search_fields = (form_name)
  - filter_horizontal = (available_to) — multi-select which UserProfile roles get form
  - has_view_permission restricted to superuser or is_staff

- **AnswerAdmin:** (uses NestedModelAdmin, ImportExportModelAdmin, ExportActionMixin)
  - Inlines: SubjAnsAdmin, ScoreAnsAdmin, FileAnsAdmin, PreferenceMainAnsAdmin
  - **SubjAnsAdmin:** readonly for CEL (staff), editable for superuser
    - formfield_for_dbfield() renders Textarea with 'readonly' CSS for staff
  - **ScoreAnsAdmin, FileAnsAdmin, PreferenceMainAnsAdmin:** all readonly for staff (via AnswerPermissions mixin)
  - **Export:** django-import-export action (AnswerResource) → exports all answers to CSV
  - resource_class = AnswerResource (defined in forms/resources.py, not shown but standard)
  - has_view_permission: only staff or superuser
  - has_add_permission: only superuser
  - has_delete_permission: only superuser

#### Meetings Admin
- **MeetingSlotAdmin:**
  - list_display = (user, start_time, end_time)
  - list_filter = (user)

- **MeetingRequestAdmin:** (uses NestedModelAdmin, ImportExportModelAdmin, ExportActionMixin)
  - list_display = (requester, requested, slot, status)
  - list_filter = (status)
  - Export via django-import-export

- **GlobalEventAdmin:**
  - list_display = (name, slot_start_time, slot_end_time)

- **BookingPortal:** (basic, no custom)
  - Toggle is_active to open/close booking

#### Staff Admin
- **AnnouncementAdmin:**
  - form = AnnouncementAdminForm (custom Django form, not shown)
  - Allows CEL admin to select multiple roles via checkboxes
  - on save: roles converted to comma-separated string
  - has_add_permission, has_change_permission, has_delete_permission restricted to staff or superuser

- **NotificationAdmin:** (basic, no custom)

### Import/Export

- **forms/resources.py:** AnswerResource (not shown in detail)
- **meetings/resources.py:** MeetingRequestResource
- Both integrate with django-import-export ExportActionMixin
- Callable as admin actions: "Export selected [Answers|Requests]"

### Django Admin Signals/Hooks

- **UserProfile.save():** (no custom save logic visible)
- **MeetingRequest.save():** cel_approved → status + meet_link generation
- **Connection.save():** clean() validation

---

## 10. Integrations

### Google OAuth

**Flow:**
1. Frontend uses `@react-oauth/google` GoogleOAuthProvider + useGoogleLogin hook
2. User clicks "Sign In with Google" → Google popup
3. On success, frontend gets access_token
4. Calls POST `/api/users/login/google/` with access_token
5. Backend calls Google API (https://www.googleapis.com/oauth2/v1/userinfo) with Authorization header
6. Extracts user email, picture, google_user_id (sub)
7. Finds or creates User + UserProfile
8. Returns JWT tokens + profile

**Credentials needed:**
- `VITE_GOOGLE_OAUTH_CLIENT_ID` in frontend/.env
- Set up in Google Cloud Console: OAuth consent screen + credentials (Web application type)

**Required scopes:** https://www.googleapis.com/oauth2/v1/userinfo (openid, email, profile implicit in OAuth 2.0)

### Firebase Storage

**Flow:**
1. User selects file in form or profile edit
2. Frontend imports firebaseConfig (defined in `components/.../FileUpload/firebaseConfig.js`)
3. Calls getStorage(), then uploadBytes(ref(storage, path), file)
4. Firebase returns download URL
5. Frontend submits URL as string (not binary file)

**Credentials needed:**
- `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_STORAGE_BUCKET`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID` in frontend/.env

**Usage:**
- Profile photo/logo uploads
- Pitch deck, resume uploads
- Form file-upload-question answers

### AWS SES (Email)

**Configured in settings.py:**
```python
EMAIL_BACKEND = 'django_ses.SESBackend'  # if AWS_ACCESS_KEY_ID set
AWS_SES_REGION_NAME = os.getenv('AWS_REGION_NAME', 'ap-south-1')
AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'
```

**Credentials needed:**
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` in backend/.env
- `DEFAULT_FROM_EMAIL` (verified sender)
- AWS IAM user with SES permissions

**Triggers (future):**
- Password reset email (if enabled)
- Connection approval notification (if enabled)
- Resource/program emails (forms/views.py has send_resource_email view, partially implemented)

**Current state:** Email functionality is set up but minimally used. No automatic password reset or connection emails in code.

### Google Meet (Meeting Links)

**Integration:** meetings/utils.py `create_google_meet_event()` function
- Likely uses Google Calendar API to create an event
- Extracts the generated Google Meet link
- Stores in MeetingRequest.meet_link

**Credentials needed:** Google service account JSON (not shown, but required in backend)

### Sentry (Error Tracking)

**Configured in settings.py:**
```python
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    ...
)
```

**Triggers:**
- Unhandled exceptions + errors logged to Sentry dashboard
- `/api/sentry-debug/` endpoint triggers test error (intentional 1/0 division)

**Credentials needed:** SENTRY_DSN env var

### Google Analytics (GA4)

**Frontend:**
- ReactGA library initialized with `GA_MEASUREMENT_ID` from frontend/.env
- Tracks pageviews: `ReactGA.send({ hitType: "pageview", page: ..., title: ... })`

**Credentials needed:** VITE_GA_MEASUREMENT_ID env var

**Scope:** Passive tracking, no feature gating.

---

## 11. Known Issues & Incomplete Features

### Partially Implemented / Buggy

1. **Password Reset Email**
   - AWS SES is configured but no password reset flow exists
   - Users cannot reset forgotten passwords via email
   - Only manual admin password reset or Google OAuth signup

2. **Connection Approval Flow**
   - `Connection.approved` field exists but is only set in Django admin, not via API
   - No PATCH endpoint to let CEL admin approve connections programmatically
   - Frontend shows pending connections but no "approve" button (admin-only)
   - Potentially confusing: `accepted` (recipient agrees) vs `approved` (CEL vets), both tracked

3. **Announcement Broadcasting**
   - Announcements created in Django admin but no automatic Notification creation
   - No signal to convert Announcement → Notification for target roles
   - To make announcements work, either:
     - Add a Django signal: on Announcement.save(), create Notification for each user in target roles
     - Or add a custom admin action "Send to users"

4. **Form Validation**
   - SubjectiveQuestion type (Single Line / Short / Long) is not enforced on submit
   - All treated as Long text
   - Frontend could add client-side validation but backend does not

5. **Subjective Answer Editing by DVM**
   - Admin formfield_for_dbfield() makes answer readonly for CEL staff via CSS 'readonly' attribute
   - DVM (superuser) can edit but FormAdmin.get_fields() may not expose all fields correctly
   - Best practice: manually test DVM answer edits

6. **Preference Question Position Validation**
   - Backend validates position 1..num_preferences, but no frontend UX for drag-drop
   - Form submission expects positions in request; frontend must ensure valid positions

7. **Meeting Link Generation**
   - Google Meet link created on CEL approval or mentor accept
   - Assumes Google service account is available and working
   - No fallback if Google API fails (exception not caught gracefully)
   - If meeting link is empty after accept, user can't join

8. **No Recording/Minutes/Feedback Collection**
   - Fields exist in MeetingRequest (recording, minutes_of_meet, *_feedback_score)
   - No UI to submit post-meeting data
   - Admin must manually fill in Django admin

9. **Token Refresh Logic in App.jsx**
   - Complex 3-hour timeout logic with potential race conditions
   - If user has multiple tabs open, each may try to refresh independently
   - Could lead to orphaned interval timers

10. **Startup Onboarding Check**
    - data_complete flag checked on login but no UI redirection if incomplete
    - Frontend must infer onboarding status and route manually
    - No dedicated onboarding flow; user can skip

11. **Guest - Tier 1 vs Tier 2 Distinction**
    - Guest - Tier 1: restricted routes (no Home, Experts, Mentors, Coaches, Connections, Forms)
    - Guest - Tier 2: redirected to Meetings only
    - Why the distinction? Code suggests Tier 2 is lower (e.g., quick signup), Tier 1 higher (e.g., invited), but not clearly documented

12. **No RLS (Row-Level Security) Enforcement**
    - CAN_VIEW, CAN_CREATE, CAN_REQUEST permissions checked in view layer
    - If backend is accessed directly (bypassing views), no DB-level enforcement
    - A determined attacker could enumerate all startups regardless of role

13. **Incomplete Meeting Slot Auto-Creation**
    - Mentor initial POST `/slots/` creates slot
    - When startup books and slot is free, code saves slot but doesn't update free flag until mentor accepts
    - Between booking request and acceptance, slot.free is still True; other startups might try to book same slot

14. **No Conflict Resolution for Double-Booking**
    - If two startups request same slot before mentor accepts first, both requests are created
    - Only one can be accepted (slot.free → False)
    - Second startup's request left hanging; no error feedback

15. **Admin Permissions Not Fully Role-Based**
    - Django admin uses is_staff and is_superuser, not UserProfile.role
    - Assumption: admins are also Django staff users
    - If CEL Admin role needs to exist without is_staff, need custom auth backend

16. **No Form Scoring/Grading Automation**
    - Forms store scoring answers but no auto-calculation of totals or weighted scores
    - Admin must manually compute offline

17. **Interest Capture Direction**
    - InterestCapture allows startup → consultant or startup → resource (partner)
    - Cannot model resource-to-startup interest (e.g., partner wants to sponsor specific startup)

18. **No Email Template Rendering for Resource Emails**
    - forms/views.py has send_resource_email() with hardcoded email templates
    - Only works for specific partner names (Phionike123, MongoDB, GitHub, etc.)
    - Not scalable; requires code changes to add new partner benefits

19. **No Pagination on Meetings Endpoints**
    - GET /api/meetings/meetings/upcoming/ returns all, no limit
    - Large cohorts with hundreds of meetings could slow API

20. **Meeting Request Type Property Unused**
    - MeetingRequest.type property returns requester.role + "/" + requested.role
    - Not used anywhere in views; computed but never consumed

21. **Startup Role Not Enforced on Login**
    - UsernameLogin assumes all users are Startup role
    - If a Mentor tries username login, code will fail trying to fetch user.profile.startup
    - Only Google OAuth handles non-Startup roles gracefully

---

## Appendix: Configuration Checklist

| Feature | Env Var | Backend | Frontend | Default |
|---------|---------|---------|----------|---------|
| Google OAuth | `VITE_GOOGLE_OAUTH_CLIENT_ID` | No | Yes | (blank) |
| Firebase | `VITE_FIREBASE_*` | No | Yes | (blank) |
| AWS SES | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DEFAULT_FROM_EMAIL` | Yes | No | (blank) |
| Google Calendar API | (in service account JSON) | Yes | No | (blank) |
| Sentry | `SENTRY_DSN` | Yes | No | (blank) |
| GA4 | `VITE_GA_MEASUREMENT_ID` | No | Yes | (blank) |
| Database | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Yes | No | (required) |
| Django Secret | `DJANGO_SECRET_KEY` | Yes | No | (required) |
| CORS Origins | `DJANGO_CORS_ALLOWED_ORIGINS` | Yes | No | (localhost defaults) |
| JWT Lifetime | `ACCESS_TOKEN_LIFETIME`, `REFRESH_TOKEN_LIFETIME` | Yes (settings.py hardcoded as timedelta) | No | (3600s, 604800s) |

---

**End of Functionality Overview**

This document is complete and exhaustive as of April 2026. For questions or clarifications, refer to the codebase at `/Users/aryanjain/Downloads/conquest-portal/`.

