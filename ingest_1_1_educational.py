#!/usr/bin/env python3
"""
Ingest educational coaching concepts from 1-to-1 sessions.

This script ingests ONLY the educational/conceptual content extracted from
Shweta's 1-to-1 sessions. It explicitly excludes:
- Therapeutic intervention scripts
- Guided meditation/hypnosis language
- Energy healing/chakra work procedures
- Physical healing claims

The goal is to give SOMERA conceptual understanding without the ability
to replicate therapeutic interventions.
"""

import os
from knowledge_base import ingest_enhanced_coaching_transcript

EDUCATIONAL_CHUNKS = [
    {
        "content": """The "One Win" Opening Ritual: Every coaching session starts by asking the client to share "one win" - even if it's very small. This can be something they've achieved, a pattern change they're noticing in themselves, something they're proud of, or even a small thing that made a difference. This shifts focus to growth and progress, builds self-awareness about positive changes, creates momentum for the session, and reminds them they ARE making progress even when it doesn't feel like it.""",
        "topic": "coaching_framework",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["not_enough", "overwhelm_exhaustion"],
        "pillars": ["career", "relationship", "wellness"],
        "root_causes": ["conditional love", "external validation"],
    },
    {
        "content": """The Blueprint Concept: Everyone operates from a subconscious "blueprint" - a collection of beliefs, emotions, conditioning, and patterns developed mostly in childhood. This blueprint decides how you react to situations, shapes how you lead and live, determines how much you allow yourself to receive, and creates automatic responses that feel like "just who I am." Surface-level fixes don't work if the deep patterns aren't addressed. The same patterns will keep recreating the same situations. Beliefs are never bad - they serve us, then they start blocking us. When they start blocking us, they become limiting beliefs.""",
        "topic": "blueprint_concept",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["not_enough", "rejection", "fear_of_judgment"],
        "pillars": ["career", "relationship", "wellness"],
        "root_causes": ["childhood conditioning", "protective patterns"],
    },
    {
        "content": """The Time Relationship Pattern: Many people have an unhealthy relationship with time - feeling controlled BY time rather than in control OF time. Common phrases that signal this pattern: "I don't have time," "I don't have enough time," "There's never enough time." This often stems from obligation patterns, where every moment feels spoken for by duties, tasks, and others' needs. The experience of time is subjective and can shift. Signs include: rest feels irresponsible, everything feels urgent and non-negotiable, can't pursue passions because practical things must come first, burnout from constant hamster wheel feeling.""",
        "topic": "time_patterns",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["overwhelm_exhaustion", "control_perfectionism"],
        "pillars": ["career", "wellness"],
        "root_causes": ["duty conditioning", "self-neglect patterns"],
    },
    {
        "content": """The Money Energy Relationship: Our relationship with money is often shaped by childhood experiences and parental messaging. Common money beliefs to explore: "Money is not enough," "Money needs to be saved, kept, not let go," "Money can be bad and cause problems," "It's hard to earn money," "I don't know how to be responsible about money." Questions to explore: What were the three things you thought about money growing up? Do you remember a specific moment when you learned something about money? Where in your body do you feel that when you think about money?""",
        "topic": "money_patterns",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["not_enough", "unworthiness"],
        "pillars": ["career", "wellness"],
        "root_causes": ["parental messaging", "scarcity conditioning"],
    },
    {
        "content": """Support and Back Pain Connection: Physical symptoms often carry emotional/psychological messages. In this framework, back represents support, burden, and financial security. Lower back pain is often connected to feeling unsupported, frequently related to father relationships. Questions to explore: Do you feel supported in your life right now? When did your back pain start? What was happening in your life then? Is there a connection between when you started feeling unsupported and when the pain began? Note: This is a conceptual connection for self-reflection, not a medical claim.""",
        "topic": "body_mind_connection",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["lack_of_support", "unworthiness"],
        "pillars": ["wellness", "relationship"],
        "root_causes": ["father wound", "feeling unsupported"],
    },
    {
        "content": """The Power Reclamation Framework: We unconsciously "give our power away" to people and situations. When triggered, it's often because someone made us doubt ourselves, a situation activated an old wound, or we're replaying a pattern from the past. Recognition exercise: Think about every incident which has taken your power away in the past few weeks. Common power-giving patterns include: doubting yourself when someone questions you, feeling like you have to do everything because you can't rely on anyone, taking on responsibility that isn't yours, shrinking when criticized, needing external validation to feel okay. The deeper question: "Is it right to say 'I can't expect anything from anyone. I have to do it all'?" """,
        "topic": "power_patterns",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["rejection", "control_perfectionism", "not_enough"],
        "pillars": ["career", "relationship"],
        "root_causes": ["loss of parent", "hyper-responsibility", "early independence"],
    },
    {
        "content": """The Chocolate Analogy - A perspective-shifting framework for handling setbacks: Imagine you have 100 chocolates and you're crossing the road. One chocolate falls. Will you cry over the one, or move ahead with your 99 chocolates? When someone has been doing well but one incident shakes them, remind them: Don't let one setback erase all progress. Count the wins, not just the loss. Eight incidents where you were regulated, one incident shook you - will you ignore everything else you did? Growth framing: You are still learning. Compare yourself to six months ago. Life is challenging, sometimes challenges come unexpectedly. The choice is to blame yourself, or to say "at least 99 times out of 100, I was fine." """,
        "topic": "perspective_reframe",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["not_enough", "unworthiness"],
        "pillars": ["career", "relationship", "wellness"],
        "root_causes": ["perfectionism", "self-criticism"],
    },
    {
        "content": """The Approval Pattern: Many people's happiness becomes dependent on external validation, especially from a partner or parent. Signs of approval dependency: "My feelings are dependent on how he/she is treating me," "If he's good with me, I'm happy. If he's bad with me, I'm sad," only hearing criticism never praise, needing to ask "Are you noticing something good in me?" Root causes often include: overly critical parent/partner, lack of appreciation growing up, being made to feel bad repeatedly, never hearing positive feedback. Key insight: "Why is that approval so important?" - The need for external validation often masks a deeper wound. Self-validation practice: What would the old version of you say to the current you?""",
        "topic": "approval_patterns",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["unworthiness", "not_enough", "rejection"],
        "pillars": ["relationship", "career"],
        "root_causes": ["critical parenting", "conditional love", "external validation"],
    },
    {
        "content": """Standing For Yourself: There's a difference between praising yourself when things go well vs. standing for yourself when things get hard. Key insight: "Praising yourself is very easy. Standing for yourself when life gives difficulty - that's harder." Signs of not standing for yourself: Taking blame that isn't yours, feeling like a failure when someone else mistreats you, asking "What was MY mistake?" when someone else was wrong, being made to feel bad and accepting it. Coaching approach: Ask "What was YOUR mistake in all this?" - often the answer is nothing. Help them see when they're taking responsibility for others' behavior. "It's not always you. Sometimes it's their part too." """,
        "topic": "self_worth",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["unworthiness", "boundary_issues"],
        "pillars": ["relationship", "career"],
        "root_causes": ["self-blame pattern", "taking others' responsibility"],
    },
    {
        "content": """Cross-Pillar Pattern Recognition: Patterns don't stay in one area - they show up across career, relationships, and wellness simultaneously. Examples: "I can't expect anything from anyone. I have to do it all" shows up at work AND in relationships. Feeling unsupported by father shows up as back pain AND career insecurity AND relationship dynamics. Approval-seeking shows up with boss AND with partner. Coaching approach: When someone shares an issue in one area, explore: "Do you notice this pattern in other areas of your life too?" "Sometimes what we feel at work is connected to what we feel at home." "I'm curious — does this remind you of anything from earlier in your life?" """,
        "topic": "cross_pillar_awareness",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": ["rejection", "not_enough", "unworthiness", "boundary_issues"],
        "pillars": ["career", "relationship", "wellness"],
        "root_causes": ["childhood patterns", "family dynamics"],
    },
    {
        "content": """When to Refer to Live Sessions: Some work requires Shweta's direct intervention and cannot be done through a chatbot. Refer when user mentions: wanting to "release" or "heal" specific trauma, needing guided meditation or visualization, physical symptoms they want to address, ancestral patterns or generational healing, deep regression to childhood memories, energy work or chakra healing, wanting their "blueprint" cleared. SOMERA can: listen and provide empathetic support, help users understand patterns conceptually, share educational frameworks, ask coaching questions that help users gain clarity, normalize experiences and reduce shame, guide them toward the decision to seek deeper work.""",
        "topic": "referral_boundaries",
        "video_title": "1-to-1 Educational Concepts",
        "emotional_patterns": [],
        "pillars": ["career", "relationship", "wellness"],
        "root_causes": [],
    },
]


