"""Quiz skill for generating and grading interactive quizzes."""

import asyncio
import json
import logging
import random
from typing import Any, Dict
import google.generativeai as genai

from src.subagents import BaseSkill, SkillResult, SkillResultStatus
from src.core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class QuizSkill(BaseSkill):
    """Skill to generate and grade interactive quizzes based on content."""

    def __init__(self):
        super().__init__(
            name="quiz",
            description="Generates and grades interactive quizzes based on content"
        )
        self.quiz_history = {}  # Store quiz attempts for grading
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_client = genai
            self.llm_model = "gemini-1.5-flash"  # Updated Gemini LLM for text generation
            self.llm = genai.GenerativeModel(self.llm_model)
        else:
            self.gemini_client = None
            self.llm = None

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """
        Execute quiz skill.
        Expected input_data keys: 'action', 'content', 'num_questions', 'quiz_id', 'answers'
        action can be 'generate', 'grade'
        """
        try:
            action = input_data.get('action', 'generate')

            if action == 'generate':
                return await self._generate_quiz(input_data)
            elif action == 'grade':
                return await self._grade_quiz(input_data)
            else:
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    data=f"Unknown action: {action}"
                )
        except Exception as e:
            logger.error(f"Error in Quiz Skill: {e}")
            return SkillResult(
                status=SkillResultStatus.ERROR,
                data=str(e)
            )

    async def _generate_quiz(self, input_data: Dict[str, Any]) -> SkillResult:
        """Generate quiz from content"""
        if not await self.validate_input(input_data):
            return SkillResult(
                status=SkillResultStatus.ERROR,
                data="Invalid input data"
            )

        content = input_data['content']
        num_questions = input_data.get('num_questions', 5)

        if self.llm is None:
            # Fallback implementation without AI
            quiz_data = {
                "questions": [
                    {
                        "question": f"Sample question about the content?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": "This is a sample explanation."
                    }
                ] * num_questions
            }
        else:
            # Create prompt for quiz generation
            quiz_prompt = f"""
            You are an expert educator creating assessment quizzes for Physical AI & Humanoid Robotics.
            Based on the following content, create {num_questions} multiple-choice questions with 4 options each.
            Include the correct answer and a brief explanation.

            Content: {content}

            Respond with a JSON array of questions in this exact format:
            {{
                "questions": [
                    {{
                        "question": "Question text here?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": "Brief explanation of why this is correct"
                    }}
                ]
            }}

            Make questions challenging but fair for intermediate developers and AI/robotics students.
            Focus on technical concepts, implementation details, and practical applications.
            """

            # Execute LLM call
            try:
                response = await self.llm.generate_content([quiz_prompt])
                quiz_json_str = response.text.strip()

                # Clean up potential markdown formatting
                if quiz_json_str.startswith("```json"):
                    quiz_json_str = quiz_json_str[7:]  # Remove ```json
                if quiz_json_str.endswith("```"):
                    quiz_json_str = quiz_json_str[:-3]  # Remove ```

                quiz_data = json.loads(quiz_json_str)
            except Exception as e:
                logger.error(f"Error generating quiz with AI: {e}")
                # Fallback to simple questions
                quiz_data = {
                    "questions": [
                        {
                            "question": f"Sample question about the content?",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "Option A",
                            "explanation": "This is a sample explanation."
                        }
                    ] * num_questions
                }

        quiz_id = f"quiz_{random.randint(1000, 9999)}"

        # Store quiz for later grading
        self.quiz_history[quiz_id] = {
            'questions': quiz_data['questions'],
            'generated_at': asyncio.get_event_loop().time()
        }

        # Format for frontend
        formatted_quiz = {
            'id': quiz_id,
            'questions': [
                {
                    'id': idx,
                    'question': q['question'],
                    'options': q['options'],
                    'explanation': q['explanation']
                }
                for idx, q in enumerate(quiz_data['questions'])
            ],
            'total_questions': len(quiz_data['questions'])
        }

        return SkillResult(
            status=SkillResultStatus.SUCCESS,
            data=formatted_quiz,
            metadata={'quiz_id': quiz_id}
        )

    async def _grade_quiz(self, input_data: Dict[str, Any]) -> SkillResult:
        """Grade submitted quiz answers"""
        quiz_id = input_data.get('quiz_id')
        user_answers = input_data.get('answers', [])

        if not quiz_id or quiz_id not in self.quiz_history:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                data="Quiz not found or expired"
            )

        stored_quiz = self.quiz_history[quiz_id]
        questions = stored_quiz['questions']

        # Grade each question
        results = []
        correct_count = 0

        for i, answer in enumerate(user_answers):
            if i >= len(questions):
                break

            question = questions[i]
            is_correct = answer.lower() == question['correct_answer'].lower()

            if is_correct:
                correct_count += 1

            results.append({
                'question_id': i,
                'is_correct': is_correct,
                'correct_answer': question['correct_answer'],
                'user_answer': answer,
                'explanation': question['explanation']
            })

        # Calculate score
        score_percentage = (correct_count / len(questions)) * 100
        passed = score_percentage >= 70  # 70% threshold

        return SkillResult(
            status=SkillResultStatus.SUCCESS,
            data={
                'score': round(score_percentage, 2),
                'passed': passed,
                'total_questions': len(questions),
                'correct_answers': correct_count,
                'results': results
            }
        )

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for quiz skill"""
        action = input_data.get('action', 'generate')

        if action == 'generate':
            return 'content' in input_data and isinstance(input_data['content'], str)
        elif action == 'grade':
            return (
                'quiz_id' in input_data and
                'answers' in input_data and
                isinstance(input_data['answers'], list)
            )
        return False


# Register the skill
from src.subagents import skill_registry
skill_registry.register_skill(QuizSkill())