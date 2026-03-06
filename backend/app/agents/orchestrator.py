"""Orchestrator for multi-agent hypothesis generation pipeline."""
from typing import List
import time

from app.core.logging import get_logger
from app.models.paper import Paper
from app.models.hypothesis import Hypothesis, HypothesisGenerationResponse, HypothesisStatus
from app.agents.generator import GeneratorAgent
from app.agents.validator import ValidatorAgent
from app.agents.ranker import RankerAgent
from app.agents.debate import DebateSystem

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates the multi-agent hypothesis generation pipeline."""

    def __init__(self) -> None:
        """Initialize orchestrator."""
        self.generator = GeneratorAgent()
        self.validator = ValidatorAgent()
        self.ranker = RankerAgent()
        self.debate_system = DebateSystem()

    async def generate_hypotheses(
        self,
        papers: List[Paper],
        rag_context: str,
        max_hypotheses: int = 5,
    ) -> HypothesisGenerationResponse:
        """Run complete hypothesis generation pipeline.
        
        Args:
            papers: Source papers
            rag_context: RAG retrieved context
            max_hypotheses: Maximum hypotheses to generate
            
        Returns:
            HypothesisGenerationResponse with results
        """
        import uuid
        
        start_time = time.time()
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        
        logger.info(
            "Starting hypothesis generation pipeline",
            request_id=request_id,
            num_papers=len(papers),
        )
        
        # Step 1: Generate hypotheses
        logger.info("Step 1: Generating hypotheses")
        hypotheses = await self.generator.generate(papers, rag_context)
        hypotheses = hypotheses[:max_hypotheses]
        
        if not hypotheses:
            logger.warning("No hypotheses generated")
            return HypothesisGenerationResponse(
                request_id=request_id,
                hypotheses=[],
                clusters=[],
                total_papers=len(papers),
                generation_time_seconds=time.time() - start_time,
                status=HypothesisStatus.FAILED,
            )
        
        # Step 2: Validate hypotheses
        logger.info(f"Step 2: Validating {len(hypotheses)} hypotheses")
        validator_results = await self.validator.validate(hypotheses)
        
        # Update hypotheses with validation results
        for hyp in hypotheses:
            if hyp.id in validator_results:
                result = validator_results[hyp.id]
                hyp.score.validator_score = result["score"]
                hyp.feedback = result["feedback"]
                hyp.validated_by = "validator"
        
        # Step 3: Debate
        logger.info("Step 3: Running debate")
        debate_rounds = await self.debate_system.run_debate(
            hypotheses, validator_results
        )
        
        # Step 4: Rank hypotheses
        logger.info("Step 4: Ranking hypotheses")
        ranked_hypotheses = await self.ranker.rank(hypotheses)
        
        # Update status
        for hyp in ranked_hypotheses:
            hyp.status = HypothesisStatus.COMPLETED
        
        generation_time = time.time() - start_time
        
        logger.info(
            "Pipeline completed",
            request_id=request_id,
            num_hypotheses=len(ranked_hypotheses),
            generation_time=generation_time,
        )
        
        return HypothesisGenerationResponse(
            request_id=request_id,
            hypotheses=ranked_hypotheses,
            clusters=[],  # TODO: Clustering
            total_papers=len(papers),
            generation_time_seconds=generation_time,
            status=HypothesisStatus.COMPLETED,
        )
