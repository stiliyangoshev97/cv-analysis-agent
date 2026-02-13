"""Database seed data for initial system templates.

This module provides the "AI-First Fintech" evaluation template that
ships with the application as the default system template.

Functions:
    get_ai_fintech_template_data: Get the default template configuration.
    seed_system_templates: Create system templates in the database.

Example:
    Seeding the database::
    
        from app.db.seed import seed_system_templates
        
        async def init_db():
            async with AsyncSessionLocal() as session:
                await seed_system_templates(session)

Note:
    This should be run once during initial database setup or as
    part of the migration process.
"""

import uuid
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EvaluationTemplate, TemplateCriterion


# System template UUID (fixed for consistency across deployments)
AI_FINTECH_TEMPLATE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def get_ai_fintech_template_data() -> Dict[str, Any]:
    """Get the AI-First Fintech template configuration.
    
    This is the default system template based on the original
    CV Screening Agent evaluation criteria.
    
    Returns:
        Dictionary containing template configuration and criteria.
    
    Example:
        >>> data = get_ai_fintech_template_data()
        >>> print(data["name"])
        "AI-First Fintech"
    """
    return {
        "id": AI_FINTECH_TEMPLATE_ID,
        "name": "AI-First Fintech",
        "description": (
            "Evaluation criteria for AI-first fintech companies looking for "
            "candidates who embrace modern development practices, including "
            "AI-assisted coding."
        ),
        "is_system_template": True,
        "user_id": None,
        "passing_score": 60,
        "minimum_criteria_met": 3,
        "criteria": [
            {
                "name": "Education",
                "description": (
                    "Educational background including formal degrees, bootcamps, "
                    "certifications, or self-taught with demonstrable portfolio."
                ),
                "max_points": 15,
                "keywords": [
                    "Bachelor", "Master", "PhD", "Computer Science",
                    "Software Engineering", "Bootcamp", "Certification",
                    "Self-taught", "Portfolio", "GitHub"
                ],
                "evaluation_guidelines": (
                    "Award points for: formal CS/SE degrees (high), bootcamp graduates (medium), "
                    "self-taught with strong portfolio (medium), any technical education (low). "
                    "High school alone with no tech background scores minimal points."
                ),
                "is_required": False,
                "sort_order": 1,
            },
            {
                "name": "Fintech Experience",
                "description": (
                    "Experience in financial technology, banking, payments, "
                    "cryptocurrency, DeFi, or related financial services."
                ),
                "max_points": 20,
                "keywords": [
                    "Fintech", "Banking", "Payments", "Crypto", "Cryptocurrency",
                    "DeFi", "Blockchain", "Trading", "Investment", "Financial Services",
                    "Insurance", "RegTech", "Lending", "Wallet", "Exchange"
                ],
                "evaluation_guidelines": (
                    "Award full points for direct fintech startup experience. "
                    "High points for banking/financial services tech roles. "
                    "Medium points for crypto/blockchain projects. "
                    "Lower points for tangentially related finance experience."
                ),
                "is_required": False,
                "sort_order": 2,
            },
            {
                "name": "Technical Skills",
                "description": (
                    "Programming languages, frameworks, and technical tools "
                    "relevant to modern full-stack development."
                ),
                "max_points": 25,
                "keywords": [
                    "TypeScript", "JavaScript", "Python", "React", "Node.js",
                    "FastAPI", "Next.js", "PostgreSQL", "MongoDB", "Redis",
                    "Docker", "Kubernetes", "AWS", "GCP", "Azure",
                    "REST API", "GraphQL", "Git", "CI/CD", "Testing"
                ],
                "evaluation_guidelines": (
                    "This is a REQUIRED criterion for passing. "
                    "Full points for: TypeScript + Python + React + modern backend. "
                    "High points for strong full-stack with 3+ key technologies. "
                    "Medium points for specialized backend or frontend expertise. "
                    "Low points for outdated tech stack or limited experience."
                ),
                "is_required": True,
                "sort_order": 3,
            },
            {
                "name": "Soft Skills & Adaptability",
                "description": (
                    "Communication, teamwork, fast learning ability, "
                    "and ability to work under pressure in startup environments."
                ),
                "max_points": 20,
                "keywords": [
                    "Leadership", "Team", "Communication", "Agile", "Scrum",
                    "Fast learner", "Adaptable", "Problem solving", "Startup",
                    "Remote work", "Collaboration", "Mentoring", "Initiative"
                ],
                "evaluation_guidelines": (
                    "Look for evidence of: startup experience (fast-paced), "
                    "leadership or mentoring roles, cross-functional collaboration, "
                    "rapid skill acquisition, working under pressure. "
                    "Award higher points for demonstrated adaptability and growth."
                ),
                "is_required": False,
                "sort_order": 4,
            },
            {
                "name": "AI-Native Development",
                "description": (
                    "Experience with AI coding tools, RAG systems, MCP protocol, "
                    "LLM integration, and AI agent development."
                ),
                "max_points": 20,
                "keywords": [
                    "AI", "LLM", "ChatGPT", "Claude", "Copilot", "Cursor",
                    "Windsurf", "RAG", "Vector database", "Embeddings",
                    "LangChain", "LlamaIndex", "MCP", "Model Context Protocol",
                    "AI Agent", "Prompt Engineering", "Fine-tuning", "OpenAI API",
                    "Anthropic", "Gemini", "Vibe coding"
                ],
                "evaluation_guidelines": (
                    "Full points for: AI agent development experience + RAG systems + MCP knowledge. "
                    "High points for: Regular use of AI coding assistants (Copilot, Cursor, Claude Code). "
                    "Medium points for: LLM API integration in projects. "
                    "Low points for: Basic awareness of AI tools without practical use. "
                    "This is a differentiator for AI-first companies."
                ),
                "is_required": False,
                "sort_order": 5,
            },
        ],
    }


async def seed_system_templates(session: AsyncSession) -> None:
    """Create system evaluation templates in the database.
    
    Checks if the AI-First Fintech template exists and creates it
    if not present. Safe to call multiple times (idempotent).
    
    Args:
        session: Async database session.
    
    Example:
        >>> async with AsyncSessionLocal() as session:
        ...     await seed_system_templates(session)
        ...     await session.commit()
    """
    # Check if template already exists
    result = await session.execute(
        select(EvaluationTemplate).where(
            EvaluationTemplate.id == AI_FINTECH_TEMPLATE_ID
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        print("System template 'AI-First Fintech' already exists, skipping seed.")
        return
    
    # Get template data
    data = get_ai_fintech_template_data()
    criteria_data = data.pop("criteria")
    
    # Create template
    template = EvaluationTemplate(**data)
    session.add(template)
    
    # Flush to get template ID
    await session.flush()
    
    # Create criteria
    for criterion_data in criteria_data:
        criterion = TemplateCriterion(
            template_id=template.id,
            **criterion_data
        )
        session.add(criterion)
    
    await session.commit()
    print(f"Created system template: {template.name}")


async def seed_database(session: AsyncSession) -> None:
    """Run all database seed operations.
    
    This is the main entry point for seeding the database with
    initial data required for the application to function.
    
    Args:
        session: Async database session.
    
    Example:
        >>> async with AsyncSessionLocal() as session:
        ...     await seed_database(session)
    """
    await seed_system_templates(session)
    # Add additional seed operations here as needed
