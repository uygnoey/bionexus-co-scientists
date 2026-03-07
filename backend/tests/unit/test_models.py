"""Unit tests for Pydantic models."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.hypothesis import (
    Hypothesis,
    HypothesisScore,
    HypothesisStatus,
    HypothesisGenerationRequest,
)
from app.models.paper import Paper, Entity, EntityType, Relationship, RelationType
from app.models.agent import AgentRole, AgentStatus, DebateRound


def test_hypothesis_score_valid():
    """Test HypothesisScore with valid data."""
    score = HypothesisScore(
        novelty=85.0,
        feasibility=75.0,
        impact=90.0,
        overall=83.3,
    )
    
    assert score.novelty == 85.0
    assert score.feasibility == 75.0
    assert score.impact == 90.0
    assert score.overall == 83.3


def test_hypothesis_score_invalid_range():
    """Test HypothesisScore with out-of-range values."""
    with pytest.raises(ValidationError):
        HypothesisScore(
            novelty=150.0,  # > 100
            feasibility=75.0,
            impact=90.0,
            overall=83.3,
        )


def test_hypothesis_creation():
    """Test Hypothesis model creation."""
    score = HypothesisScore(
        novelty=85.0,
        feasibility=75.0,
        impact=90.0,
        overall=83.3,
    )
    
    hyp = Hypothesis(
        id="hyp_123",
        text="Test hypothesis",
        description="Test description",
        score=score,
        source_papers=["2301.12345"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    assert hyp.id == "hyp_123"
    assert hyp.text == "Test hypothesis"
    assert hyp.score.overall == 83.3
    assert hyp.status == HypothesisStatus.PENDING  # default


def test_paper_creation():
    """Test Paper model creation."""
    paper = Paper(
        arxiv_id="2301.12345",
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="Abstract",
        published_date=datetime(2023, 1, 15),
        categories=["cs.AI"],
        pdf_url="https://arxiv.org/pdf/2301.12345.pdf",
    )
    
    assert paper.arxiv_id == "2301.12345"
    assert len(paper.authors) == 2
    assert paper.authors[0] == "Alice"


def test_entity_creation():
    """Test Entity model creation."""
    entity = Entity(
        id="ent_1",
        name="Quantum Computing",
        type=EntityType.CONCEPT,
        mention_count=5,
        confidence=0.95,
    )
    
    assert entity.id == "ent_1"
    assert entity.type == EntityType.CONCEPT
    assert entity.mention_count == 5


def test_relationship_creation():
    """Test Relationship model creation."""
    rel = Relationship(
        id="rel_1",
        source_id="ent_1",
        target_id="ent_2",
        type=RelationType.USES,
        confidence=0.9,
        paper_id="2301.12345",
    )
    
    assert rel.type == RelationType.USES
    assert rel.confidence == 0.9


def test_hypothesis_generation_request_valid():
    """Test HypothesisGenerationRequest validation."""
    request = HypothesisGenerationRequest(
        paper_ids=["2301.12345", "2302.67890"],
        max_hypotheses=5,
        debate_rounds=3,
    )
    
    assert len(request.paper_ids) == 2
    assert request.max_hypotheses == 5


def test_hypothesis_generation_request_invalid():
    """Test HypothesisGenerationRequest with invalid data."""
    # Too many papers
    with pytest.raises(ValidationError):
        HypothesisGenerationRequest(
            paper_ids=["paper_" + str(i) for i in range(25)],  # > 20
            max_hypotheses=5,
        )
    
    # Too many hypotheses
    with pytest.raises(ValidationError):
        HypothesisGenerationRequest(
            paper_ids=["2301.12345"],
            max_hypotheses=15,  # > 10
        )


def test_debate_round_creation():
    """Test DebateRound model."""
    round_data = DebateRound(
        round_number=1,
        generator_hypotheses=["hyp_1", "hyp_2"],
        validator_feedback=["Good", "Needs work"],
        consensus_reached=False,
    )
    
    assert round_data.round_number == 1
    assert len(round_data.generator_hypotheses) == 2
    assert round_data.consensus_reached is False
