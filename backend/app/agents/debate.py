"""Debate system for agent collaboration."""
from typing import List
from app.core.logging import get_logger
from app.models.hypothesis import Hypothesis
from app.models.agent import DebateRound, AgentMessage, AgentRole

logger = get_logger(__name__)


class DebateSystem:
    """Manages debate between Generator and Validator."""

    def __init__(self, max_rounds: int = 3) -> None:
        """Initialize debate system.
        
        Args:
            max_rounds: Maximum debate rounds
        """
        self.max_rounds = max_rounds

    async def run_debate(
        self,
        hypotheses: List[Hypothesis],
        validator_results: dict,
    ) -> List[DebateRound]:
        """Run debate between agents.
        
        Args:
            hypotheses: Initial hypotheses from Generator
            validator_results: Validation results
            
        Returns:
            List of debate rounds
        """
        logger.info(f"Starting debate with {len(hypotheses)} hypotheses")
        
        rounds: List[DebateRound] = []
        
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"Debate round {round_num}/{self.max_rounds}")
            
            round_data = DebateRound(
                round_number=round_num,
                generator_hypotheses=[h.id for h in hypotheses],
            )
            
            # Validator feedback
            for hyp in hypotheses:
                validation = validator_results.get(hyp.id, {})
                feedback_text = " ".join(validation.get("feedback", []))
                
                message = AgentMessage(
                    from_agent=AgentRole.VALIDATOR,
                    to_agent=AgentRole.GENERATOR,
                    message=feedback_text,
                    message_type="feedback",
                    hypothesis_id=hyp.id,
                    round_number=round_num,
                )
                round_data.messages.append(message)
                round_data.validator_feedback.append(feedback_text)
                round_data.validator_scores[hyp.id] = validation.get("score", 50.0)
            
            # Check consensus
            passing = [
                hyp for hyp in hypotheses
                if validator_results.get(hyp.id, {}).get("pass", False)
            ]
            
            if len(passing) >= len(hypotheses) * 0.7:  # 70% pass threshold
                round_data.consensus_reached = True
                round_data.consensus_hypotheses = [h.id for h in passing]
                rounds.append(round_data)
                logger.info(f"Consensus reached in round {round_num}")
                break
            
            rounds.append(round_data)
        
        logger.info(f"Debate completed after {len(rounds)} rounds")
        return rounds
