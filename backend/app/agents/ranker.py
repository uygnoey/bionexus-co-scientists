"""Ranker agent for final hypothesis ranking."""
from typing import List
from anthropic import Anthropic

from app.core.config import settings
from app.core.logging import get_logger
from app.models.hypothesis import Hypothesis

logger = get_logger(__name__)


class RankerAgent:
    """Agent responsible for final ranking."""

    SYSTEM_PROMPT = """당신은 최종 순위를 결정하는 심사위원장입니다.

토론 결과를 바탕으로 가설의 최종 순위를 매기세요.

고려 사항:
- Generator의 창의성
- Validator의 검증 결과
- 실제 연구 가치

출력 형식 (JSON):
{
  "rankings": [
    {
      "hypothesis_id": "hyp_xxx",
      "rank": 1,
      "final_score": 85.0,
      "rationale": "순위 근거"
    }
  ]
}
"""

    def __init__(self) -> None:
        """Initialize ranker agent."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.ranker_model

    async def rank(self, hypotheses: List[Hypothesis]) -> List[Hypothesis]:
        """Rank hypotheses.
        
        Args:
            hypotheses: List of hypotheses to rank
            
        Returns:
            Sorted list of hypotheses
        """
        logger.info(f"Ranking {len(hypotheses)} hypotheses")
        
        # Build prompt
        hypotheses_text = "\n\n".join([
            f"ID: {h.id}\nText: {h.text}\nScores: {h.score.model_dump()}"
            for h in hypotheses
        ])
        
        user_prompt = f"""## Hypotheses
{hypotheses_text}

위 가설들을 순위 매기고 JSON 형식으로 결과를 제공하세요."""
        
        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        
        # Parse and sort
        import json
        
        response_text = response.content[0].text
        
        try:
            data = json.loads(response_text)
            rankings = data.get("rankings", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse ranking JSON, using original order")
            return hypotheses
        
        # Sort by rank
        id_to_rank = {r["hypothesis_id"]: r["rank"] for r in rankings}
        sorted_hypotheses = sorted(
            hypotheses, key=lambda h: id_to_rank.get(h.id, 999)
        )
        
        logger.info(f"Ranked {len(sorted_hypotheses)} hypotheses")
        return sorted_hypotheses
