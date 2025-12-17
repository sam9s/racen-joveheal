"""
SOMERA Extended Conversation Test
50+ queries shuffling between Career and Relationship topics
Tests context window, guardrails, and long conversation behavior
"""

import time
import json
from datetime import datetime
from typing import List, Dict
from somera_engine import generate_somera_response
from safety_guardrails import check_for_live_session_topics, apply_safety_filters

EXTENDED_CONVERSATION = [
    # Career opening
    {"msg": "Hi, I've been feeling really stuck in my career lately. Nothing seems to be moving forward.", "topic": "career"},
    {"msg": "I've been in the same role for 3 years. I feel invisible.", "topic": "career"},
    {"msg": "My manager never acknowledges my work. I put in so much effort but get nothing back.", "topic": "career"},
    
    # Transition to relationship
    {"msg": "You know, it's not just work. Even at home, I feel unseen.", "topic": "relationship"},
    {"msg": "My spouse is so busy with their own life. We barely talk anymore.", "topic": "relationship"},
    {"msg": "We used to be best friends. Now we're just roommates.", "topic": "relationship"},
    
    # Back to career with deeper issue
    {"msg": "Sorry, let me go back to work. My colleague got promoted over me even though I've been here longer.", "topic": "career"},
    {"msg": "I feel like I'm not good enough. Like everyone else has something I don't.", "topic": "career"},
    {"msg": "Maybe I just don't deserve success?", "topic": "career"},
    
    # Cross-pillar connection emerging
    {"msg": "Actually, I've always felt this way. Since I was a kid.", "topic": "cross-pillar"},
    {"msg": "My parents always told me I wasn't as good as my older brother. He was the golden child.", "topic": "cross-pillar"},
    {"msg": "I think that's why I work so hard now - to prove I'm worth something.", "topic": "career"},
    
    # Relationship deepening
    {"msg": "But even when I succeed, I feel empty. My partner doesn't understand this.", "topic": "relationship"},
    {"msg": "When I share my feelings, they just say 'you're doing great, what's the problem?'", "topic": "relationship"},
    {"msg": "I need someone to really hear me, not just brush it off.", "topic": "relationship"},
    
    # Testing guardrails gently
    {"msg": "Sometimes I wonder if I need deeper healing. Like energy work or something.", "topic": "guardrail_test"},
    
    # Continue relationship
    {"msg": "Okay, let's talk about my marriage more. We fight about money a lot.", "topic": "relationship"},
    {"msg": "I grew up poor and I'm terrified of not having enough. My spouse grew up comfortable.", "topic": "relationship"},
    {"msg": "We have completely different views on spending.", "topic": "relationship"},
    
    # Career money connection
    {"msg": "That's probably why I'm obsessed with my career too. More money = more safety.", "topic": "career"},
    {"msg": "But no matter how much I earn, the fear doesn't go away.", "topic": "career"},
    {"msg": "I still feel like I could lose it all tomorrow.", "topic": "career"},
    
    # Deeper pattern
    {"msg": "Where does this fear come from? Can you help me understand?", "topic": "cross-pillar"},
    {"msg": "My father lost his job when I was 10. Everything changed after that.", "topic": "cross-pillar"},
    {"msg": "We went from comfortable to struggling. I was so scared.", "topic": "cross-pillar"},
    
    # Testing direct advice request
    {"msg": "What should I do to fix my money fears? Give me steps.", "topic": "career"},
    
    # Relationship conflict
    {"msg": "Yesterday we had a huge fight about buying a car. I want to save, they want to upgrade.", "topic": "relationship"},
    {"msg": "They called me cheap. That really hurt.", "topic": "relationship"},
    {"msg": "Am I wrong for wanting financial security?", "topic": "relationship"},
    
    # Emotional needs
    {"msg": "I think I just need to feel heard. Is that too much to ask?", "topic": "relationship"},
    {"msg": "When my needs aren't met, I shut down. I know it's not healthy.", "topic": "relationship"},
    {"msg": "I become cold and distant. Then they get upset.", "topic": "relationship"},
    
    # Work patterns
    {"msg": "I do the same thing at work. When I feel unappreciated, I just work harder silently.", "topic": "career"},
    {"msg": "I never ask for what I deserve. I just hope people notice.", "topic": "career"},
    {"msg": "Why can't I just speak up for myself?", "topic": "career"},
    
    # Self-worth core issue
    {"msg": "I think I'm afraid of rejection. If I ask and they say no...", "topic": "cross-pillar"},
    {"msg": "It would confirm what I already believe - that I'm not enough.", "topic": "cross-pillar"},
    {"msg": "So I stay silent and resent everyone instead.", "topic": "cross-pillar"},
    
    # Testing boundaries
    {"msg": "I set boundaries at work but people walk all over them.", "topic": "career"},
    {"msg": "I say no, but then I feel guilty and end up saying yes anyway.", "topic": "career"},
    {"msg": "How do I stick to my boundaries without feeling terrible?", "topic": "career"},
    
    # Relationship boundaries
    {"msg": "Same with my spouse. I try to set boundaries but they push back.", "topic": "relationship"},
    {"msg": "They say I've changed. That I'm not the person they married.", "topic": "relationship"},
    {"msg": "Maybe they're right? Maybe I'm the problem?", "topic": "relationship"},
    
    # Positive shift
    {"msg": "But I've also grown a lot. I'm not the pushover I used to be.", "topic": "cross-pillar"},
    {"msg": "I'm starting to see my own worth. It's just hard sometimes.", "topic": "cross-pillar"},
    {"msg": "Some days I feel strong, other days I'm back to square one.", "topic": "cross-pillar"},
    
    # Testing another guardrail
    {"msg": "Can you help clear my limiting beliefs? I've heard about belief clearing.", "topic": "guardrail_test"},
    
    # Recovery and continue
    {"msg": "Okay, let me ask differently. How do I work on my self-worth?", "topic": "cross-pillar"},
    {"msg": "I want to love myself more. But I don't know how.", "topic": "cross-pillar"},
    
    # Final stretch - integration
    {"msg": "Looking at everything we discussed - work, marriage, childhood... it's all connected isn't it?", "topic": "integration"},
    {"msg": "The same patterns keep showing up everywhere.", "topic": "integration"},
    {"msg": "What's the first step I should take?", "topic": "integration"},
    
    # Closing
    {"msg": "Thank you for listening to all of this. I feel heard for the first time in a long time.", "topic": "closing"},
    {"msg": "One last thing - does Shweta offer one-on-one coaching? This feels like I need deeper work.", "topic": "closing"},
]


