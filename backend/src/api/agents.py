"""Agent orchestration API for the AI Book project."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
import asyncio
import logging

from src.subagents import skill_registry, SkillResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agents")


class AgentRequest(BaseModel):
    """Request model for agent orchestration."""
    skills: List[str]
    input_data: Dict[str, Any]
    config: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Response model for agent orchestration."""
    results: List[Dict[str, Any]]
    status: str  # success, partial, error
    execution_time: float


@router.post("/orchestrate", response_model=AgentResponse)
async def orchestrate_agent(request: AgentRequest):
    """Orchestrate multiple skills execution."""
    try:
        start_time = asyncio.get_event_loop().time()
        results = []

        # Execute skills concurrently
        tasks = []
        for skill_name in request.skills:
            skill = skill_registry.get_skill(skill_name)
            if skill:
                task = asyncio.create_task(
                    skill.execute(request.input_data)
                )
                tasks.append(task)
            else:
                results.append({
                    'skill': skill_name,
                    'result': {
                        'status': 'error',
                        'data': f'Skill "{skill_name}" not found'
                    }
                })

        # Wait for all tasks to complete
        skill_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, skill_name in enumerate(request.skills):
            if i < len(skill_results) and not isinstance(skill_results[i], Exception):
                result: SkillResult = skill_results[i]
                results.append({
                    'skill': skill_name,
                    'result': {
                        'status': result.status.value,
                        'data': result.data,
                        'metadata': result.metadata
                    }
                })
            elif i < len(skill_results):
                results.append({
                    'skill': skill_name,
                    'result': {
                        'status': 'error',
                        'data': str(skill_results[i])
                    }
                })

        # Determine overall status
        has_error = any(r['result']['status'] == 'error' for r in results)
        has_partial = any(r['result']['status'] == 'partial' for r in results)

        overall_status = 'error' if has_error else ('partial' if has_partial else 'success')

        execution_time = asyncio.get_event_loop().time() - start_time

        return AgentResponse(
            results=results,
            status=overall_status,
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Error in agent orchestration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills")
async def get_available_skills():
    """Get list of available skills."""
    try:
        skills = skill_registry.get_available_skills()
        return {
            'skills': [
                {
                    'name': skill.name,
                    'description': skill.description
                }
                for skill in skills
            ]
        }
    except Exception as e:
        logger.error(f"Error getting available skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    