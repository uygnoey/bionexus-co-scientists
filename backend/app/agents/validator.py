"""Validator agent for hypothesis validation."""
from typing import List, Dict
from anthropic import Anthropic

from app.core.config import settings
from app.core.logging import get_logger
from app.models.hypothesis import Hypothesis

logger = get_logger(__name__)


class ValidatorAgent:
    """Agent responsible for validating hypotheses."""

    SYSTEM_PROMPT = """당신은 과학적 엄밀함을 검증하는 비평가입니다.

제안된 가설의 타당성을 평가하세요.

체크리스트:
1. 논리적 일관성
2. 증거 기반 추론
3. 편향 검사
4. 실험 설계 가능성

각 가설에 점수(0-100)와 피드백을 제공하세요.

출력 형식 (JSON):
{
  "validations": [
    {
      "hypothesis_id": "hyp_xxx",
      "score": 75.0,
      "feedback": ["긍정적 피드백", "개선 사항"],
      "pass": true
    }
  ]
}
"""

    def __init__(self) -> None:
        """Initialize validator agent."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.validator_model

    async def validate(self, hypotheses: List[Hypothesis]) -> Dict[str, Dict]:
        """Validate hypotheses.
        
        Args:
            hypotheses: List of hypotheses to validate
            
        Returns:
            Dict mapping hypothesis IDs to validation results
        """
        logger.info(f"Validating {len(hypotheses)} hypotheses")
        
        # Build prompt
        hypotheses_text = "\n\n".join([
            f"ID: {h.id}\n{h.text}\n{h.description}"
            for h in hypotheses
        ])
        
        user_prompt = f"""## Hypotheses to Validate
{hypotheses_text}

위 가설들을 검증하고 JSON 형식으로 결과를 제공하세요."""
        
        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        
        # Parse response
        import json
        
        response_text = response.content[0].text
        
        try:
            data = json.loads(response_text)
            validations = data.get("validations", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse validation JSON")
            validations = []
        
        # Build result dict
        results = {}
        for v in validations:
            hyp_id = v.get("hypothesis_id")
            if hyp_id:
                results[hyp_id] = {
                    "score": v.get("score", 50.0),
                    "feedback": v.get("feedback", []),
                    "pass": v.get("pass", False),
                }
        
        logger.info(f"Validated {len(results)} hypotheses")
        return results
