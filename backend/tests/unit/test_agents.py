"""Unit tests for agent modules."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.models.hypothesis import Hypothesis, HypothesisScore
from app.models.paper import Paper


def test_agent_roles():
    """Test agent role definitions."""
    from app.models.agent import AgentRole
    
    assert AgentRole.GENERATOR == "generator"
    assert AgentRole.VALIDATOR == "validator"
    assert AgentRole.RANKER == "ranker"


def test_debate_round_creation():
    """Test debate round model."""
    from app.models.agent import DebateRound
    
    round_data = DebateRound(
        round_number=1,
        generator_hypotheses=["hyp_1"],
        validator_feedback=["Good"],
        consensus_reached=False,
    )
    
    assert round_data.round_number == 1
    assert not round_data.consensus_reached


@pytest.fixture
def sample_paper():
    """Create sample paper."""
    return Paper(
        arxiv_id="2301.12345",
        title="Test Paper",
        authors=["Alice"],
        abstract="Test abstract",
        published_date=datetime(2023, 1, 15),
        categories=["cs.AI"],
        pdf_url="https://arxiv.org/pdf/2301.12345.pdf",
    )


@pytest.fixture
def sample_hypothesis():
    """Create sample hypothesis."""
    score = HypothesisScore(
        novelty=85.0,
        feasibility=75.0,
        impact=90.0,
        overall=83.3,
    )
    
    return Hypothesis(
        id="hyp_1",
        text="Test hypothesis",
        description="Test description",
        score=score,
        source_papers=["2301.12345"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_hypothesis_score_overall(sample_hypothesis):
    """Test hypothesis overall score."""
    assert sample_hypothesis.score.overall == 83.3
    assert sample_hypothesis.score.novelty == 85.0


def test_hypothesis_status(sample_hypothesis):
    """Test hypothesis status."""
    from app.models.hypothesis import HypothesisStatus
    
    assert sample_hypothesis.status == HypothesisStatus.PENDING
