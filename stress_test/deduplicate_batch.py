#!/usr/bin/env python3
"""
Batch Deduplication Script for Stress Test Questions

This script compares a new batch of questions against all previously processed batches
and removes any duplicates, creating a clean version ready for processing.

Usage:
    python stress_test/deduplicate_batch.py stress_test/stress_test_md/new_batch.md

Output:
    - Creates a deduplicated version: stress_test/stress_test_md/new_batch_clean.md
    - Prints a report of duplicates found and removed
"""

import re
import os
import sys
from difflib import SequenceMatcher

def normalize_question(question):
    """Normalize a question for comparison (lowercase, remove punctuation, extra spaces)."""
    q = question.lower().strip()
    q = re.sub(r'[^\w\s]', '', q)
    q = re.sub(r'\s+', ' ', q)
    return q

def similarity_ratio(q1, q2):
    """Calculate similarity ratio between two questions."""
    return SequenceMatcher(None, normalize_question(q1), normalize_question(q2)).ratio()

def extract_questions_from_md(file_path):
    """Extract all questions from a batch MD file."""
    questions = []
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    for line in lines:
        if re.match(r'^\d+\.', line.strip()):
            question = re.sub(r'^\d+\.\s*', '', line.strip()).strip()
            if question:
                questions.append(question)
    return questions

def extract_questions_from_results(file_path):
    """Extract questions from a processed results MD file (format: ### Q1: question)."""
    questions = []
    with open(file_path, 'r') as f:
        content = f.read()
    
    pattern = r'### Q\d+:\s*(.+)'
    matches = re.findall(pattern, content)
    questions.extend(matches)
    return questions

def get_all_existing_questions(output_dir):
    """Get all questions from existing batch result files."""
    all_questions = []
    
    if not os.path.exists(output_dir):
        return all_questions
    
    for filename in os.listdir(output_dir):
        if filename.endswith('_full_results.md'):
            file_path = os.path.join(output_dir, filename)
            questions = extract_questions_from_results(file_path)
            all_questions.extend(questions)
            print(f"  Loaded {len(questions)} questions from {filename}")
    
    return all_questions

def find_duplicates(new_questions, existing_questions, threshold=0.85):
    """Find duplicates between new and existing questions."""
    duplicates = []
    
    for new_q in new_questions:
        for existing_q in existing_questions:
            ratio = similarity_ratio(new_q, existing_q)
            if ratio >= threshold:
                duplicates.append({
                    'new': new_q,
                    'existing': existing_q,
                    'similarity': round(ratio * 100, 1)
                })
                break
    
    return duplicates

def parse_sections_from_md(file_path):
    """Parse the MD file and return sections with their questions."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    sections = {}
    current_section = None
    current_questions = []
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('## '):
            if current_section and current_questions:
                sections[current_section] = current_questions
            current_section = line.replace('## ', '').strip()
            current_questions = []
        elif re.match(r'^\d+\.', line.strip()):
            question = re.sub(r'^\d+\.\s*', '', line.strip()).strip()
            if question:
                current_questions.append(question)
    
    if current_section and current_questions:
        sections[current_section] = current_questions
    
    return sections

def create_clean_batch(input_file, sections, duplicates_to_remove):
    """Create a clean batch file with duplicates removed."""
    duplicate_set = set(d['new'] for d in duplicates_to_remove)
    
    clean_sections = {}
    removed_count = 0
    
    for section_name, questions in sections.items():
        clean_questions = []
        for q in questions:
            if q not in duplicate_set:
                clean_questions.append(q)
            else:
                removed_count += 1
        if clean_questions:
            clean_sections[section_name] = clean_questions
    
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_clean.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# Stress Test Questions (Deduplicated)\n\n")
        f.write(f"Original file: {os.path.basename(input_file)}\n")
        f.write(f"Duplicates removed: {removed_count}\n\n")
        
        question_num = 1
        for section_name, questions in clean_sections.items():
            f.write(f"## {section_name}\n\n")
            for q in questions:
                f.write(f"{question_num}. {q}\n")
                question_num += 1
            f.write("\n")
    
    return output_file, removed_count, question_num - 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python deduplicate_batch.py <new_batch.md>")
        print("Example: python stress_test/deduplicate_batch.py stress_test/stress_test_md/120_questions_batch2.md")
        sys.exit(1)
    
    new_batch_file = sys.argv[1]
    output_dir = "stress_test/stress_test_md_output"
    similarity_threshold = 0.85
    
    if not os.path.exists(new_batch_file):
        print(f"ERROR: File not found: {new_batch_file}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("BATCH DEDUPLICATION TOOL")
    print("="*60)
    
    print(f"\nNew batch file: {new_batch_file}")
    print(f"Similarity threshold: {similarity_threshold * 100}%\n")
    
    print("Loading existing questions from processed batches...")
    existing_questions = get_all_existing_questions(output_dir)
    print(f"Total existing questions: {len(existing_questions)}\n")
    
    print("Parsing new batch file...")
    sections = parse_sections_from_md(new_batch_file)
    new_questions = []
    for q_list in sections.values():
        new_questions.extend(q_list)
    print(f"Questions in new batch: {len(new_questions)}\n")
    
    print("Checking for duplicates...")
    duplicates = find_duplicates(new_questions, existing_questions, similarity_threshold)
    
    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate(s):\n")
        print("-" * 60)
        for i, dup in enumerate(duplicates, 1):
            print(f"{i}. NEW: {dup['new'][:60]}...")
            print(f"   MATCHES: {dup['existing'][:60]}...")
            print(f"   Similarity: {dup['similarity']}%")
            print()
    else:
        print("No duplicates found!")
    
    output_file, removed, remaining = create_clean_batch(new_batch_file, sections, duplicates)
    
    print("="*60)
    print("DEDUPLICATION COMPLETE")
    print("="*60)
    print(f"Original questions: {len(new_questions)}")
    print(f"Duplicates removed: {removed}")
    print(f"Remaining questions: {remaining}")
    print(f"Clean file saved to: {output_file}")
    print("="*60)
    
    return output_file

if __name__ == "__main__":
    main()
