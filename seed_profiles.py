#!/usr/bin/env python3
"""
Seed 20 diverse evaluation profile templates for testing.
These are user templates (not system), so they can be edited and deleted.

Run this script to populate the database with sample templates.
Usage: python seed_profiles.py
"""

import asyncio
import uuid
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import EvaluationTemplate, TemplateCriterion, User


# 20 Diverse evaluation templates
SAMPLE_TEMPLATES = [
    # ============================================
    # 1. Single Criterion Templates (Simple)
    # ============================================
    {
        "name": "Python Developer (Basic)",
        "description": "Simple Python proficiency check for entry-level roles.",
        "passing_score": 50,
        "minimum_criteria_met": 1,
        "criteria": [
            {
                "name": "Python Skills",
                "description": "Core Python programming abilities including syntax, data structures, and standard library.",
                "max_points": 100,
                "keywords": ["Python", "Django", "Flask", "FastAPI", "Pandas", "NumPy", "pip", "virtualenv", "pytest"],
                "evaluation_guidelines": "Full points for 3+ years Python experience with frameworks. Medium for 1-2 years. Low for beginners.",
                "is_required": True,
                "sort_order": 1,
            },
        ],
    },
    {
        "name": "React Frontend Focus",
        "description": "Single criterion focused on React.js expertise for frontend positions.",
        "passing_score": 60,
        "minimum_criteria_met": 1,
        "criteria": [
            {
                "name": "React Mastery",
                "description": "Deep knowledge of React ecosystem including hooks, state management, and modern patterns.",
                "max_points": 100,
                "keywords": ["React", "React Hooks", "Redux", "Zustand", "Next.js", "TypeScript", "JSX", "Component", "Virtual DOM", "React Query"],
                "evaluation_guidelines": "Full points for production React apps with hooks & TypeScript. High for Redux/state management experience. Medium for basic React knowledge.",
                "is_required": True,
                "sort_order": 1,
            },
        ],
    },
    
    # ============================================
    # 2. Two Criteria Templates
    # ============================================
    {
        "name": "TypeScript Full-Stack",
        "description": "Evaluates TypeScript proficiency across frontend and backend development.",
        "passing_score": 55,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "TypeScript Fundamentals",
                "description": "Core TypeScript knowledge including types, interfaces, generics, and advanced patterns.",
                "max_points": 50,
                "keywords": ["TypeScript", "Types", "Interfaces", "Generics", "Enums", "Type Guards", "Utility Types", "tsconfig"],
                "evaluation_guidelines": "Full points for advanced TypeScript (generics, utility types). High for solid typing practices. Medium for basic usage.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Full-Stack Implementation",
                "description": "Ability to build complete applications from frontend to backend using TypeScript.",
                "max_points": 50,
                "keywords": ["Node.js", "Express", "NestJS", "React", "Next.js", "API", "REST", "GraphQL", "Prisma", "TypeORM"],
                "evaluation_guidelines": "Full points for end-to-end TypeScript projects. High for either frontend or backend expertise. Medium for learning.",
                "is_required": True,
                "sort_order": 2,
            },
        ],
    },
    {
        "name": "FastAPI Backend Developer",
        "description": "Focused on Python FastAPI expertise for API development roles.",
        "passing_score": 60,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "FastAPI Proficiency",
                "description": "Knowledge of FastAPI framework including async/await, dependency injection, and Pydantic.",
                "max_points": 60,
                "keywords": ["FastAPI", "Pydantic", "async", "await", "Starlette", "uvicorn", "OpenAPI", "Swagger", "dependency injection"],
                "evaluation_guidelines": "Full points for production FastAPI apps with async patterns. High for Pydantic models & validation. Medium for basic knowledge.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Database Integration",
                "description": "Experience with databases and ORMs in Python API contexts.",
                "max_points": 40,
                "keywords": ["SQLAlchemy", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Alembic", "migrations", "async database"],
                "evaluation_guidelines": "Full points for SQLAlchemy async with migrations. High for any SQL + ORM. Medium for basic database usage.",
                "is_required": False,
                "sort_order": 2,
            },
        ],
    },
    
    # ============================================
    # 3. Three Criteria Templates
    # ============================================
    {
        "name": "Crypto & Blockchain Developer",
        "description": "Evaluates cryptocurrency and blockchain development experience.",
        "passing_score": 55,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Blockchain Fundamentals",
                "description": "Understanding of blockchain technology, consensus mechanisms, and distributed ledgers.",
                "max_points": 30,
                "keywords": ["Blockchain", "Consensus", "Distributed Ledger", "Proof of Work", "Proof of Stake", "Hash", "Merkle Tree", "Node"],
                "evaluation_guidelines": "Full points for deep blockchain understanding. High for practical blockchain project experience. Medium for theoretical knowledge.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Smart Contract Development",
                "description": "Experience with smart contracts on Ethereum, Solana, or other chains.",
                "max_points": 40,
                "keywords": ["Solidity", "Smart Contract", "Ethereum", "ERC-20", "ERC-721", "NFT", "Hardhat", "Truffle", "Foundry", "Solana", "Rust"],
                "evaluation_guidelines": "Full points for deployed mainnet contracts. High for testnet experience. Medium for tutorials/learning.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Web3 Integration",
                "description": "Frontend integration with blockchain using Web3 libraries.",
                "max_points": 30,
                "keywords": ["Web3.js", "ethers.js", "MetaMask", "WalletConnect", "dApp", "DeFi", "Uniswap", "Aave", "wallet integration"],
                "evaluation_guidelines": "Full points for production dApps with wallet integration. High for DeFi protocol work. Medium for basic Web3 frontend.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "Junior Developer Screening",
        "description": "Entry-level developer assessment focusing on fundamentals and potential.",
        "passing_score": 45,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Programming Fundamentals",
                "description": "Basic programming concepts, algorithms, and problem-solving abilities.",
                "max_points": 40,
                "keywords": ["Programming", "Algorithm", "Data Structure", "OOP", "Functions", "Variables", "Loops", "Conditionals", "Debugging"],
                "evaluation_guidelines": "Full points for CS fundamentals demonstrated. High for self-taught with projects. Medium for bootcamp basics.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Learning Ability",
                "description": "Demonstrated ability to learn new technologies quickly.",
                "max_points": 30,
                "keywords": ["Fast learner", "Bootcamp", "Self-taught", "Online courses", "Projects", "GitHub", "Portfolio", "Eager", "Curious"],
                "evaluation_guidelines": "Full points for rapid skill acquisition evidence. High for diverse project portfolio. Medium for formal education only.",
                "is_required": False,
                "sort_order": 2,
            },
            {
                "name": "Collaboration & Communication",
                "description": "Ability to work in teams and communicate effectively.",
                "max_points": 30,
                "keywords": ["Team", "Collaboration", "Communication", "Agile", "Scrum", "Remote", "Pair programming", "Code review"],
                "evaluation_guidelines": "Full points for team project experience. High for internship/job experience. Medium for academic team projects.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "DevOps & Cloud Engineer",
        "description": "Infrastructure, CI/CD, and cloud platform expertise evaluation.",
        "passing_score": 60,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Cloud Platforms",
                "description": "Experience with major cloud providers and their services.",
                "max_points": 35,
                "keywords": ["AWS", "GCP", "Azure", "EC2", "S3", "Lambda", "Cloud Functions", "IAM", "VPC", "Cloud Run", "ECS", "EKS"],
                "evaluation_guidelines": "Full points for multi-cloud or AWS certification. High for production cloud infrastructure. Medium for basic cloud usage.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "CI/CD & Automation",
                "description": "Building and maintaining automated pipelines for testing and deployment.",
                "max_points": 35,
                "keywords": ["CI/CD", "GitHub Actions", "GitLab CI", "Jenkins", "CircleCI", "ArgoCD", "Terraform", "Ansible", "Infrastructure as Code"],
                "evaluation_guidelines": "Full points for IaC + CI/CD pipeline design. High for GitHub Actions/GitLab CI experience. Medium for basic automation.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Containerization",
                "description": "Docker and Kubernetes expertise for container orchestration.",
                "max_points": 30,
                "keywords": ["Docker", "Kubernetes", "K8s", "Helm", "Container", "Pod", "Deployment", "Service", "Docker Compose", "Dockerfile"],
                "evaluation_guidelines": "Full points for Kubernetes in production. High for Docker + orchestration. Medium for basic Docker usage.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    
    # ============================================
    # 4. Four Criteria Templates
    # ============================================
    {
        "name": "Senior Backend Engineer",
        "description": "Comprehensive evaluation for senior backend positions.",
        "passing_score": 65,
        "minimum_criteria_met": 3,
        "criteria": [
            {
                "name": "System Design",
                "description": "Ability to design scalable, maintainable backend systems.",
                "max_points": 30,
                "keywords": ["System Design", "Architecture", "Scalability", "Microservices", "Monolith", "API Design", "Database Design", "Caching"],
                "evaluation_guidelines": "Full points for designing systems at scale. High for microservices experience. Medium for basic architecture knowledge.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Backend Languages & Frameworks",
                "description": "Proficiency in backend programming languages and frameworks.",
                "max_points": 30,
                "keywords": ["Python", "Java", "Go", "Node.js", "FastAPI", "Django", "Spring", "Express", "NestJS", "Rust"],
                "evaluation_guidelines": "Full points for multiple languages + frameworks. High for deep expertise in one. Medium for basic backend development.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Database & Storage",
                "description": "Experience with various database systems and data storage solutions.",
                "max_points": 25,
                "keywords": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB", "Cassandra", "SQL", "NoSQL", "Caching"],
                "evaluation_guidelines": "Full points for SQL + NoSQL + caching. High for advanced query optimization. Medium for basic CRUD operations.",
                "is_required": True,
                "sort_order": 3,
            },
            {
                "name": "Leadership & Mentoring",
                "description": "Experience leading teams, mentoring juniors, and driving technical decisions.",
                "max_points": 15,
                "keywords": ["Leadership", "Mentoring", "Tech Lead", "Code Review", "Architecture Decisions", "Team", "Senior", "Principal"],
                "evaluation_guidelines": "Full points for tech lead experience. High for mentoring juniors. Medium for code review participation.",
                "is_required": False,
                "sort_order": 4,
            },
        ],
    },
    {
        "name": "Data Engineer",
        "description": "Evaluation for data pipeline and data infrastructure roles.",
        "passing_score": 60,
        "minimum_criteria_met": 3,
        "criteria": [
            {
                "name": "Data Pipeline Development",
                "description": "Building ETL/ELT pipelines for data processing at scale.",
                "max_points": 30,
                "keywords": ["ETL", "ELT", "Data Pipeline", "Airflow", "Luigi", "Prefect", "Dagster", "Data Orchestration", "Batch Processing"],
                "evaluation_guidelines": "Full points for production pipeline design. High for Airflow/orchestration. Medium for basic ETL scripts.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Big Data Technologies",
                "description": "Experience with big data processing frameworks and tools.",
                "max_points": 30,
                "keywords": ["Spark", "Hadoop", "Kafka", "Flink", "Beam", "Presto", "BigQuery", "Snowflake", "Databricks", "dbt"],
                "evaluation_guidelines": "Full points for Spark + streaming experience. High for data warehouse tools. Medium for basic big data concepts.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "SQL & Data Modeling",
                "description": "Advanced SQL skills and data modeling expertise.",
                "max_points": 25,
                "keywords": ["SQL", "Data Modeling", "Star Schema", "Dimensional Modeling", "PostgreSQL", "Redshift", "Data Warehouse", "Analytics"],
                "evaluation_guidelines": "Full points for complex SQL + warehouse modeling. High for analytical queries. Medium for basic SQL.",
                "is_required": True,
                "sort_order": 3,
            },
            {
                "name": "Python for Data",
                "description": "Python programming for data manipulation and analysis.",
                "max_points": 15,
                "keywords": ["Python", "Pandas", "NumPy", "PySpark", "Data Analysis", "Jupyter", "Polars", "Data Manipulation"],
                "evaluation_guidelines": "Full points for PySpark + production Python. High for Pandas expertise. Medium for basic Python data work.",
                "is_required": False,
                "sort_order": 4,
            },
        ],
    },
    {
        "name": "Mobile Developer (React Native)",
        "description": "Cross-platform mobile development with React Native focus.",
        "passing_score": 55,
        "minimum_criteria_met": 3,
        "criteria": [
            {
                "name": "React Native Core",
                "description": "Core React Native development including components, navigation, and state management.",
                "max_points": 35,
                "keywords": ["React Native", "Expo", "Navigation", "Redux", "React Query", "StyleSheet", "Flexbox", "Mobile", "Cross-platform"],
                "evaluation_guidelines": "Full points for published apps with React Native. High for complex app features. Medium for basic RN development.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Native Integration",
                "description": "Experience bridging to native iOS/Android code when needed.",
                "max_points": 25,
                "keywords": ["Native Modules", "iOS", "Android", "Swift", "Kotlin", "Java", "Objective-C", "Bridge", "Native Code"],
                "evaluation_guidelines": "Full points for custom native modules. High for native debugging experience. Medium for awareness of native platforms.",
                "is_required": False,
                "sort_order": 2,
            },
            {
                "name": "App Store Deployment",
                "description": "Experience with app store submission and mobile CI/CD.",
                "max_points": 20,
                "keywords": ["App Store", "Google Play", "TestFlight", "Fastlane", "CodePush", "OTA Updates", "App Signing", "Release"],
                "evaluation_guidelines": "Full points for full deployment pipeline. High for app store experience. Medium for development builds only.",
                "is_required": False,
                "sort_order": 3,
            },
            {
                "name": "Mobile UX",
                "description": "Understanding of mobile-specific UX patterns and performance.",
                "max_points": 20,
                "keywords": ["Mobile UX", "Performance", "Animations", "Gestures", "Responsive", "Accessibility", "Mobile Design", "Touch"],
                "evaluation_guidelines": "Full points for performance optimization experience. High for animation/gesture work. Medium for basic mobile UX.",
                "is_required": False,
                "sort_order": 4,
            },
        ],
    },
    
    # ============================================
    # 5. Five Criteria Templates (Comprehensive)
    # ============================================
    {
        "name": "AI/ML Engineer",
        "description": "Machine learning and AI engineering role evaluation.",
        "passing_score": 60,
        "minimum_criteria_met": 3,
        "criteria": [
            {
                "name": "Machine Learning Fundamentals",
                "description": "Core ML concepts, algorithms, and model development.",
                "max_points": 25,
                "keywords": ["Machine Learning", "Deep Learning", "Neural Networks", "Classification", "Regression", "Clustering", "Feature Engineering"],
                "evaluation_guidelines": "Full points for production ML models. High for research/academic ML. Medium for online course completion.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "ML Frameworks & Tools",
                "description": "Proficiency with ML frameworks and development tools.",
                "max_points": 25,
                "keywords": ["TensorFlow", "PyTorch", "scikit-learn", "Keras", "Hugging Face", "XGBoost", "LightGBM", "MLflow", "Weights & Biases"],
                "evaluation_guidelines": "Full points for PyTorch/TensorFlow production use. High for experiment tracking. Medium for tutorial-level experience.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "LLM & NLP",
                "description": "Experience with large language models and natural language processing.",
                "max_points": 20,
                "keywords": ["LLM", "NLP", "Transformers", "BERT", "GPT", "Fine-tuning", "RAG", "Embeddings", "Tokenization", "Prompt Engineering"],
                "evaluation_guidelines": "Full points for LLM fine-tuning or RAG systems. High for prompt engineering. Medium for API usage only.",
                "is_required": False,
                "sort_order": 3,
            },
            {
                "name": "MLOps & Deployment",
                "description": "Deploying and monitoring ML models in production.",
                "max_points": 15,
                "keywords": ["MLOps", "Model Deployment", "Model Serving", "SageMaker", "Vertex AI", "BentoML", "Model Monitoring", "A/B Testing"],
                "evaluation_guidelines": "Full points for end-to-end MLOps. High for model serving experience. Medium for local model development.",
                "is_required": False,
                "sort_order": 4,
            },
            {
                "name": "Mathematics & Statistics",
                "description": "Mathematical foundations for ML including statistics and linear algebra.",
                "max_points": 15,
                "keywords": ["Statistics", "Linear Algebra", "Calculus", "Probability", "Optimization", "Mathematics", "Statistical Analysis"],
                "evaluation_guidelines": "Full points for strong math background. High for statistics expertise. Medium for basic math understanding.",
                "is_required": False,
                "sort_order": 5,
            },
        ],
    },
    {
        "name": "Fintech Payment Systems",
        "description": "Specialized evaluation for payment processing and fintech infrastructure.",
        "passing_score": 65,
        "minimum_criteria_met": 4,
        "criteria": [
            {
                "name": "Payment Processing",
                "description": "Experience with payment gateways, processors, and payment flows.",
                "max_points": 25,
                "keywords": ["Payments", "Stripe", "PayPal", "Adyen", "Square", "Payment Gateway", "Checkout", "Transactions", "Settlement"],
                "evaluation_guidelines": "Full points for payment infrastructure design. High for integration experience. Medium for basic payment API usage.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Security & Compliance",
                "description": "Knowledge of financial security standards and compliance requirements.",
                "max_points": 20,
                "keywords": ["PCI DSS", "PCI Compliance", "Encryption", "Tokenization", "KYC", "AML", "Fraud Detection", "Security", "GDPR"],
                "evaluation_guidelines": "Full points for PCI compliance implementation. High for security architecture. Medium for awareness of standards.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Banking & Ledger Systems",
                "description": "Understanding of core banking concepts and ledger architecture.",
                "max_points": 20,
                "keywords": ["Ledger", "Double-entry", "Accounting", "Banking", "Core Banking", "Reconciliation", "Balance", "Transaction History"],
                "evaluation_guidelines": "Full points for ledger system design. High for banking integrations. Medium for basic understanding.",
                "is_required": True,
                "sort_order": 3,
            },
            {
                "name": "API & Integration",
                "description": "Building and consuming financial APIs and third-party integrations.",
                "max_points": 20,
                "keywords": ["API", "REST", "Webhooks", "Plaid", "Yodlee", "Open Banking", "Integration", "Idempotency", "Retry Logic"],
                "evaluation_guidelines": "Full points for financial API design. High for webhook/async patterns. Medium for basic API consumption.",
                "is_required": True,
                "sort_order": 4,
            },
            {
                "name": "Real-time Systems",
                "description": "Experience with real-time transaction processing and low-latency systems.",
                "max_points": 15,
                "keywords": ["Real-time", "Low Latency", "Streaming", "Message Queue", "Kafka", "RabbitMQ", "Event-driven", "High Throughput"],
                "evaluation_guidelines": "Full points for high-throughput system design. High for message queue experience. Medium for basic async processing.",
                "is_required": False,
                "sort_order": 5,
            },
        ],
    },
    {
        "name": "Frontend Architect",
        "description": "Senior frontend role with architecture and leadership responsibilities.",
        "passing_score": 65,
        "minimum_criteria_met": 4,
        "criteria": [
            {
                "name": "Frontend Frameworks Mastery",
                "description": "Deep expertise in modern frontend frameworks and their ecosystems.",
                "max_points": 25,
                "keywords": ["React", "Vue", "Angular", "Svelte", "Next.js", "Nuxt", "State Management", "Server Components", "Hydration"],
                "evaluation_guidelines": "Full points for framework-agnostic architecture. High for deep single-framework expertise. Medium for basic framework usage.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Performance Optimization",
                "description": "Web performance, bundle optimization, and core web vitals.",
                "max_points": 20,
                "keywords": ["Performance", "Core Web Vitals", "Lighthouse", "Bundle Size", "Code Splitting", "Lazy Loading", "Caching", "CDN"],
                "evaluation_guidelines": "Full points for measurable performance improvements. High for optimization strategies. Medium for awareness of metrics.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Design Systems",
                "description": "Building and maintaining component libraries and design systems.",
                "max_points": 20,
                "keywords": ["Design System", "Component Library", "Storybook", "Tokens", "Accessibility", "WCAG", "Atomic Design", "Figma"],
                "evaluation_guidelines": "Full points for design system architecture. High for component library contribution. Medium for consuming design systems.",
                "is_required": True,
                "sort_order": 3,
            },
            {
                "name": "Testing Strategy",
                "description": "Comprehensive testing approach for frontend applications.",
                "max_points": 20,
                "keywords": ["Testing", "Jest", "Vitest", "Cypress", "Playwright", "RTL", "E2E", "Unit Testing", "Integration Testing", "TDD"],
                "evaluation_guidelines": "Full points for testing strategy ownership. High for E2E + unit testing. Medium for basic test writing.",
                "is_required": True,
                "sort_order": 4,
            },
            {
                "name": "Technical Leadership",
                "description": "Leading frontend teams and driving technical decisions.",
                "max_points": 15,
                "keywords": ["Tech Lead", "Architecture", "Code Review", "Mentoring", "RFC", "Technical Decision", "Team Lead"],
                "evaluation_guidelines": "Full points for frontend team leadership. High for architecture decisions. Medium for senior IC experience.",
                "is_required": False,
                "sort_order": 5,
            },
        ],
    },
    
    # ============================================
    # 6. Specialized/Niche Templates
    # ============================================
    {
        "name": "Security Engineer",
        "description": "Application and infrastructure security evaluation.",
        "passing_score": 65,
        "minimum_criteria_met": 3,
        "criteria": [
            {
                "name": "Application Security",
                "description": "Securing applications against common vulnerabilities.",
                "max_points": 35,
                "keywords": ["OWASP", "XSS", "SQL Injection", "CSRF", "Security", "Penetration Testing", "Vulnerability", "Secure Coding"],
                "evaluation_guidelines": "Full points for security engineering experience. High for penetration testing. Medium for secure coding practices.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Infrastructure Security",
                "description": "Securing cloud infrastructure and networks.",
                "max_points": 35,
                "keywords": ["Cloud Security", "IAM", "Network Security", "Firewall", "VPN", "Zero Trust", "Security Groups", "Encryption at Rest"],
                "evaluation_guidelines": "Full points for cloud security architecture. High for IAM/access control. Medium for basic infrastructure security.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Security Tools & Monitoring",
                "description": "Using security tools for monitoring and incident response.",
                "max_points": 30,
                "keywords": ["SIEM", "IDS", "Logging", "Monitoring", "Incident Response", "Threat Detection", "Security Audit", "Compliance"],
                "evaluation_guidelines": "Full points for incident response experience. High for SIEM/monitoring setup. Medium for security tool usage.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "Technical Writer / DevRel",
        "description": "Documentation, technical writing, and developer relations.",
        "passing_score": 55,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Technical Writing",
                "description": "Creating clear, accurate technical documentation.",
                "max_points": 40,
                "keywords": ["Documentation", "Technical Writing", "API Docs", "Tutorials", "README", "Markdown", "Docs-as-Code", "Writing"],
                "evaluation_guidelines": "Full points for published documentation portfolio. High for API documentation. Medium for internal docs experience.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Developer Experience",
                "description": "Understanding and improving developer experience.",
                "max_points": 30,
                "keywords": ["Developer Experience", "DX", "SDK", "CLI", "Onboarding", "Developer Tools", "API Design", "DevRel"],
                "evaluation_guidelines": "Full points for DevRel experience. High for SDK/CLI development. Medium for developer-focused thinking.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Community & Speaking",
                "description": "Community engagement and public speaking.",
                "max_points": 30,
                "keywords": ["Conference", "Speaking", "Community", "Open Source", "Blog", "YouTube", "Streaming", "Twitter", "Advocacy"],
                "evaluation_guidelines": "Full points for conference speaking. High for active community presence. Medium for blog/content creation.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "QA Automation Engineer",
        "description": "Test automation and quality assurance evaluation.",
        "passing_score": 55,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Test Automation",
                "description": "Building automated test suites and frameworks.",
                "max_points": 40,
                "keywords": ["Test Automation", "Selenium", "Cypress", "Playwright", "pytest", "Jest", "TestNG", "Automation Framework"],
                "evaluation_guidelines": "Full points for framework design. High for E2E automation. Medium for basic test automation.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Testing Strategy",
                "description": "Comprehensive testing approach including test planning.",
                "max_points": 35,
                "keywords": ["Test Strategy", "Test Planning", "Coverage", "Regression", "Smoke Testing", "Integration Testing", "TDD", "BDD"],
                "evaluation_guidelines": "Full points for test strategy ownership. High for coverage improvement. Medium for test execution experience.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Performance & Load Testing",
                "description": "Performance testing and load testing capabilities.",
                "max_points": 25,
                "keywords": ["Performance Testing", "Load Testing", "JMeter", "k6", "Gatling", "Stress Testing", "Benchmarking"],
                "evaluation_guidelines": "Full points for performance test design. High for load testing tools. Medium for basic performance awareness.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "Startup Generalist",
        "description": "Jack-of-all-trades evaluation for early-stage startup roles.",
        "passing_score": 50,
        "minimum_criteria_met": 3,
        "criteria": [
            {
                "name": "Full-Stack Capability",
                "description": "Ability to work across the entire stack independently.",
                "max_points": 30,
                "keywords": ["Full-Stack", "Frontend", "Backend", "Database", "DevOps", "API", "Independent", "Versatile"],
                "evaluation_guidelines": "Full points for solo project delivery. High for cross-functional work. Medium for primary specialty with exposure.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Speed & Iteration",
                "description": "Ability to ship quickly and iterate based on feedback.",
                "max_points": 25,
                "keywords": ["Fast", "Ship", "MVP", "Iteration", "Agile", "Startup", "Rapid Development", "Prototyping"],
                "evaluation_guidelines": "Full points for startup shipping experience. High for rapid prototyping. Medium for agile process experience.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "Ownership & Initiative",
                "description": "Taking ownership of problems and driving solutions.",
                "max_points": 25,
                "keywords": ["Ownership", "Initiative", "Problem Solving", "Self-starter", "Proactive", "Entrepreneurial", "Founder"],
                "evaluation_guidelines": "Full points for founder/early employee experience. High for project ownership. Medium for initiative examples.",
                "is_required": True,
                "sort_order": 3,
            },
            {
                "name": "Adaptability",
                "description": "Willingness to learn new technologies and change direction.",
                "max_points": 20,
                "keywords": ["Adaptable", "Learning", "Flexible", "Change", "Growth Mindset", "Curious", "New Technologies"],
                "evaluation_guidelines": "Full points for demonstrated pivots. High for diverse tech experience. Medium for learning attitude.",
                "is_required": False,
                "sort_order": 4,
            },
        ],
    },
    {
        "name": "Database Administrator",
        "description": "Database administration and optimization expertise.",
        "passing_score": 60,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Database Management",
                "description": "Administration of relational and NoSQL databases.",
                "max_points": 40,
                "keywords": ["DBA", "PostgreSQL", "MySQL", "Oracle", "SQL Server", "MongoDB", "Database Administration", "Backup", "Recovery"],
                "evaluation_guidelines": "Full points for production DBA experience. High for multiple database systems. Medium for single database expertise.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Performance Tuning",
                "description": "Query optimization and database performance tuning.",
                "max_points": 35,
                "keywords": ["Query Optimization", "Index", "Explain Plan", "Performance Tuning", "Slow Query", "Profiling", "Caching"],
                "evaluation_guidelines": "Full points for significant performance improvements. High for index optimization. Medium for basic query tuning.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "High Availability",
                "description": "Replication, clustering, and high availability setups.",
                "max_points": 25,
                "keywords": ["Replication", "Clustering", "High Availability", "Failover", "Disaster Recovery", "Standby", "Master-Slave"],
                "evaluation_guidelines": "Full points for HA architecture design. High for replication setup. Medium for HA concepts understanding.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "Embedded Systems Developer",
        "description": "Hardware-software integration and embedded systems.",
        "passing_score": 55,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Embedded Programming",
                "description": "Low-level programming for embedded systems.",
                "max_points": 40,
                "keywords": ["Embedded", "C", "C++", "Microcontroller", "ARM", "RTOS", "Firmware", "Assembly", "Bare Metal"],
                "evaluation_guidelines": "Full points for production firmware. High for RTOS experience. Medium for hobbyist embedded projects.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Hardware Integration",
                "description": "Working with sensors, actuators, and hardware interfaces.",
                "max_points": 35,
                "keywords": ["Hardware", "Sensor", "I2C", "SPI", "UART", "GPIO", "PCB", "Schematic", "Arduino", "Raspberry Pi"],
                "evaluation_guidelines": "Full points for custom hardware design. High for sensor integration. Medium for development board experience.",
                "is_required": True,
                "sort_order": 2,
            },
            {
                "name": "IoT & Connectivity",
                "description": "Internet of Things and wireless connectivity.",
                "max_points": 25,
                "keywords": ["IoT", "WiFi", "Bluetooth", "LoRa", "MQTT", "Zigbee", "Cloud IoT", "Edge Computing"],
                "evaluation_guidelines": "Full points for IoT product development. High for wireless protocols. Medium for basic connectivity.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "Gaming & Graphics Developer",
        "description": "Game development and graphics programming.",
        "passing_score": 55,
        "minimum_criteria_met": 2,
        "criteria": [
            {
                "name": "Game Engines",
                "description": "Proficiency with game engines and game development.",
                "max_points": 40,
                "keywords": ["Unity", "Unreal Engine", "Godot", "Game Development", "C#", "Blueprints", "Game Design", "3D", "2D"],
                "evaluation_guidelines": "Full points for shipped games. High for game jam participation. Medium for tutorial projects.",
                "is_required": True,
                "sort_order": 1,
            },
            {
                "name": "Graphics Programming",
                "description": "Shaders, rendering pipelines, and graphics APIs.",
                "max_points": 35,
                "keywords": ["Shader", "OpenGL", "Vulkan", "DirectX", "WebGL", "HLSL", "GLSL", "Rendering", "Graphics Pipeline"],
                "evaluation_guidelines": "Full points for custom shader/engine work. High for rendering optimization. Medium for basic shader usage.",
                "is_required": False,
                "sort_order": 2,
            },
            {
                "name": "Game Systems",
                "description": "Implementing game mechanics, AI, and physics.",
                "max_points": 25,
                "keywords": ["Game AI", "Physics", "Animation", "Multiplayer", "Networking", "State Machine", "Pathfinding", "ECS"],
                "evaluation_guidelines": "Full points for complex game systems. High for multiplayer networking. Medium for basic game mechanics.",
                "is_required": False,
                "sort_order": 3,
            },
        ],
    },
]


async def seed_user_templates(session, user_id: uuid.UUID) -> int:
    """Create sample evaluation templates for a user.
    
    Args:
        session: Async database session.
        user_id: The user ID to assign templates to.
        
    Returns:
        Number of templates created.
    """
    created = 0
    
    for template_data in SAMPLE_TEMPLATES:
        # Check if template with same name exists for this user
        result = await session.execute(
            select(EvaluationTemplate).where(
                EvaluationTemplate.user_id == user_id,
                EvaluationTemplate.name == template_data["name"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  ⏭️  Skipping '{template_data['name']}' (already exists)")
            continue
        
        # Extract criteria
        criteria_data = template_data.pop("criteria")
        
        # Create template (not a system template, so it's editable)
        template = EvaluationTemplate(
            user_id=user_id,
            is_system_template=False,  # User can edit/delete
            **template_data
        )
        session.add(template)
        await session.flush()  # Get the template ID
        
        # Create criteria
        for criterion_data in criteria_data:
            criterion = TemplateCriterion(
                template_id=template.id,
                **criterion_data
            )
            session.add(criterion)
        
        # Restore criteria_data for potential reuse
        template_data["criteria"] = criteria_data
        
        print(f"  ✓ Created '{template_data['name']}' ({len(criteria_data)} criteria)")
        created += 1
    
    await session.commit()
    return created


async def main():
    """Main entry point for seeding templates."""
    print("\n🚀 Seeding Evaluation Profile Templates\n")
    
    # Target user email
    TARGET_EMAIL = "stiliyan.goshev97@gmail.com"
    
    async with AsyncSessionLocal() as session:
        # Find the specific user by email
        result = await session.execute(
            select(User).where(User.email == TARGET_EMAIL)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User with email '{TARGET_EMAIL}' not found in database.")
            print("   Make sure this user exists before running this script.")
            return
        
        print(f"📧 Assigning templates to user: {user.email}\n")
        
        created = await seed_user_templates(session, user.id)
        
        print(f"\n✅ Created {created} new templates!")
        print(f"📊 Total templates available: {len(SAMPLE_TEMPLATES)}")
        print(f"\n💡 These templates are editable and deletable (not system templates).\n")


if __name__ == "__main__":
    asyncio.run(main())
