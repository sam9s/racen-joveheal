"""
Script to ingest the Career Healing Course transcript with proper emotional pattern tagging.

This transcript contains rich content about:
- Root causes of career struggles (parental resentment, childhood patterns)
- How emotions manifest across career, relationships, and health
- The blueprint concept (subconscious beliefs, conditioning, patterns)
- Healing techniques and frameworks
"""

from pathlib import Path
from knowledge_base import ingest_enhanced_coaching_transcript


CAREER_HEALING_PATTERNS = [
    "not_enough",
    "fear_of_judgment", 
    "rejection",
    "seeking_validation",
    "boundary_issues",
    "stuck_patterns",
    "parental_resentment",
    "overwhelm_exhaustion",
    "misalignment"
]

CAREER_HEALING_ROOT_CAUSES = [
    "unresolved_parental_resentment",
    "childhood_comparison",
    "conditional_love",
    "emotional_neglect",
    "critical_controlling_parents",
    "fear_of_speaking_up",
    "not_feeling_heard",
    "seeking_external_validation",
    "overworking_pattern",
    "blueprint_limiting_beliefs"
]


def ingest_career_healing_transcript():
    """Ingest the Career Healing Course transcript."""
    
    transcript_path = Path("attached_assets/Career_Healing_Course_Clean_1765861933864.md")
    
    if not transcript_path.exists():
        print(f"Transcript not found at {transcript_path}")
        return 0
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith("# "):
        lines = content.split("\n")
        content = "\n".join(lines[1:])
    
    chunks_added = ingest_enhanced_coaching_transcript(
        text_content=content,
        video_title="Career Healing Course - Masterclass",
        primary_pillar="career",
        emotional_patterns=CAREER_HEALING_PATTERNS,
        root_causes=CAREER_HEALING_ROOT_CAUSES,
        speaker="Shweta",
        youtube_url=None,
        session_type="masterclass"
    )
    
    print(f"\n=== Career Healing Course Ingestion Complete ===")
    print(f"Total chunks added: {chunks_added}")
    print(f"Emotional patterns tagged: {len(CAREER_HEALING_PATTERNS)}")
    print(f"Root causes tagged: {len(CAREER_HEALING_ROOT_CAUSES)}")
    
    return chunks_added


if __name__ == "__main__":
    ingest_career_healing_transcript()
