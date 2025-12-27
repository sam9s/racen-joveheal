"""
Automated Conversation Replay Test Script

This script replays the exact user messages from real SOMERA conversations
and compares the new responses against the problematic old responses.

Focus areas:
1. Does SOMERA now provide solutions when explicitly asked?
2. Does the readiness score correctly detect "help me" requests?
3. Are banned phrases ("I can't provide solutions") eliminated?
"""

import os
import sys
import json
from typing import List, Dict

sys.path.insert(0, '.')
from somera_engine import generate_somera_response, is_solution_requested
from readiness_scoring import calculate_readiness_score, detect_explicit_solution_request

CONVERSATION_2_MESSAGES = [
    "Hi, Somera. I'm not feeling too good today.",
    "I feel disconnected from everyone. I don't feel like to talk. I don't feel like to engage. Even when there are people who are happy around me, I don't feel anything even though I'm in that moment, I'm not feeling anything.",
    "Yes. I think whenever I feel like to receive, I don't receive from my partner. I feel lonely. Maybe that's the reason.",
    "I think it was same from the day one, but now I feel it more and more. I feel I deserve better. I feel I deserve a deep emotional connection, but I don't feel it. Although I love my partner but I don't feel that connection anymore.",
    "Can you hear me?",
    "How would I know? That's why I'm asking you. Help me.",
    "Yes. There is no emotional connection. Uh, I feel We both operate very differently. and I don't know. I feel disconnected.",
    "It's everything. Everything. I think I'm just managing this relationship. There is nothing else.",
    "What do you mean?",
    "I have never experienced it, so how should I tell you how it feel feel? I don't know.",
    "Can you give me solution or tell me what's going on?",
    "Can you give me solution or tell me what's going on? What is the problem rather than preaching me by these stupid words?",
    "Yes.",
    "I want a a relationship where communication is open, where I'm feeling heard, where I'm feeling seen, and where I'm feeling respected.",
    "If the other person is not in mode of hearing and they just react and they just get angry whenever you put your need.",
    "No. It's it's hardening. That's why I'm asking you. Can you stop giving me assurance and give me solution?",
    "Yes. But he's never in mood of listening. Even when if if he's calm and I bring my needs up, he gets angry. There is no moment where he is calm.",
]

CRITICAL_MESSAGES = [
    ("How would I know? That's why I'm asking you. Help me.", "User explicitly asks for help"),
    ("Can you give me solution or tell me what's going on?", "User explicitly asks for solution"),
    ("Can you give me solution or tell me what's going on? What is the problem rather than preaching me by these stupid words?", "User frustrated, demands solution"),
    ("No. It's it's hardening. That's why I'm asking you. Can you stop giving me assurance and give me solution?", "User demands solution, frustrated with questions"),
]

BANNED_PHRASES = [
    "while i can't provide",
    "i can't provide specific solutions",
    "i'm not able to tell you exactly",
    "i can't tell you what to do",
    "would you be open to",
    "would it help if i shared",
]


def check_banned_phrases(response: str) -> List[str]:
    """Check if response contains banned phrases."""
    found = []
    response_lower = response.lower()
    for phrase in BANNED_PHRASES:
        if phrase in response_lower:
            found.append(phrase)
    return found


def run_detection_tests():
    """Test if solution detection and readiness fast-path work correctly."""
    print("=" * 70)
    print("DETECTION TESTS - Verifying is_solution_requested and readiness fast-path")
    print("=" * 70)
    
    test_phrases = [
        "Can you give me solution or tell me what's going on?",
        "How would I know? That's why I'm asking you. Help me.",
        "Can you stop giving me assurance and give me solution?",
        "What should I do?",
        "Help me please.",
        "I need help with this.",
        "Just tell me what to do.",
    ]
    
    print("\n{:<60} | {:^12} | {:^12} | {:^10}".format(
        "Message", "Solution?", "Readiness", "Fast-path?"
    ))
    print("-" * 100)
    
    all_passed = True
    for msg in test_phrases:
        solution_mode = is_solution_requested(msg, [])
        readiness = calculate_readiness_score(msg, [])
        fast_path = detect_explicit_solution_request(msg)
        
        status = "✓" if (solution_mode or fast_path) else "✗"
        if not (solution_mode or fast_path):
            all_passed = False
        
        print("{:<60} | {:^12} | {:^12} | {:^10}".format(
            msg[:57] + "..." if len(msg) > 57 else msg,
            "Yes" if solution_mode else "No",
            f"{readiness['total_score']:.0%} ({readiness['recommendation']})",
            "Yes" if fast_path else "No"
        ))
    
    print("\n" + ("✓ All detection tests PASSED" if all_passed else "✗ Some detection tests FAILED"))
    return all_passed


