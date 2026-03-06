"""Generator agent for hypothesis generation."""
from typing import List, Dict, Any
from anthropic import Anthropic

from app.core.config import settings
from app.core.logging import get_logger
from app.models.hypothesis import Hypothesis, HypothesisScore
from app.models.paper import Paper

logger = get_logger(__name__)


class GeneratorAgent:
    """Agent responsible for generating creative hypotheses."""

    SYSTEM_PROMPT = """당신은 과학 논문에서 창의적인 가설을 생성하는 연구원입니다.

주어진 RAG 컨텍스트를 바탕으로 3-5개의 참신한 가설을 제안하세요.

평가 기준:
- 참신성 (Novelty): 기존 연구와 차별화
- 실현 가능성 (Feasibility): 검증 가능한 방법론
- 영향력 (Impact): 학문적 기여도

출력 형식 (JSON):
{
  "hypotheses": [
    {
      "text": "가설 문장",
      "description": "상세 설명",
      "novelty_score": 85.0,
      "feasibility_score": 75.0,
      "impact_score": 90.0,
      "evidence": ["논문 ID 또는 인용구"]
    }
  ]
}
"""

    def __init__(self) -> None:
        """Initialize generator agent."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.generator_model

    async def generate(
        self, papers: List[Paper], rag_context: str
    ) -> List[Hypothesis]:
        """Generate hypotheses from papers.
        
        Args:
            papers: List of source papers
            rag_context: RAG retrieved context
            
        Returns:
            List of generated hypotheses
        """
        logger.info(f"Generating hypotheses from {len(papers)} papers")
        
        # Build prompt
        paper_summaries = "\n\n".join([
            f"[{p.arxiv_id}] {p.title}\n{p.abstract}"
            for p in papers[:10]
        ])
        
        user_prompt = f"""## RAG Context
{rag_context}

## Papers
{paper_summaries}

위 논문들을 기반으로 3-5개의 창의적인 가설을 JSON 형식으로 제안하세요."""
        
        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        
        # Parse response
        import json
        import uuid
        from datetime import datetime
        
        response_text = response.content[0].text
        
        try:
            data = json.loads(response_text)
            hypotheses_data = data.get("hypotheses", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, using fallback")
            hypotheses_data = []
        
        hypotheses = []
        for h_data in hypotheses_data:
            score = HypothesisScore(
                novelty=h_data.get("novelty_score", 50.0),
                feasibility=h_data.get("feasibility_score", 50.0),
                impact=h_data.get("impact_score", 50.0),
                overall=(
                    h_data.get("novelty_score", 50.0)
                    + h_data.get("feasibility_score", 50.0)
                    + h_data.get("impact_score", 50.0)
                )
                / 3.0,
            )
            
            hypothesis = Hypothesis(
                id=f"hyp_{uuid.uuid4().hex[:8]}",
                text=h_data.get("text", ""),
                description=h_data.get("description", ""),
                score=score,
                source_papers=[p.arxiv_id for p in papers],
                generated_by="generator",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            hypotheses.append(hypothesis)
        
        logger.info(f"Generated {len(hypotheses)} hypotheses")
        return hypotheses
