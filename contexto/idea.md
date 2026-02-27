# Project Idea and Requirements

## Hypothesis
Freelancers, especially in high-demand fields like UX/UI, need quick and personalized access to relevant job vacancies to save time and avoid missing opportunities. A Telegram bot that delivers on-demand job searches, filtered by a user's specific profile and AI-personalized recommendations, can solve this problem effectively.

## Problem
The manual search for freelance or contract roles across multiple platforms (like LinkedIn, Indeed, etc.) is inefficient, time-consuming, and often results in a high volume of irrelevant vacancies. This "noise" makes it difficult for freelancers to identify valuable leads quickly.

## Solution Overview
We will build a Telegram bot that delivers on-demand, intelligently-curated job searches. The workflow is as follows:
1.  **Profile Setup**: Users interact with the bot using commands like `/perfil` to set up their professional profile, defining specific keywords for the jobs they are seeking (e.g., "ux/ui", "design system", "python developer", "remote", "contract") and their location.
2.  **Unified Data Storage**: The user's profile (Telegram ID, email, phone number, keywords, location preferences) is stored in **Google Sheets**, providing a simple and visual single source of truth for all user data.
3.  **Multi-Platform On-Demand Search**: When a user sends `/vacantes`, the Telegram bot immediately searches **all job platforms** (Indeed, LinkedIn, Glassdoor) via the **JobSpy API** ([rainmanjam/jobspy-api](https://github.com/rainmanjam/jobspy-api)). The bot intelligently sends the country parameter only to platforms that require it (Indeed, Glassdoor). Fresh job postings are collected in 2-5 seconds.
4.  **AI-Powered Intelligent Curation**: A **LangChain agent** powered by **Gemini 2.5 Flash** analyzes ALL job results (from multiple platforms), intelligently filters and prioritizes them by relevance to the user's profile (keywords, location, job type), and selects the top 3-5 best matches.
5.  **Personalized Results**: The curated job postings with AI-generated personalization messages are sent directly to users via Telegram in real-time (e.g., "Hey Juan, here are 3 opportunities that match your ux/ui experience and remote preferences...").

---

## Functional Requirements (FR)
- **FR-01: User Profile Management**: The system must allow users, through Telegram commands, to create and update a profile with specific job-seeking keywords, location preferences, and experience level (via `/perfil` command).
- **FR-02: Unified Data Persistence**: User data (Telegram ID, email, phone number, keywords, preferences) must be stored in **Google Sheets** as a single source of truth.
- **FR-03: On-Demand Job Search**: When a user sends `/vacantes`, the system must immediately call the **JobSpy API** ([rainmanjam/jobspy-api](https://github.com/rainmanjam/jobspy-api)) with the user's keywords to fetch fresh job postings from multiple sources (LinkedIn, Indeed, ZipRecruiter, etc.).
- **FR-04: AI-Powered Job Personalization**: A **LangChain agent** powered by **Gemini 2.5 Flash** must analyze each job against the user's profile and generate a personalized copy explaining the match (e.g., "This matches your ux/ui skills and remote preference").
- **FR-05: Instant Delivery**: Personalized job results with AI-generated messages must be sent to users via Telegram in real-time, immediately after the search completes.

## Non-Functional Requirements (NFR)
- **NFR-01: Response Time**: On-demand job search must complete within 10 seconds (JobSpy: 2-5s + Gemini: 1-2s + buffer).
- **NFR-02: Resilience (Anti-ban)**: The JobSpy API handles User-Agent rotation, proxies, and rate limiting to avoid IP blocks and bans. Rate limit: 100 requests/hour.
- **NFR-03: Scalability**: The architecture must support a growing number of concurrent users. Google Sheets is sufficient for MVP (< 10k users). Migration to Firebase/Supabase for larger scale.
- **NFR-04: Availability**: The bot should remain online 24/7 to accept user commands. JobSpy API is production-ready.

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Bot Framework | python-telegram-bot | Handle Telegram commands and messaging |
| Unified Database | Google Sheets | Store users, keywords, preferences (simple & visual) |
| Job Scraping API | [rainmanjam/jobspy-api](https://github.com/rainmanjam/jobspy-api) | Fetch jobs on-demand from LinkedIn, Indeed, ZipRecruiter |
| AI Agent | LangChain + Gemini 2.5 Flash | Generate personalized job matching messages |
| Backend | Python 3.10+ | Core backend service (no scheduler, event-driven) |
| Language & Env | Python 3.10+, uv | Language and package/environment management |

## Success Metrics
- High weekly active user rate, indicating that users find the service valuable enough to keep using it.
- Positive qualitative feedback from users confirming that the bot saves them time and delivers relevant job opportunities.
- High engagement rate on sent job alerts (users clicking links, applying to jobs).