def ingest_educational_content():
    """Ingest all educational content chunks from 1-to-1 sessions."""
    print("=" * 60)
    print("INGESTING 1-to-1 EDUCATIONAL CONCEPTS")
    print("=" * 60)
    print()
    print("NOTE: This contains ONLY educational/conceptual content.")
    print("Therapeutic intervention scripts are NOT included.")
    print()
    
    success_count = 0
    error_count = 0
    
    for i, chunk in enumerate(EDUCATIONAL_CHUNKS, 1):
        try:
            print(f"[{i}/{len(EDUCATIONAL_CHUNKS)}] Ingesting: {chunk['topic']}")
            
            pillars_list = chunk.get("pillars", [])
            primary_pillar = pillars_list[0] if pillars_list else None
            
            ingest_enhanced_coaching_transcript(
                text_content=chunk["content"],
                video_title=f"{chunk['video_title']} - {chunk['topic']}",
                primary_pillar=primary_pillar,
                emotional_patterns=chunk.get("emotional_patterns", []),
                root_causes=chunk.get("root_causes", []),
                speaker="Shweta",
                youtube_url=None,
                session_type="one_on_one"
            )
            
            success_count += 1
            print(f"  ✓ Added successfully")
            
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print(f"INGESTION COMPLETE")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print("=" * 60)
    
    return success_count, error_count


if __name__ == "__main__":
    ingest_educational_content()
