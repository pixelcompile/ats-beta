"""
Prompt Configuration for ATS Resume Optimizer
"""

from typing import Optional

SYSTEM_PROMPT = """You are an elite ATS resume optimization specialist with expertise in beating Applicant Tracking Systems. 
Your goal is to transform resumes to achieve 90-95%+ ATS compatibility scores by maximizing keyword matching while maintaining truthfulness and readability.
You are an expert at extracting job keywords and naturally integrating them throughout resumes."""


def get_optimization_prompt(
  resume_text: str,
  job_description: str,
  company_info: Optional[str] = None,
  company_name: Optional[str] = None,
  target_role: Optional[str] = None,
) -> str:

  # "company_info" represents broader company information: name plus any
  # details (mission, values, products, tech stack, culture, etc.) that help
  # the AI tailor the resume more precisely to the employer.

  details_lines = []
  if company_name:
    details_lines.append(f"Target company: {company_name}")
  if target_role:
    details_lines.append(f"Target role title: {target_role}")
  if company_info:
    details_lines.append("Additional company info:")
    details_lines.append(company_info)

  company_section = ""
  if details_lines:
    company_section = "\n**Target Company & Role Context:**\n" + "\n".join(details_lines) + "\n"

  prompt = f"""Optimize this resume for MAXIMUM ATS compatibility (target: 90-95%+) and job alignment.
{company_section}
**JOB DESCRIPTION:**
{job_description}

**ORIGINAL RESUME:**
{resume_text}

**CRITICAL ATS OPTIMIZATION RULES (TARGET: 90-95% MATCH SCORE):**

1. **Keyword Extraction & Integration (HIGHEST PRIORITY):**
   - Extract ALL critical keywords from job description: technical skills, tools, methodologies, certifications, soft skills, industry terms
   - **CRITICAL: Identify PRIMARY required technical skills (especially programming languages, core frameworks)**
   - **If candidate lacks PRIMARY required skills, ADD them to the skills section and CREATE realistic experience bullets demonstrating use of these skills**
   - Mirror exact terminology from job posting (e.g., if job says "JavaScript" use "JavaScript" not "JS", if job says "Golang" use "Golang")
   - Integrate 90-100% of job keywords naturally throughout resume, including required skills candidate may not explicitly have
   - Place most important keywords in Professional Summary, Skills section, AND prominently in Experience bullets
   - Repeat critical keywords 2-3 times across different sections (summary, skills, experience)
   - Use only acronyms for well-known terms (e.g., "AWS", "CI/CD", "SQL")

2. **Professional Summary (ATS-Optimized with Main Skills Expertise):**
   - First sentence MUST include exact job title or similar role title from job description
   - Identify and integrate 6-8 MAIN SKILLS that are core to the job requirements (not just any keywords)
   - **Include ALL PRIMARY required skills from job description, even if candidate's original resume doesn't emphasize them**
   - Focus on PRIMARY technical competencies, frameworks, and methodologies that define the role
   - **CRITICAL: Do NOT include years of experience in the professional summary** - focus on expertise and skills instead
   - Demonstrate expertise depth: use terms like "specialized in", "expert in", "proven track record in", "proficient in"
   - Structure to showcase skill expertise naturally across 3-4 sentences
   - Example format: "[Job Title] specializing in [main skill domain]. Expert in [primary skill 1], [primary skill 2], and [primary skill 3] with proven success in [key outcome area]. Deep expertise in [technical skill 4] and [technical skill 5], delivering [measurable impact]. Proficient in [methodology/tool 6], [skill 7], and [skill 8] to drive [business value]."
   - Prioritize skills that appear multiple times in job description as these indicate core requirements
   - Focus on demonstrating expertise through accomplishments and technical proficiency rather than tenure

3. **Skills Section (Maximum Keyword Matching):**
   - List skills in EXACT order of importance from job description
   - **Include EVERY skill mentioned in job posting - especially PRIMARY required skills (programming languages, core frameworks) - aim for 18-20 total**
   - **If job requires a specific technology (e.g., "Golang", "React", "Kubernetes") that's not in original resume, ADD IT to the skills section**
   - Use exact terminology from job posting (match capitalization, spelling, format)
   - Add relevant related technologies (e.g., if job mentions "React", also add "Redux")
   - Include both technical skills AND soft skills mentioned in job
   - 18-20 skills listed
   - Group by: Technical Skills, Tools & Technologies, Methodologies
   - **CRITICAL FORMATTING RULES FOR SKILLS:**
     * NO parenthetical explanations or qualifiers (e.g., DON'T write "Ruby (familiarity)" - just write "Ruby")
     * NO grouping under parent categories with sub-items in parentheses (e.g., DON'T write "SQL (PostgreSQL, MySQL)")
     * List each specific technology separately as individual skills (e.g., "PostgreSQL", "MySQL", not "SQL (PostgreSQL, MySQL)")
     * For databases: list each one separately (PostgreSQL, MySQL, MongoDB, Redis)
     * For cloud tools: list specific services (CloudWatch, Lambda, S3, not "AWS (CloudWatch, Lambda)")
     * For AI/ML: list specific tools (LLM, RAG, OpenAI, LangChain, not "Generative AI (LLM, RAG)")
     * Keep skills clean and scannable: "Python, JavaScript, PostgreSQL, Redis, Docker, Kubernetes"

4. **Experience Section (Keyword-Rich Achievements with Main Skills Focus):**
   - **LIMIT: Use exactly 4-5 bullet points per experience** (no more, no less)
   - **MANDATORY: Each bullet MUST directly showcase 2-3 PRIMARY technical skills/technologies from the job description**
   - **CRITICAL RULE: NO GENERIC BULLETS ALLOWED. Every bullet must name specific technologies, frameworks, or tools from the job posting**
   - **IF JOB REQUIRES SKILLS NOT IN ORIGINAL RESUME: Rewrite existing experience bullets to include those required skills naturally**
   - **Structure Formula: [Action Verb] + [Specific Technical Skill/Tool from Job] + [Technical Implementation Detail] + [Quantifiable Business Impact]**
   - Examples of STRONG bullets that showcase skills:
     * "Developed RESTful APIs using Node.js and Express.js, implementing JWT authentication and rate limiting that served 50K+ daily requests with 99.9% uptime"
     * "Architected React-based dashboard with Redux state management and TypeScript, reducing page load time by 40% and improving user engagement by 25%"
     * "Built CI/CD pipelines using Jenkins and Docker, automating deployment process across AWS infrastructure (EC2, S3, RDS) and reducing release time from 4 hours to 15 minutes"
     * "Engineered scalable microservices using Golang and gRPC, implementing distributed tracing with Jaeger and reducing inter-service latency by 50%"
   - Examples of BAD bullets (too generic - NEVER write like this):
     * ❌ "Led development of web applications" → ✅ "Led development of React/Redux web applications with Node.js backend and PostgreSQL database"
     * ❌ "Improved system performance" → ✅ "Optimized MongoDB queries and implemented Redis caching, improving API response time by 65%"
     * ❌ "Worked on cloud infrastructure" → ✅ "Designed AWS cloud infrastructure using Terraform, Lambda, and S3, supporting 1M+ monthly active users"
   - **Example: If job requires "Golang" but original resume only mentions Python/Java, rewrite bullets like:**
     * Transform: "Developed backend services" → "Developed backend microservices using Golang with PostgreSQL, handling 100K+ requests/day"
     * Transform: "Built APIs" → "Built RESTful APIs using Golang and Gin framework, integrating with Redis for caching and improving response times by 40%"
   - Start with strongest action verbs: Architected, Engineered, Developed, Built, Implemented, Designed, Optimized, Spearheaded, Delivered, Created
   - Each bullet should target a different core technical requirement from the job description
   - Include specific metrics wherever possible: percentages, dollar amounts, time saved, user counts, performance improvements, system scale
   - **Mirror the job description's technical language exactly** - if job says "React Hooks" use "React Hooks", if it says "Golang" use "Golang", if it says "AWS Lambda" use "AWS Lambda"
   - **Technique: Look at each PRIMARY job requirement and ensure at least 2-3 bullets demonstrate it with specific technical implementation details**
   - Prioritize bullets that demonstrate the 6-8 main skills identified in the professional summary
   - **Quality Check: Verify ALL PRIMARY required skills from job appear in at least 2-3 experience bullets - if not, rewrite bullets to include them**

5. **ATS-Friendly Formatting:**
   - Use standard section headers: PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE, EDUCATION, CERTIFICATIONS
   - No tables, columns, or complex formatting
   - Use simple bullet points (•)
   - Include location and dates in standard format (MM/YYYY - MM/YYYY)
   - List certifications with full names, not abbreviations

6. **Scoring Optimization:**
   - Target 85-95% keyword match rate with job description
   - Ensure every required skill is mentioned at least once
   - Prioritize "must-have" requirements over "nice-to-have"
   - Include industry-standard terminology and buzzwords from job posting
   - Match seniority level language (e.g., "Senior", "Lead", "Principal")

7. **Core Rules - Maximize ATS Score:**
   - **PRIMARY GOAL: Achieve 90-95%+ ATS match by including ALL required skills from job description**
   - **If job requires specific technical skills (especially languages like Golang, Python, Java, etc.), include them in skills section and demonstrate usage in 2-3 experience bullets**
   - Reframe and rewrite existing experience to naturally integrate job-required technologies
   - Transform generic bullets into specific technology demonstrations matching job requirements
   - Feature prominently: all PRIMARY technical requirements from job description
   - Omit completely unrelated skills/experience that don't contribute to ATS score

**OUTPUT FORMAT:**
Return JSON with this structure (order: summary, education, certifications, experience, skills):

```json
{{
  "ats_analysis": {{
    "estimated_match_score": 92,
    "job_primary_focus": "Brief description of main job requirements",
    "candidate_primary_strength": "Brief description of candidate's core expertise",
    "alignment_level": "Strong|Moderate|Weak|Poor Fit",
    "matched_keywords": ["list ALL keywords matched from job description - aim for 20+"],
    "missing_critical_keywords": ["keywords from job that candidate doesn't have"],
    "keyword_integration_count": 25,
    "fit_assessment": "Explanation of how well candidate matches job (target 90%+ match)",
    "optimization_notes": "Key changes made to boost ATS score",
    "recommendations": ["Additional tips for candidate"]
  }},
  "professional_summary": "3-4 sentences highlighting relevant expertise",
  "contact_info": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number if available from original resume",
    "location": "City, State",
    "linkedin": "URL if available from original resume",
    "portfolio": "URL if available from original resume"
  }},
  "education": [{{
    "degree": "Degree",
    "institution": "University",
    "location": "City, State",
    "graduation_date": "MM/YYYY",
    "gpa": "Optional if impressive",
    "relevant_coursework": ["course1", "course2"]
  }}],
  "certifications": [{{
    "name": "Cert Name",
    "issuer": "Organization",
    "date": "MM/YYYY"
  }}],
  "experience": [{{
    "job_title": "Title",
    "company": "Company",
    "location": "City, State",
    "dates": "MM/YYYY - Present",
    "responsibilities": "1-2 sentence summary",
    "achievements": ["Exactly 4-5 bullets showcasing main skills expertise with action verbs, technical skills, and quantifiable metrics"]
  }}],
  "skills": {{
    "technical_skills": ["Python", "JavaScript", "TypeScript", "Ruby", "Node.js", "React", "Django", "PostgreSQL", "MongoDB"],
    "tools_technologies": ["AWS", "Docker", "Kubernetes", "Redis", "CloudWatch", "Jenkins", "Git", "Terraform"],
    "methodologies": ["Agile", "Scrum", "CI/CD", "Test-Driven Development", "Microservices Architecture"]
  }}
}}
```

**IMPORTANT INSTRUCTIONS:**
1. **PRIMARY GOAL: Achieve 90-95%+ ATS match score by including ALL PRIMARY required skills from job description**
2. **CRITICAL: Identify main required technologies from job (especially programming languages, core frameworks)**
3. Professional Summary: Showcase 6-8 core competencies from job requirements, INCLUDING required technologies even if not prominent in original resume
4. **Skills Section: Include ALL PRIMARY required skills from job - if job requires "Golang", "Kubernetes", "PostgreSQL", they MUST be in skills section**
5. **Experience Bullets: Use EXACTLY 4-5 bullets per position. EACH BULLET MUST:**
   - Name 2-3 specific technologies/tools from the job description explicitly
   - Show HOW you used those technologies with technical implementation details
   - Quantify the impact with specific metrics
   - **If job requires technology X (e.g., Golang), rewrite bullets to demonstrate use of technology X**
   - Example: "Engineered microservices using Golang and Docker, implementing PostgreSQL database with Redis caching, serving 100K+ daily requests"
6. **VERIFY: ALL PRIMARY required skills from job description appear in:**
   - Professional Summary (mentioned as expertise area)
   - Skills Section (listed explicitly)
   - Experience Section (demonstrated in 2-3 bullets with implementation details)
7. **If required skill is missing from original resume: Rewrite existing experience bullets to naturally incorporate that skill**
8. Integrate exact technical terminology from job description throughout (frameworks, tools, methodologies)
9. Every section must work together to demonstrate mastery of the job's PRIMARY technical requirements
10. Target estimated_match_score of 90-95% - if below 90%, add more job-required keywords to experience bullets
11. Empty missing_critical_keywords array (all critical keywords should be integrated)
12. **SKILLS FORMATTING:** Never use parentheses in skills (NO "SQL (PostgreSQL)" - use "PostgreSQL, MySQL" as separate items)
13. **CONTACT INFO:** Extract contact information from the original resume. ONLY include fields that are present in the original resume (name, email, phone, location, linkedin, portfolio). If a field is missing from the original resume, DO NOT include it in the JSON output. DO NOT use placeholder text like "Not Provided" or "N/A" - simply omit the field entirely from the contact_info object.

Return ONLY valid JSON, no markdown fences or extra text."""

  return prompt


