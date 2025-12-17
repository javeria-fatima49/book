"""Subagents module for the AI Book project."""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SkillResultStatus(Enum):
    """Enumeration of possible skill execution statuses."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    TIMEOUT = "timeout"


class SkillResult(BaseModel):
    """Represents the result of a skill execution."""

    status: SkillResultStatus
    data: Any
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = None

    def model_post_init(self, __context):
        """Set timestamp after model initialization."""
        self.timestamp = asyncio.get_event_loop().time()


class BaseSkill(ABC):
    """Base class for all subagent skills."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.is_available = True

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """Execute the skill with given input data."""
        pass

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data before execution."""
        return True

    async def preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess input data before execution."""
        return input_data


class SkillRegistry:
    """Central registry for managing available skills."""

    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}

    def register_skill(self, skill: BaseSkill):
        """Register a new skill."""
        self.skills[skill.name] = skill
        print(f"Registered skill: {skill.name}")

    def get_skill(self, skill_name: str) -> BaseSkill:
        """Get a registered skill by name."""
        return self.skills.get(skill_name)

    def get_available_skills(self) -> List[BaseSkill]:
        """Get list of all available skills."""
        return [skill for skill in self.skills.values() if skill.is_available]

    async def execute_skill(self, skill_name: str, input_data: Dict[str, Any]) -> SkillResult:
        """Execute a skill by name."""
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")
        return await skill.execute(input_data)


# Global skill registry instance
skill_registry = SkillRegistry()