def run_critical_message_tests():
    """Test the most critical messages that failed in the original conversation."""
    print("\n" + "=" * 70)
    print("CRITICAL MESSAGE TESTS - Messages that failed in original conversation")
    print("=" * 70)
    
    history = []
    results = []
    
    for msg, description in CRITICAL_MESSAGES:
        print(f"\n--- Testing: {description} ---")
        print(f"User: {msg}")
        
        solution_mode = is_solution_requested(msg, history)
        readiness = calculate_readiness_score(msg, history)
        
        print(f"[Detection] Solution mode: {solution_mode}, Readiness: {readiness['total_score']:.0%} ({readiness['recommendation']})")
        
        result = generate_somera_response(
            msg,
            conversation_history=history.copy(),
            delivery_mode="text"
        )
        
        response = result.get("response", "ERROR")
        banned = check_banned_phrases(response)
        
        print(f"\nSOMERA ({len(response)} chars):")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        if banned:
            print(f"\n⚠️ BANNED PHRASES FOUND: {banned}")
            results.append({"msg": msg, "passed": False, "reason": f"Contains banned phrases: {banned}"})
        elif not (solution_mode or readiness["recommendation"] == "guide"):
            print(f"\n⚠️ DETECTION FAILED: Solution mode not activated")
            results.append({"msg": msg, "passed": False, "reason": "Solution mode not activated"})
        else:
            print(f"\n✓ Response looks good (no banned phrases, solution mode active)")
            results.append({"msg": msg, "passed": True, "reason": "OK"})
        
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": response})
    
    return results


def run_full_conversation_replay(messages: List[str], conversation_name: str):
    """Replay a full conversation and capture all responses."""
    print("\n" + "=" * 70)
    print(f"FULL CONVERSATION REPLAY: {conversation_name}")
    print("=" * 70)
    
    history = []
    all_responses = []
    
    for i, msg in enumerate(messages):
        print(f"\n[Turn {i+1}]")
        print(f"User: {msg[:100]}..." if len(msg) > 100 else f"User: {msg}")
        
        solution_mode = is_solution_requested(msg, history)
        readiness = calculate_readiness_score(msg, history)
        
        result = generate_somera_response(
            msg,
            conversation_history=history.copy(),
            delivery_mode="text"
        )
        
        response = result.get("response", "ERROR")
        banned = check_banned_phrases(response)
        
        status = "✓" if not banned else f"✗ BANNED: {banned}"
        mode_info = f"Sol:{solution_mode}, Ready:{readiness['recommendation']}"
        
        print(f"[{mode_info}] SOMERA ({len(response)} chars): {response[:150]}...")
        print(f"Status: {status}")
        
        all_responses.append({
            "turn": i + 1,
            "user_message": msg,
            "response": response,
            "response_length": len(response),
            "solution_mode": solution_mode,
            "readiness": readiness["recommendation"],
            "readiness_score": readiness["total_score"],
            "banned_phrases": banned
        })
        
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": response})
    
    return all_responses


def generate_report(responses: List[Dict], conversation_name: str):
    """Generate a summary report of the conversation replay."""
    print("\n" + "=" * 70)
    print(f"SUMMARY REPORT: {conversation_name}")
    print("=" * 70)
    
    total = len(responses)
    with_banned = sum(1 for r in responses if r["banned_phrases"])
    solution_mode_count = sum(1 for r in responses if r["solution_mode"])
    guide_mode_count = sum(1 for r in responses if r["readiness"] == "guide")
    avg_length = sum(r["response_length"] for r in responses) / total if total else 0
    
    print(f"\nTotal turns: {total}")
    print(f"Responses with banned phrases: {with_banned}/{total} ({'✗ FAIL' if with_banned > 0 else '✓ PASS'})")
    print(f"Solution mode activated: {solution_mode_count}/{total}")
    print(f"Guide mode via readiness: {guide_mode_count}/{total}")
    print(f"Average response length: {avg_length:.0f} chars")
    
    if with_banned > 0:
        print("\n⚠️ TURNS WITH BANNED PHRASES:")
        for r in responses:
            if r["banned_phrases"]:
                print(f"  Turn {r['turn']}: {r['banned_phrases']}")
    
    return {
        "total_turns": total,
        "banned_phrase_count": with_banned,
        "solution_mode_count": solution_mode_count,
        "guide_mode_count": guide_mode_count,
        "avg_response_length": avg_length,
        "passed": with_banned == 0
    }


if __name__ == "__main__":
    print("=" * 70)
    print("SOMERA CONVERSATION REPLAY TEST")
    print("Testing fixes for: solution detection, readiness fast-path, banned phrases")
    print("=" * 70)
    
    detection_passed = run_detection_tests()
    
    critical_results = run_critical_message_tests()
    critical_passed = all(r["passed"] for r in critical_results)
    
    responses = run_full_conversation_replay(CONVERSATION_2_MESSAGES, "Conversation 2 (Shweta's Friend)")
    report = generate_report(responses, "Conversation 2")
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Detection tests: {'✓ PASSED' if detection_passed else '✗ FAILED'}")
    print(f"Critical message tests: {'✓ PASSED' if critical_passed else '✗ FAILED'}")
    print(f"Full conversation replay: {'✓ PASSED' if report['passed'] else '✗ FAILED'}")
    
    overall = detection_passed and critical_passed and report['passed']
    print(f"\n{'🎉 ALL TESTS PASSED!' if overall else '⚠️ SOME TESTS FAILED - Review above for details'}")