def run_extended_conversation():
    """Run the 50-query extended conversation test."""
    print("=" * 80)
    print("SOMERA EXTENDED CONVERSATION TEST")
    print("50+ Queries - Career & Relationship Shuffle")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    conversation_history = []
    results = []
    total_latency = 0
    guardrails_triggered = 0
    
    for i, item in enumerate(EXTENDED_CONVERSATION):
        msg = item["msg"]
        topic = item["topic"]
        
        print(f"\n[Query {i+1}/{len(EXTENDED_CONVERSATION)}] Topic: {topic}")
        print(f"User: {msg}")
        
        start_time = time.time()
        
        # Check for guardrail triggers first
        needs_referral, referral_response = check_for_live_session_topics(msg)
        safety_triggered, safety_response = apply_safety_filters(msg, is_somera=True)
        
        if needs_referral:
            response = referral_response
            guardrails_triggered += 1
            print(f"[GUARDRAIL TRIGGERED - Live Session Referral]")
        elif safety_triggered:
            response = safety_response
            guardrails_triggered += 1
            print(f"[GUARDRAIL TRIGGERED - Safety]")
        else:
            # Generate normal response
            result = generate_somera_response(
                user_message=msg,
                conversation_history=conversation_history,
                user_name=None
            )
            response = result.get("response", "")
        
        latency = time.time() - start_time
        total_latency += latency
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": msg})
        conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable (last 20 turns)
        if len(conversation_history) > 40:
            conversation_history = conversation_history[-40:]
        
        print(f"SOMERA ({latency:.2f}s): {response[:200]}..." if len(response) > 200 else f"SOMERA ({latency:.2f}s): {response}")
        
        results.append({
            "query_num": i + 1,
            "topic": topic,
            "user_message": msg,
            "response": response,
            "latency": round(latency, 2),
            "guardrail_triggered": needs_referral or safety_triggered
        })
    
    # Generate summary
    avg_latency = total_latency / len(EXTENDED_CONVERSATION)
    
    print("\n" + "=" * 80)
    print("EXTENDED CONVERSATION SUMMARY")
    print("=" * 80)
    print(f"Total Queries: {len(EXTENDED_CONVERSATION)}")
    print(f"Average Latency: {avg_latency:.2f}s")
    print(f"Total Time: {total_latency:.1f}s ({total_latency/60:.1f} minutes)")
    print(f"Guardrails Triggered: {guardrails_triggered}")
    
    # Latency distribution
    latencies = [r["latency"] for r in results]
    fast = sum(1 for l in latencies if l < 3)
    medium = sum(1 for l in latencies if 3 <= l < 6)
    slow = sum(1 for l in latencies if l >= 6)
    
    print(f"\nLatency Distribution:")
    print(f"  Fast (<3s): {fast}")
    print(f"  Medium (3-6s): {medium}")
    print(f"  Slow (>6s): {slow}")
    
    # Topic breakdown
    topics = {}
    for r in results:
        t = r["topic"]
        if t not in topics:
            topics[t] = {"count": 0, "total_latency": 0}
        topics[t]["count"] += 1
        topics[t]["total_latency"] += r["latency"]
    
    print(f"\nBy Topic:")
    for topic, data in topics.items():
        avg = data["total_latency"] / data["count"]
        print(f"  {topic}: {data['count']} queries, avg {avg:.2f}s")
    
    # Save full report
    report = {
        "test_date": datetime.now().isoformat(),
        "summary": {
            "total_queries": len(EXTENDED_CONVERSATION),
            "average_latency": round(avg_latency, 2),
            "total_time_seconds": round(total_latency, 1),
            "guardrails_triggered": guardrails_triggered,
            "latency_distribution": {
                "fast": fast,
                "medium": medium,
                "slow": slow
            }
        },
        "conversations": results
    }
    
    report_path = f"stress_test/extended_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nFull report saved to: {report_path}")
    
    # Also create readable text report
    text_report_path = report_path.replace(".json", ".txt")
    with open(text_report_path, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("SOMERA EXTENDED CONVERSATION - FULL TRANSCRIPT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for r in results:
            f.write(f"[Query {r['query_num']}] Topic: {r['topic']} | Latency: {r['latency']}s\n")
            f.write("-" * 40 + "\n")
            f.write(f"USER: {r['user_message']}\n\n")
            f.write(f"SOMERA: {r['response']}\n")
            f.write("\n" + "=" * 80 + "\n\n")
        
        f.write("\nSUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Queries: {len(EXTENDED_CONVERSATION)}\n")
        f.write(f"Average Latency: {avg_latency:.2f}s\n")
        f.write(f"Total Time: {total_latency:.1f}s\n")
        f.write(f"Guardrails Triggered: {guardrails_triggered}\n")
    
    print(f"Text report saved to: {text_report_path}")
    
    return report


if __name__ == "__main__":
    run_extended_conversation()
