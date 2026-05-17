"""
Smoke-test: run the full workflow with a sample resume + job description
and print every section of output.
"""
import sys
sys.path.insert(0, ".")

from workflow.runner import run_workflow

SAMPLE_RESUME = """
Jane Smith
jane.smith@email.com | (555) 123-4567 | linkedin.com/in/janesmith | github.com/janesmith
San Francisco, CA

PROFESSIONAL SUMMARY
Software engineer with 6 years of experience building scalable backend systems and data pipelines.
Strong background in Python, distributed systems, and cloud infrastructure.

SKILLS
Python, Go, SQL, PostgreSQL, Redis, Kafka, AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes,
Terraform, CI/CD, REST APIs, gRPC, Git, Linux

EXPERIENCE

Senior Software Engineer — DataFlow Inc., San Francisco, CA (Jan 2021 – Present)
- Designed and implemented a real-time data ingestion pipeline processing 2.5 million events/day using Kafka and Python
- Reduced API response latency by 38% by introducing Redis caching layer across 4 microservices
- Led a team of 5 engineers to migrate legacy monolith to microservices architecture, cutting deployment time from 4 hours to 22 minutes
- Built internal Terraform modules adopted by 3 other engineering teams, saving ~120 engineer-hours per quarter

Software Engineer — CloudBase Corp., Austin, TX (Jun 2018 – Dec 2020)
- Developed RESTful APIs serving 50,000 daily active users using Python/Flask and PostgreSQL
- Automated nightly ETL jobs processing 800GB of raw data, reducing manual intervention by 90%
- Implemented monitoring dashboards in Grafana reducing mean time to detection (MTTD) from 45 min to 8 min
- Collaborated with data science team to deploy 3 ML models into production using Docker and AWS Lambda

EDUCATION
B.S. Computer Science — University of Texas at Austin, 2018 (GPA 3.7)

CERTIFICATIONS
AWS Certified Solutions Architect – Associate (2022)
""".strip()

SAMPLE_JD = """
Senior Backend Engineer — Streamline AI
San Francisco, CA (Hybrid) | Full-time

About Us
Streamline AI is building the operating system for legal operations teams. We process millions of
documents per month and help Fortune 500 legal teams work 10x faster.

What You'll Do
- Design and build high-throughput data pipelines to ingest and process legal documents at scale
- Own and evolve our microservices architecture across Python and Go services
- Improve system reliability and observability — we target 99.9% uptime
- Work closely with ML engineers to integrate LLM-based document processing features
- Mentor junior engineers and contribute to technical roadmap decisions

Requirements
- 5+ years of backend engineering experience
- Strong proficiency in Python (our primary language) and/or Go
- Experience with distributed systems and event streaming (Kafka, Kinesis, or similar)
- Proficiency with PostgreSQL and experience tuning queries at scale
- AWS cloud infrastructure experience (we run on AWS)
- Experience with containerization (Docker, Kubernetes)

Preferred
- Experience in a fast-growing startup environment
- Familiarity with LLM APIs or AI/ML model deployment
- Infrastructure-as-code experience (Terraform, CDK)
- Experience with legal tech or document processing

What We Offer
- Competitive salary: $180,000–$220,000
- Equity package
- Fully covered health/dental/vision
""".strip()


def main():
    print("Running Resume Tailor workflow...\n")
    result = run_workflow(SAMPLE_RESUME, SAMPLE_JD)

    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return

    print("=" * 70)
    print("GAP ANALYSIS")
    print("=" * 70)
    gap = result["gap_analysis"]
    print(f"Fit Score: {gap.overall_fit_score}/10")
    print(f"\nStrong Matches: {', '.join(m.skill for m in gap.strong_matches)}")
    print(f"Partial Matches: {', '.join(m.skill for m in gap.partial_matches)}")
    print(f"Gaps: {', '.join(gap.gaps) or 'None'}")
    print(f"\nStrategy: {gap.tailoring_strategy}")

    print("\n" + "=" * 70)
    print("TAILORED RESUME (first 800 chars)")
    print("=" * 70)
    tailored = result["tailored_resume"]
    print(tailored.resume_text[:800])
    print("\n--- Key changes ---")
    for c in tailored.key_changes_made:
        print(f"  • {c}")

    print("\n" + "=" * 70)
    print("COVER LETTER (first 600 chars)")
    print("=" * 70)
    letter = result["cover_letter"]
    print(letter.cover_letter_text[:600])

    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)
    v = result["validation_result"]
    retry_count = result["retry_count"]
    status = "PASS" if v.is_valid else "FAIL"
    print(f"Status: {status} | Severity: {v.severity} | Retries: {retry_count}")
    if v.issues:
        print("Issues:")
        for i in v.issues:
            print(f"  - {i}")
    if v.hallucinated_skills:
        print(f"Hallucinated skills: {v.hallucinated_skills}")
    if v.hallucinated_metrics:
        print(f"Changed metrics: {v.hallucinated_metrics}")
    if not v.issues:
        print("No hallucinations detected.")


if __name__ == "__main__":
    main()
