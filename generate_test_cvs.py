#!/usr/bin/env python3
"""
Generate 20 test CVs for the CV Screening Agent.
Uses reportlab to create PDF resumes with diverse profiles.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

# CV Data - 20 diverse candidates
CANDIDATES = [
    # Should PASS - Strong candidates
    {
        "name": "Alex Thompson",
        "email": "alex.thompson@email.com",
        "phone": "+1 (555) 123-4567",
        "education": "B.S. Computer Science, MIT, 2020",
        "fintech_exp": "3 years at JPMorgan Chase - Payment Systems Developer. Built real-time transaction processing system handling 10M+ daily transactions. Experience with blockchain integration.",
        "tech_skills": "TypeScript, Python, React, Node.js, FastAPI, PostgreSQL, Redis, Docker, AWS. Expert in microservices architecture.",
        "soft_skills": "Fast learner - shipped 5 major features in first 6 months. Thrives under pressure during trading hours. Led team of 3 junior developers.",
        "ai_native": "Daily user of GitHub Copilot and Claude Code. Built RAG-powered customer support system using LangChain. Implemented MCP server for trading data access. Created AI agents for automated compliance checks."
    },
    {
        "name": "Sarah Chen",
        "email": "sarah.chen@email.com",
        "phone": "+1 (555) 234-5678",
        "education": "Coding Bootcamp Graduate - Le Wagon, 2022. Self-taught developer since 2020.",
        "fintech_exp": "2 years at Stripe - Developer Relations. Built payment integration demos for 50+ fintech startups. Deep knowledge of payment APIs, PCI compliance, and fraud prevention.",
        "tech_skills": "Python, TypeScript, React, Next.js, FastAPI, Stripe API, Plaid API. Strong in REST API design and webhook systems.",
        "soft_skills": "Excellent under pressure - handled live demos at conferences. Quick learner - mastered 3 new frameworks in 6 months. Great team player, mentored 10+ bootcamp students.",
        "ai_native": "Uses Cursor AI for all development. Built AI-powered invoice parser using GPT-4 Vision. Created vibe-coded prototypes that became production features. Expertise in prompt engineering for code generation."
    },
    {
        "name": "Michael Rodriguez",
        "email": "m.rodriguez@email.com",
        "phone": "+1 (555) 345-6789",
        "education": "M.S. Financial Engineering, Stanford, 2021",
        "fintech_exp": "4 years at Goldman Sachs - Algorithmic Trading Systems. Built high-frequency trading infrastructure. Experience with cryptocurrency exchanges and DeFi protocols.",
        "tech_skills": "Python, TypeScript, React, Node.js, FastAPI, GraphQL, WebSockets, PostgreSQL, TimescaleDB. Expert in real-time data pipelines.",
        "soft_skills": "Performs exceptionally under market pressure. Fast decision maker during critical trading incidents. Trains new team members on system architecture.",
        "ai_native": "Pioneer in AI-assisted trading strategies. Built LLM-powered market sentiment analyzer. Uses Claude for code reviews and debugging. Created custom MCP tools for financial data analysis."
    },
    {
        "name": "Emma Wilson",
        "email": "emma.wilson@dev.com",
        "phone": "+1 (555) 456-7890",
        "education": "B.A. Economics + Coding Bootcamp (General Assembly), 2021",
        "fintech_exp": "2.5 years at Revolut - Mobile Banking Features. Led implementation of savings goals and budgeting tools. Worked on crypto trading feature reaching 2M users.",
        "tech_skills": "TypeScript, React Native, Python, FastAPI, Django, PostgreSQL, Redis. Strong in mobile-first design and API integration.",
        "soft_skills": "Extremely adaptable - switched from economics to tech in 1 year. Works well in fast-paced startup environment. Excellent at learning from feedback.",
        "ai_native": "Uses GitHub Copilot daily. Built AI chatbot for customer support using Anthropic API. Implements RAG systems for in-app help. Experienced with vector databases and embeddings."
    },
    {
        "name": "David Kim",
        "email": "david.kim@tech.com",
        "phone": "+1 (555) 567-8901",
        "education": "Self-taught developer. High school graduate, 2019. Online courses from FreeCodeCamp, Udemy, and YouTube.",
        "fintech_exp": "3 years at Coinbase - Crypto Wallet Infrastructure. Built secure multi-signature wallet system. Experience with blockchain protocols (Bitcoin, Ethereum, Solana).",
        "tech_skills": "TypeScript, Python, React, Node.js, Rust, FastAPI, Web3.js, ethers.js. Deep understanding of cryptography and security.",
        "soft_skills": "Self-motivated learner with impressive portfolio. Handles high-stakes production issues calmly. Contributed to open-source crypto projects with 5K+ stars.",
        "ai_native": "Early adopter of AI coding tools. Built AI-powered transaction categorization system. Uses Claude and GPT-4 for architecture decisions. Created automation agents for deployment pipelines."
    },
    
    # Should PASS - Solid candidates
    {
        "name": "Lisa Martinez",
        "email": "lisa.m@email.com",
        "phone": "+1 (555) 678-9012",
        "education": "B.S. Information Systems, UC Berkeley, 2020",
        "fintech_exp": "2 years at PayPal - Merchant Services. Built dashboard for 100K+ merchants to track payments and disputes.",
        "tech_skills": "TypeScript, React, Python, Flask, PostgreSQL, Docker. Good understanding of REST APIs and OAuth2.",
        "soft_skills": "Quick learner, adapted to new tech stack in 2 months. Reliable team member who delivers on time. Good at handling customer escalations.",
        "ai_native": "Uses GitHub Copilot for development. Built simple RAG system for internal documentation. Learning about AI agents and LangChain."
    },
    {
        "name": "James Anderson",
        "email": "j.anderson@dev.com",
        "phone": "+1 (555) 789-0123",
        "education": "Bootcamp Graduate - App Academy, 2022",
        "fintech_exp": "1.5 years at Square - Point of Sale Systems. Worked on payment terminal software and backend APIs.",
        "tech_skills": "Python, TypeScript, React, Node.js, Express, MongoDB. Familiar with payment processing and PCI compliance.",
        "soft_skills": "Eager to learn and take on challenges. Works well under tight deadlines. Good communicator with stakeholders.",
        "ai_native": "Uses AI tools for code completion and debugging. Interested in building AI-powered features. Completed online course on LLM applications."
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@email.com",
        "phone": "+1 (555) 890-1234",
        "education": "B.Tech Computer Engineering, IIT Bombay, 2021",
        "fintech_exp": "2 years at Razorpay (India) - Payment Gateway Integration. Built SDKs for multiple programming languages.",
        "tech_skills": "Python, TypeScript, React, Node.js, FastAPI, Redis, RabbitMQ. Strong in async processing and webhooks.",
        "soft_skills": "Excellent problem solver. Quick to adapt to new requirements. Great at technical documentation.",
        "ai_native": "Uses Claude Code for development. Built LLM-powered code documentation tool. Exploring AI agents for testing automation."
    },
    
    # Borderline - Could PASS or FAIL
    {
        "name": "Tom Harris",
        "email": "tom.harris@email.com",
        "phone": "+1 (555) 901-2345",
        "education": "B.S. Computer Science, State University, 2020",
        "fintech_exp": "1 year at small fintech startup - Built admin dashboard for loan management system.",
        "tech_skills": "JavaScript, React, Python, Django, MySQL. Basic knowledge of TypeScript and Docker.",
        "soft_skills": "Willing to learn new technologies. Works well in small teams. Handles routine tasks efficiently.",
        "ai_native": "Occasionally uses ChatGPT for debugging. Learning about AI tools but limited hands-on experience."
    },
    {
        "name": "Nina Kowalski",
        "email": "nina.k@email.com",
        "phone": "+1 (555) 012-3456",
        "education": "Associate Degree in Web Development, Community College, 2021",
        "fintech_exp": "1.5 years at credit union - Maintained online banking portal. Fixed bugs and implemented small features.",
        "tech_skills": "JavaScript, React, Python, Flask, PostgreSQL. Some experience with REST APIs.",
        "soft_skills": "Reliable and punctual. Good at following instructions. Needs guidance on complex tasks.",
        "ai_native": "Heard about AI coding tools but hasn't used them much. Interested in learning more about AI."
    },
    
    # Should FAIL - Weak technical skills
    {
        "name": "Robert Johnson",
        "email": "robert.j@email.com",
        "phone": "+1 (555) 123-4568",
        "education": "B.A. Business Administration, 2019",
        "fintech_exp": "2 years at Wells Fargo - Business Analyst. Created Excel reports and PowerPoint presentations.",
        "tech_skills": "Excel, SQL basics, some HTML/CSS. Took online JavaScript course but no professional coding experience.",
        "soft_skills": "Good communicator. Detail-oriented with documentation. Works well in structured environments.",
        "ai_native": "No experience with AI development tools."
    },
    {
        "name": "Jennifer Lee",
        "email": "jennifer.lee@email.com",
        "phone": "+1 (555) 234-5679",
        "education": "B.S. Marketing, 2020",
        "fintech_exp": "1 year at fintech startup - Product Manager. Worked with developers but no hands-on coding.",
        "tech_skills": "Basic HTML, CSS. Familiar with Jira and Figma. No backend or framework experience.",
        "soft_skills": "Great at stakeholder management. Organized and proactive. Quick to understand business requirements.",
        "ai_native": "Uses ChatGPT for writing product specs. No development experience with AI."
    },
    {
        "name": "Kevin Brown",
        "email": "kevin.brown@email.com",
        "phone": "+1 (555) 345-6780",
        "education": "Some college courses, no degree",
        "fintech_exp": "None. 2 years as IT support at retail company.",
        "tech_skills": "Basic WordPress, HTML, CSS. Troubleshooting hardware and software issues.",
        "soft_skills": "Customer service oriented. Patient with users. Good at solving technical problems.",
        "ai_native": "No AI development experience."
    },
    
    # Should FAIL - No fintech experience
    {
        "name": "Amanda Taylor",
        "email": "amanda.taylor@email.com",
        "phone": "+1 (555) 456-7891",
        "education": "B.S. Computer Science, 2021",
        "fintech_exp": "None. 2 years at gaming company building mobile games.",
        "tech_skills": "Python, JavaScript, React, Unity, Firebase. Good technical skills but wrong domain.",
        "soft_skills": "Creative problem solver. Works well in agile teams. Passionate about user experience.",
        "ai_native": "Uses GitHub Copilot. Built AI NPCs for games. Some ML experience with TensorFlow."
    },
    {
        "name": "Chris Murphy",
        "email": "chris.murphy@email.com",
        "phone": "+1 (555) 567-8902",
        "education": "B.S. Software Engineering, 2020",
        "fintech_exp": "None. 3 years at e-commerce company - Shopify store development.",
        "tech_skills": "JavaScript, TypeScript, React, Node.js, MongoDB, Shopify API.",
        "soft_skills": "Reliable developer. Meets deadlines consistently. Good at code reviews.",
        "ai_native": "Limited AI experience. Uses ChatGPT occasionally."
    },
    
    # International candidates
    {
        "name": "Yuki Tanaka",
        "email": "yuki.tanaka@email.com",
        "phone": "+81 90-1234-5678",
        "education": "B.Eng Computer Science, Tokyo Institute of Technology, 2020",
        "fintech_exp": "3 years at Mercari - Payment Platform. Built QR code payment system. Experience with Japanese payment providers (PayPay, Line Pay).",
        "tech_skills": "TypeScript, Python, React, Go, FastAPI, PostgreSQL, Redis, Kubernetes.",
        "soft_skills": "Detail-oriented and thorough. Excellent at documentation. Works well in distributed teams.",
        "ai_native": "Uses Claude and GPT-4 for development. Built AI chatbot for customer support in Japanese and English."
    },
    {
        "name": "Dmitry Volkov",
        "email": "dmitry.volkov@email.com",
        "phone": "+7 495-123-4567",
        "education": "M.S. Applied Mathematics, Moscow State University, 2019",
        "fintech_exp": "4 years at Yandex Money - Fraud Detection Systems. Built ML models for transaction monitoring.",
        "tech_skills": "Python, TypeScript, React, FastAPI, PostgreSQL, Kafka, Spark. Expert in data pipelines and ML.",
        "soft_skills": "Analytical thinker. Handles complex technical challenges. Good at mentoring junior developers.",
        "ai_native": "Deep experience with LLMs and embeddings. Built RAG systems for financial document analysis. Uses AI for code generation daily."
    },
    
    # More diverse profiles
    {
        "name": "Maria Garcia",
        "email": "maria.garcia@email.com",
        "phone": "+34 91-123-4567",
        "education": "B.S. Computer Science, Universidad Politécnica de Madrid, 2021",
        "fintech_exp": "2 years at N26 - Digital Banking. Worked on account opening flow and KYC verification.",
        "tech_skills": "TypeScript, React, Python, FastAPI, PostgreSQL, Docker, AWS.",
        "soft_skills": "Fluent in English, Spanish, and Portuguese. Great at cross-cultural communication. Adaptable to change.",
        "ai_native": "Uses AI coding assistants. Built LLM-powered document verification. Exploring AI agents."
    },
    {
        "name": "Ahmed Hassan",
        "email": "ahmed.hassan@email.com",
        "phone": "+971 50-123-4567",
        "education": "B.S. Software Engineering, American University of Sharjah, 2020",
        "fintech_exp": "2.5 years at Emerging Markets Payments - Remittance Platform. Built cross-border payment system.",
        "tech_skills": "Python, TypeScript, React, Node.js, FastAPI, PostgreSQL, Redis.",
        "soft_skills": "Excellent problem solver. Works well under pressure. Strong communication skills.",
        "ai_native": "Regular user of GitHub Copilot. Built AI-powered currency conversion predictor. Learning about RAG systems."
    },
    {
        "name": "Sophie Dubois",
        "email": "sophie.dubois@email.com",
        "phone": "+33 1-23-45-67-89",
        "education": "Master's in Computer Science, École Polytechnique, 2021",
        "fintech_exp": "2 years at BNP Paribas - Investment Banking Platform. Built portfolio management tools.",
        "tech_skills": "TypeScript, Python, React, Angular, FastAPI, PostgreSQL, Docker.",
        "soft_skills": "Analytical and detail-oriented. Great at documentation. Collaborative team member.",
        "ai_native": "Uses AI tools for code generation and refactoring. Interested in LLM applications in finance."
    },
    {
        "name": "Carlos Silva",
        "email": "carlos.silva@email.com",
        "phone": "+55 11-9876-5432",
        "education": "B.S. Information Systems, University of São Paulo, 2020",
        "fintech_exp": "3 years at Nubank - Credit Card Platform. Built transaction processing and rewards system.",
        "tech_skills": "Python, TypeScript, React, Clojure, FastAPI, PostgreSQL, Kafka.",
        "soft_skills": "Fast learner who thrives in startup environments. Excellent at agile development. Strong problem-solving skills.",
        "ai_native": "Daily user of AI coding tools. Built RAG-powered customer support for Brazilian market. Experience with prompt engineering."
    }
]


def create_cv_pdf(candidate, output_dir):
    """Create a PDF CV for a candidate."""
    filename = f"{candidate['name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#555555',
        alignment=TA_CENTER,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor='#2563eb',
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#1a1a1a',
        spaceAfter=8,
        alignment=TA_LEFT,
        leading=14
    )
    
    # Build content
    content = []
    
    # Name
    content.append(Paragraph(candidate['name'], title_style))
    
    # Contact info
    contact = f"{candidate['email']} | {candidate['phone']}"
    content.append(Paragraph(contact, contact_style))
    
    # Education
    content.append(Paragraph("<b>EDUCATION</b>", heading_style))
    content.append(Paragraph(candidate['education'], body_style))
    
    # Experience - Fintech
    content.append(Paragraph("<b>FINTECH EXPERIENCE</b>", heading_style))
    content.append(Paragraph(candidate['fintech_exp'], body_style))
    
    # Technical Skills
    content.append(Paragraph("<b>TECHNICAL SKILLS</b>", heading_style))
    content.append(Paragraph(candidate['tech_skills'], body_style))
    
    # Soft Skills
    content.append(Paragraph("<b>SOFT SKILLS & ADAPTABILITY</b>", heading_style))
    content.append(Paragraph(candidate['soft_skills'], body_style))
    
    # AI-Native Development
    content.append(Paragraph("<b>AI-NATIVE DEVELOPMENT</b>", heading_style))
    content.append(Paragraph(candidate['ai_native'], body_style))
    
    # Build PDF
    doc.build(content)
    print(f"✓ Created: {filename}")


def main():
    """Generate all test CVs."""
    output_dir = "/Users/stiliyangoshev/Desktop/Coding/Fullstack/CV Analysis Agent/CVs"
    
    print(f"\n🚀 Generating 20 test CVs in: {output_dir}\n")
    
    for i, candidate in enumerate(CANDIDATES, 1):
        create_cv_pdf(candidate, output_dir)
    
    print(f"\n✅ Successfully generated {len(CANDIDATES)} CVs!")
    print(f"\n📊 Expected Results:")
    print("   - Strong PASS: 5 candidates (Alex, Sarah, Michael, Emma, David)")
    print("   - Solid PASS: 3 candidates (Lisa, James, Priya)")
    print("   - Borderline: 2 candidates (Tom, Nina)")
    print("   - FAIL (weak tech): 3 candidates (Robert, Jennifer, Kevin)")
    print("   - FAIL (no fintech): 2 candidates (Amanda, Chris)")
    print("   - International: 5 candidates (Yuki, Dmitry, Maria, Ahmed, Sophie, Carlos)")
    print(f"\n📁 Location: {output_dir}\n")


if __name__ == "__main__":
    main()