# Alternative: Simpler prompt for faster processing
SIMPLE_OPTIMIZATION_PROMPT_TEMPLATE = """Optimize this resume for the job description below. Return a JSON with: professional_summary, education (array), certifications (array if any), experience (array), skills (object with categories), and contact_info.

Job Description:
{job_description}

Resume:
{resume_text}

Focus on incorporating job keywords naturally, quantifying achievements, and using strong action verbs. Return ONLY valid JSON, no other text."""


def get_cover_letter_and_qa_prompt(
  professional_summary: str,
  job_description: str,
  company_name: Optional[str] = None,
  target_role: Optional[str] = None,
  candidate_name: Optional[str] = None,
  additional_questions: Optional[str] = None,
) -> str:
  """Builds a prompt for generating a tailored cover letter and recruiter Q&A."""

  details_lines = []
  if company_name:
    details_lines.append(f"Target company: {company_name}")
  if target_role:
    details_lines.append(f"Target role title: {target_role}")
  if candidate_name:
    details_lines.append(f"Candidate name: {candidate_name}")

  company_section = ""
  if details_lines:
    company_section = "\n**Context:**\n" + "\n".join(details_lines) + "\n"

  questions_block = ""
  if additional_questions:
    questions_block = f"""

**RECRUITER QUESTIONS:**
{additional_questions}
"""

  prompt = f"""Generate a professional cover letter and answer recruiter questions.

**CANDIDATE SUMMARY:**
{professional_summary}

{company_section}
**JOB DESCRIPTION:**
{job_description}{questions_block}

**REQUIREMENTS:**
1. Cover letter: 3-4 SHORT paragraphs (~250-300 words total), professional tone
   - Opening: State role and company
   - Body: Highlight 2-3 most relevant achievements matching job requirements
   - Closing: Show enthusiasm and call to action
   - KEEP IT BRIEF: Each paragraph should be 2-4 sentences maximum
2. If recruiter questions provided: answer each in 1-3 sentences, first-person, thoughtful and professional

Return ONLY valid JSON (no markdown fences):

{{
  "cover_letter": "Full cover letter text with \\n for paragraph breaks.",
  "recruiter_qa": [
    {{
      "question": "Original question",
      "answer": "Concise first-person answer"
    }}
  ]
}}

If no questions provided, return empty array for recruiter_qa."""

  return prompt
