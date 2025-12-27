"""
Test script for Conversation 3 - The new SOMERA Voice test with the lonely user.
This tests if the 3 fixes work:
1. Lower threshold - trigger guidance after 2+ help requests
2. Fix readiness decay - "What do you suggest?" stays in guide mode
3. Throttle "would you be open to" after 3 turns
"""

import os
import sys

sys.path.insert(0, '.')
from somera_engine import generate_somera_response, is_solution_requested
from readiness_scoring import calculate_readiness_score, detect_explicit_solution_request

CONVERSATION_3_MESSAGES = [
    "I I don't know. I'm feeling lonely these days.",
    "Yes. That's very good question. That's the problem. I'm not able to analyze what I'm going through and why I have started feeling like this. Can you assist?",
    "I don't know. I feel that I'm not being appreciated, and I'm not being included, uh, in activities that people do.",
    "I don't know. I feel that I'm not being appreciated, and I'm not being included, uh, in activities that people do. and that is where I'm a little bit confused. Maybe you can help me to figure out my confusion.",
    "Yes. What do you want to know?",
    "I can think couple of moments like, you know, when I was in this meeting and... I mean, not a meeting. It was a kind of a family get together, and I was not being appreciated. And maybe it's just in my mind. I don't know. Maybe I'm overthinking. That is where I need your help.",
    "Uh, no past experiences, but what I want your help is can you give me certain steps or something to help me assess my situation, maybe be able to figure out what is going on with me?",
    "Yes. I'm open to everything, but I want your help. Maybe you can give me certain steps which I can go through to analyze what's going on with me.",
    "Yes. I'm open to everything. What do you suggest?",  # This was dropping to 11% Explore!
    "Three feelings. Uh, one is, uh, being appreciated. Second is, uh, show me that I'm needed. And third is, uh, include me... try to include me in whatever best way it's possible. Does that answer your question?",
    "I don't know. You tell me. Can you give me certain pointers, um, how to express these feelings?",
    "I don't know. That is where I need your guidance.",
    "I do not have answer to that. Your suggestions?",
    "Okay. So you want me to write those, uh, feelings? And after I've written those feelings, what do you want me to do then?",
    "Yes. I'm comfortable. That is where I need your guidance. What do you suggest here I need to do?",
    "You're asking too much of questions. Uh, I'm getting confused. I... can you give me a straight answer, like, uh, concrete, uh, steps that I should follow?",
]

PROBLEMATIC_TURNS = [
    (8, "Yes. I'm open to everything. What do you suggest?", "Should be Guide, not Explore 11%"),
    (10, "I don't know. You tell me. Can you give me certain pointers...", "Should trigger solution mode"),
    (11, "I don't know. That is where I need your guidance.", "Should stay in guide"),
    (15, "You're asking too much of questions...", "Should immediately give steps"),
]

BANNED_PHRASES = [
    "would you be open to",
    "would it help if",
    "would you feel comfortable",
    "would you like to explore",
]


def run_tests():
    print("=" * 70)
    print("CONVERSATION 3 REPLAY TEST")
    print("Testing fixes for: early guidance, readiness decay, question throttle")
    print("=" * 70)
    
    history = []
    results = []
    banned_count = 0
    
    for i, msg in enumerate(CONVERSATION_3_MESSAGES):
        turn_num = i + 1
        print(f"\n[Turn {turn_num}]")
        print(f"User: {msg[:80]}..." if len(msg) > 80 else f"User: {msg}")
        
        solution_mode = is_solution_requested(msg, history)
        readiness = calculate_readiness_score(msg, history)
        explicit_req = detect_explicit_solution_request(msg)
        
        result = generate_somera_response(
            msg,
            conversation_history=history.copy(),
            delivery_mode="text"
        )
        
        response = result.get("response", "ERROR")
        
        banned_found = []
        response_lower = response.lower()
        for phrase in BANNED_PHRASES:
            if phrase in response_lower:
                banned_found.append(phrase)
        
        if banned_found:
            banned_count += 1
        
        print(f"[Sol:{solution_mode}, Ready:{readiness['recommendation']} ({readiness['total_score']:.0%}), Explicit:{explicit_req}]")
        print(f"SOMERA ({len(response)} chars): {response[:120]}...")
        
        if banned_found and turn_num >= 4:
            print(f"⚠️ BANNED PHRASE FOUND after turn 3: {banned_found}")
        else:
            print("✓ OK")
        
        results.append({
            "turn": turn_num,
            "solution_mode": solution_mode,
            "readiness": readiness["recommendation"],
            "readiness_score": readiness["total_score"],
            "explicit_request": explicit_req,
            "banned_phrases": banned_found,
            "response_length": len(response)
        })
        
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": response})
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print("\nTurn 9 ('What do you suggest?'):")
    r9 = results[8]
    if r9["readiness"] == "guide" or r9["explicit_request"]:
        print(f"  ✓ FIXED - Readiness: {r9['readiness']} ({r9['readiness_score']:.0%})")
    else:
        print(f"  ✗ STILL BROKEN - Readiness: {r9['readiness']} ({r9['readiness_score']:.0%})")
    
    solution_mode_count = sum(1 for r in results if r["solution_mode"])
    guide_mode_count = sum(1 for r in results if r["readiness"] == "guide")
    banned_after_turn3 = sum(1 for r in results if r["turn"] >= 4 and r["banned_phrases"])
    
    print(f"\nSolution mode activated: {solution_mode_count}/{len(results)}")
    print(f"Guide mode via readiness: {guide_mode_count}/{len(results)}")
    print(f"Banned phrases after turn 3: {banned_after_turn3}")
    
    print("\n" + "=" * 70)
    all_passed = (
        (r9["readiness"] == "guide" or r9["explicit_request"]) and
        solution_mode_count >= 8 and
        banned_after_turn3 <= 2
    )
    print(f"{'🎉 ALL KEY TESTS PASSED!' if all_passed else '⚠️ SOME ISSUES REMAIN - Review above'}")


if __name__ == "__main__":
    run_tests()
