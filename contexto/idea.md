# Project Idea and Requirements

## Hypothesis
Freelancers, especially in high-demand fields like UX/UI, need personalized and timely job vacancy alerts to save time and avoid missing opportunities. A Telegram bot that delivers push notifications, filtered by a user's specific profile and preferred frequency, can solve this problem effectively.

## Problem
The manual search for freelance or contract roles across multiple platforms (like LinkedIn, Indeed, etc.) is inefficient, time-consuming, and often results in a high volume of irrelevant vacancies. This "noise" makes it difficult for freelancers to identify valuable leads quickly.

## Solution Overview
We will build a Telegram bot that automates the job search and delivery process. The workflow is as follows:
1.  **Profile Setup**: Users interact with the bot using commands like `/perfil` to set up their professional profile, defining specific keywords for the jobs they are seeking (e.g., "ux/ui", "design system", "python developer").
2.  **Unified Data Storage**: The user's profile (Telegram ID, email, phone number, keywords, location preferences) is stored in **Google Sheets**, providing a simple and visual single source of truth for all application data.
3.  **Automated Scraping**: A scheduled backend Python service calls the **JobSpy API** ([rainmanjam/jobspy-api](https://github.com/rainmanjam/jobspy-api)) to fetch job postings from multiple sources (LinkedIn, Indeed, ZipRecruiter, etc.), filtering for "freelance" and "contract" positions. The API returns structured JSON data.
4.  **Job Storage**: Scraped jobs are stored in **Google Sheets** alongside user profiles, enabling easy deduplication, tracking of which users have already received each job, and visual management.
5.  **AI-Powered Personalization**: A **LangChain agent** powered by **Gemini 2.5 Flash** analyzes each job posting against the user's profile (keywords, experience, location preferences, etc.) and generates a personalized copy message explaining why this job matches their profile.
6.  **Keyword Matching & Filtering**: The system queries Google Sheets to find jobs matching user keywords, and the LangChain agent ranks and filters the most relevant opportunities with personalized reasoning.
7.  **Personalized Notifications**: Curated job postings with personalized AI-generated messages are sent directly to users via Telegram, once or twice a day (e.g., "Hey Juan, here are 3 opportunities that match your ux/ui experience and remote preferences...").

---

## Functional Requirements (FR)
- **FR-01: User Profile Management**: The system must allow users, through Telegram commands, to create and update a profile with specific job-seeking keywords, location preferences, and experience level.
- **FR-02: Unified Data Persistence**: User data (Telegram ID, email, phone number, keywords, preferences) must be stored in **Google Sheets** as a single source of truth.
- **FR-03: API-Based Job Scraping**: The scraping engine must call the **JobSpy API** ([rainmanjam/jobspy-api](https://github.com/rainmanjam/jobspy-api)) to fetch job postings, filtering for roles explicitly marked as "freelance" or "contract".
- **FR-04: Job Data Storage & Deduplication**: Scraped job postings (JSON format) must be stored in **Google Sheets** with tracking of which users have already received each job (via `sent_to` field).
- **FR-05: AI-Powered Job Personalization**: A **LangChain agent** powered by **Gemini 2.5 Flash** must analyze each job against the user's profile and generate a personalized copy explaining the match (e.g., "This matches your ux/ui skills and remote preference").
- **FR-06: Intelligent Job Matching**: The system must query Google Sheets to filter and rank job postings based on user keywords and preferences, leveraging the LangChain agent for semantic understanding.
- **FR-07: Scheduled Notifications**: The system must deliver personalized job alerts to users via Telegram on a schedule of 1 to 2 times per day, including the AI-generated personalized message for each opportunity.

## Non-Functional Requirements (NFR)
- **NFR-01: Scheduling Precision**: The automated scraping and notification tasks should execute reliably at their scheduled intervals.
- **NFR-02: Resilience (Anti-ban)**: The JobSpy API handles User-Agent rotation, proxies, and rate limiting to avoid IP blocks and bans.
- **NFR-03: Scalability**: The architecture must support a growing number of users. Firebase Firestore provides automatic scaling, and the JobSpy API is production-ready.
- **NFR-04: Performance**: Job matching and AI personalization should complete within reasonable timeframes (< 30 seconds per batch).

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Bot Framework | python-telegram-bot | Handle Telegram commands and messaging |
| Unified Database | Firebase Firestore | Store users, keywords, preferences, and jobs (JSON) |
| Job Scraping API | [rainmanjam/jobspy-api](https://github.com/rainmanjam/jobspy-api) | Fetch jobs from LinkedIn, Indeed, ZipRecruiter |
| AI Agent | LangChain + Gemini 2.5 Flash | Generate personalized job matching messages |
| Backend Framework | Python + APScheduler | Core backend service with task scheduling |
| Language & Env | Python 3.10+, uv | Language and package/environment management |

## Success Metrics
- High weekly active user rate, indicating that users find the service valuable enough to keep using it.
- Positive qualitative feedback from users confirming that the bot saves them time and delivers relevant job opportunities.
- High engagement rate on sent job alerts (users clicking links, applying to jobs).
