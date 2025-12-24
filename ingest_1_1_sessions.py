#!/usr/bin/env python3
"""
Ingest the 3 one-to-one session transcripts from Shweta's coaching sessions.

These transcripts provide rich examples of:
- Transition patterns from questioning to guidance
- Coaching frameworks and techniques
- Real client interactions across all 3 pillars
"""

import os
from knowledge_base import ingest_enhanced_coaching_transcript

SESSION_1_CONTENT = """
Session 1: Healing Session - Soul Purpose, Business Collaboration & Fear Work

Session Opening - Vision & Collaboration

Practitioner: Things that are done with service always manifest beautifully. I didn't have to put effort in my healing business because it started with service. So when you work with this ego - I will be explaining it more in our session today because we are working on it.

You told me that you want to work on fear of driving and fear of water. I think fear of water has already gone down when you revisited your story. You knew what's happening. See, you could have died. You're still alive sitting here. When that major event couldn't take your life, how come a swimming pool will take your life? Because the lifeguard is sitting over there.

Client: It hit me. It hit me a lot.

Practitioner: Yeah, but you didn't die.

Client: I didn't die. I didn't get hurt. Only one point when I told you - two stones were there. They were just my palm size, those two stones I just held. That was the point where if I cross that one point my body will be downstream.

Practitioner: Exactly. Rather than hitting your brain, what did it do? It saved you. There is a major power behind you and I hope you are realizing it now.

The Turning Point

Practitioner: Today is our ninth session, right? Nine sessions. This is such an important point in your life where there is no going back anymore. Generally if you see, when we did other modalities and all that, I used to say if you don't practice you will fall back. I'm not saying it here. Why? Because you are reprogrammed. Your blueprint has changed. From here there is no going back.

But how you have to use this power is in your hand. And the kind of energy we are in right now - if you take two steps, eight steps are automatic. So you will be taking 10 steps forward.

It's very important that from here you have to just think how to move forward. Because your new job is on the way, your desired life is on the way. You have to just keep yourself open.

If some delivery person comes and your door is closed, they will ring the bell. You will only get the package when you open the door. Until then it will be outside. That's it. Always remember that example - door opening you have to do. It's on the way.

Recent Wins & Transformations

Client: Actually I wanted to share some things with you.

Practitioner: Yes, I want to know the wins.

Client: Because from the last week I've been practicing the meditation of last session and I see profound changes in me that I never had. Like there was no sense of self earlier, right? So now from the last session I'm feeling sense of self.

And there is - I never saw myself... like people say I'm pretty, but the whole reflection came into me - like I am the one. If I don't see it, how does the world see it? If I don't believe in me, how does the world believe in me? Then everything fell off.

Neither it's my family - all the people who pointed out things about me - that was not reflection of anybody. It was reflection of me that I didn't see. So definitely they didn't see. So that reflection came. And every time I go and see in my mirror I just see myself fully, like "Oh I love you." I keep saying those statements and all. And I'm like "Wow, you are beautiful."

You know, I realized my soul fought so much to take this life - the current life. So I need... I don't know, suddenly that realization came. This is my journey.

Recognizing Soul Power

Practitioner: And you should feel proud because you know, I have said that many times. And believe me, I have not told this to many people. In fact, hardly one out of all my clients - you have such a powerful aura and I see angels all behind you.

The only thing that you are missing is you don't realize it yet. Start noticing it more. Start becoming in your flow more.

Go with your flow. What brings you in that flow? You have to find out. And today we are going to find that out as well.

The Three Keys to Success

Practitioner: You know, remember only two words moving forward - three in fact. If you want to note it down:

Consistency, discipline, and action.

Every day, don't forget about these three words. And when I say action, it should be soul-aligned action, not just any action.

See, you have been thinking about this journal for so long. You should have worked on that because that will be a soul-aligned action for you. Because this is coming from your soul.

Creating from Soul Alignment

Practitioner: I want you to do this from your soul alignment - not just because we have to create or you have to impress me. No, no, no.

So what you have to do is you will only do this work after doing a deep meditation. And after that, ask yourself or ask the Creator: "Give me three questions." Whatever comes in, add that. Because this is your product. I want you to design it beautifully.

You are a powerful soul. So you have to start believing it.

Client: I always want to keep questioning. You always say that I am powerful, right? I go back and I'm like "Why does she keep saying that? What makes her keep saying that? What am I powerful?"

Practitioner: It's not realizing - it's you have forgotten. So I keep on reminding you. It's that simple as that.

Consciousness Shift Teaching

Practitioner: There are three parts to today's session. Number one is driving - fear of driving. Number two is fear of water. And number three is I will be taking you deep into co-creation.

Because right now you are working through your ego. Your ego, your fear, and you feel that everything is in your control. This is called "by me" consciousness - that everything is happening by me, by me, by me.

So we have to shift from "by me" consciousness to God's consciousness. And it's a long process. It doesn't happen automatically. But at least we will light the lamp today so that your mind is prepared that yes, you are going that way now.
"""

SESSION_2_CONTENT = """
Session 2: Discovery Call - Health Issues, Relationship Patterns & Limiting Beliefs

Initial Energy Scan

Practitioner: Can you hear me? Just to let you know, this meeting is being recorded. So tell me, how was your day?

Client: It was fine. I didn't really go into work, just was at home. Nothing productive.

Practitioner: So what do you do?

Client: Real estate. But I think I'm not so sure if I still enjoy it because I've been doing real estate for 14 years. And maybe if it's not the right place or just my health has been a bit of a concern.

Practitioner: Okay. So do you mind if I quickly scan you? Just close your eyes. Take a deep breath in and exhale through your mouth. Keep on breathing deeply. Keep your eyes closed while I scan you.

Yes. Okay, you can open your eyes. Can I share what I saw?

As soon as I connected to your energy, the first thing that I got connected to is your heart as well as your solar plexus, which is like your upper abdomen. How is your digestion?

Client: Very bad.

Practitioner: Yeah. So it was immediately taking me there. And tell me, how is your relationship with your father?

Client: It's normal, but I think it's something that I probably would have wanted - that warmth. Like he's always been there for us and he's never said no. But I think I probably craved the love connection, the emotional connection.

Sharing Health Struggles

Client: I think it's just my health because I've had digestive issues for the past six years. It started off with H. pylori and then it led to something or another. I've done healing, I've done detoxes, I've worked with a gut coach. It will be okay for a while and then I'll slip back to normal.

I think I'm living in a lot of fear, a lot of phobias and fear. And that's taken me back. Like I was pretty confident and very independent, staying on my own. And now I've been living with my parents and family for the last six years. But I just feel like I've lost my independence as well.

And there's just been - I don't think I don't remember the last time I was just genuinely happy. Like I'm always feeling weighed down.

I'm getting into the wrong relationships. They're always unavailable. And it's been... I got divorced in maybe I would say 2014. And after that ended, I was in a relationship with someone who's married because that person came and sort of filled a void.

And as much as I didn't want it to happen, it happened. And then when that ended, it's the same thing. It's like I feel like history's just repeated itself.

This has been six years as well. And like today we're just always arguing because it's never going to be good. And I know it deep down. And the hardest bit is how do I detach now? Because I've spent so much of my energy and time. I know there's no future.

Defining the Ideal Life

Practitioner: Okay. So if I ask you, what is a perfect life for you? If you see from here, what do you want?

Client: I definitely want good health. I want my health to not be something that keeps pulling me back every time I'm trying to do something.

And I want to be able to just not hold on to these things. I want to have a loving relationship where I'm committed and someone is able to commit to me wholly and not partially and not just a facade of words and showering with things and then walk away.

And to be able to find what I would really want to do in my life. I feel like it's going over my head now. It's become so fast-paced and I'm just not able to keep up with it. So there's a part of me that also just feels kind of lost with my purpose.

But yeah, so I want to find my purpose and just be happy - genuinely happy.

Practitioner: When was the last time you felt happy?

Client: I really honestly can't tell you. I just feel like it's just been too much and overburdened of pressure.

The Scan Results

Practitioner: Yeah, there's nothing. I didn't see any. There are these pressures that I see, these patterns that I see. But nothing is wrong with you that you will suffer or something like that. No. It's like you are disconnected from your own being. So your soul is asking for that connection so that you realize that there is a bigger purpose for you here.

Client: Yeah. Sometimes I actually feel soulless. Like I feel so choked and you can't breathe and you're just... you don't know what's going on.

Understanding Patterns

Practitioner: Do you see, since we started, how patterns are playing in your life? It's not you. It's these subconscious patterns that are running your life.

And this is what I also understood. People call it different names but this is our life, right? And sometimes what happens is we give our power to healers, we give our power to coaches, we give our power to astrologers, other people. Because we feel we are less.

What I teach you is you are the creator of your own life. I'm just here to clean your glasses to see it. Simple as that. Because there is no magic pill. You need to work on your patterns. You need to release it.

Explaining the Blueprint

Practitioner: So the blueprint is something that actually reveals what are your limiting beliefs. See, we all have beliefs. Beliefs are nothing but what is actually building our life. There are good beliefs, there are limiting beliefs.

And sometimes what happens is - let's say you were suppressed as a child, right? So there is this fire in you: "I want to show them that I am capable." So you build your career. But now that belief has expired because you don't need it anymore. Right now you need an internal connection, a deeper connection with yourself. But because you have survived with that pattern, it's still running your life. You're proving, proving, proving.

So your blueprint is something that includes your beliefs, your limiting beliefs, your conditioning that happened in this life. Because this is not the real you. You're not real right now. You're someone who has been conditioned by teachers, by parents, by environment, by relationships, by whoever is around.

And the third thing is your ancestral imprint, which is like our 12-generation imprint. If your great-great-great grandmother was suppressed, you are still holding on to her trauma. And it kicks in whenever you feel that way.

Client: Yeah. Because my mom is like that. My grandmother's like that. So I can understand from those two that it's...

Practitioner: So the work definitely - it will not just heal you, it will heal backwards as well as the future generations. It will heal your family. It will heal your future children when you have them.
"""

SESSION_3_CONTENT = """
Session 3: Career Transition, Focus & Goal-Setting with RPM Tool

Focus and Inner Clarity

Practitioner: Let me tell you what focus is and how you can bring in more focus in your life.

So first of all, focus doesn't mean that you have to avoid distractions. It's not that everything should be fine in your life, then only you can focus. Or you should be 100% into something, then only it's focus.

Focus is not about avoiding distraction. It's about creating inner clarity within you. Even though your spouse is playing music loudly, you should be able to focus in that situation as well. And how it will happen is when you create inner clarity, emotional regulation, and strong connection to why you are doing what you're doing.

So ask yourself now - tell me, when is your least focus? When are you in least focus?

Client: When you are doing your office work?

Practitioner: Now you know why? Because you yourself are answering that you are not 100% in that. You don't have inner clarity why you're doing what you're doing.

Now tell me - what is that one thing you totally become engrossed in? For me, these sessions. I get so much into these sessions that I don't even realize that I'm sitting at my home.

Finding the Flow State

Client: I get involved when I am with people - especially when people come up with problems, when I give solutions, when I talk to them. That's when I don't realize how much time is passing.

I love - with your sessions and all - I just look forward for this session because this is where I am most myself.

Practitioner: So this is not an attention problem. This is inner clarity problem.

Now how to deal with this? Because earning is important, right? Now your job is the most important thing, right?

So you have to give this clarity to your mind that whatever you are doing, you are doing it because you need to do that right now to build a life of your dreams. Once you are in that position where you can leave your job, you can come back to the healing. But right now it's very important that your mind understands that 100% focus is important in my job.

And the way to do it is ask why. Why you're doing what you're doing: "I'm doing it because I am creating a better future where I will be able to do what my heart wants me to do."

Daily Focus Protocol

Practitioner: So let me give you what you have to do in the morning, afternoon and night to make sure that you're doing everything with focus.

So every day morning you have to make sure you are hydrating and then no phone for 30 minutes. And do one focused task that time - any focused task. You can do this meditation as well. This will program your brain for clarity all day.

Also once you are done with your meditation, ask yourself: "What actually matters today? What is my highest priority for this week?" And set an intention that aligns with your values as well as purpose.

Pomodoro Method for Focus

Practitioner: Have you heard about Pomodoro method?

Client: Yeah, yeah. I used to implement it in bits and pieces.

Practitioner: So what I do is when, let's say, I'm working on something important - let's say you have to write an email - I put a timer 20 minutes. I will not touch it.

So 25 - you do 25-20 minute timer. During that time you will do your work only - no other thing, no more tabs opening, just one tab. And that will be that focused work.

And then once the timer is off, pick up your phone. Give yourself some time. But put a timer for five minutes. As soon as timer is on, keep it. This will help you build a very good habit of staying in focus.

Daily Focus Retrospective

Practitioner: And then at last, at the end of your day, what you have to do is you have to do a retrospective. "How did I do well today?" Sorry - "What did I do well today?" And note it down.

Because this will give your brain some food: "Oh I'm doing it. I'm so beautifully doing it."

And then ask: "What distracted me?" And take an action: "How will I reset tomorrow?"

So this is - I call it as focus retrospective. So you have to check in every day with your mind.

RPM Tool - Goal Setting

Practitioner: So today is a very important day. Because today - I know I say that in most of our sessions - but today it's clarity about what exactly you want, why you want it, and some massive actions.

Tell me something you want to achieve in next 30 days.

Client: Next 30 days - I want to get a job that is as expected.

Practitioner: You want leadership role. What kind of company you want?

Client: I want to be a product manager with full autonomy in a tech industry which values my contribution, supports my growth and pays me well, and also helps me maintain my status.

Practitioner: Beautiful.

Healing Visualization

Practitioner: Now time to heal. We will heal whatever is blocking it. So close your eyes.

Take a deep breath in and release through your mouth. Again breathe in through your nose 1-2-3-4, hold 1-2-3-4, release through your mouth 1-2-3-4, hold 1-2-3-4.

Now we will be working with God's consciousness. We all have this consciousness within us, but sometimes we forget that we already carry this beautiful God's consciousness within us.

So we keep imagining things which are not there yet. And we keep on delaying the process of manifesting or delay the process of receiving just because we are thinking "Oh they might think that way."

So it's time to release "what if, what if and what if." We will change this to "what if":

What if they don't care that I'm coming from a different industry? What if they don't care that I don't have any experience as a product manager? What if they are ready to support my visa as soon as I go in?

So can you feel the difference between these emotions? One is contracting and one is so expanding.

Meeting the Future Self

Practitioner: Look at this version of yourself who is in this new technology job as a product manager, who is earning beautifully. She is saving, she is investing in her growth as well as in the journal as well.

Look at this confident version - the decision-maker, the leader. What has she done to achieve these goals?

Ask her: "What have you done? What have I done to achieve my goals?"

Client: I think I have released self-doubt.

Practitioner: And how has she released it? Ask her.

Client: By believing in myself, by trusting myself and my capabilities.

Practitioner: If you have a client or a younger person and if they say "I doubt myself" and you see that they doubt themselves and they do procrastination just because they're fearful of failure - how will you coach them? How will you heal them? You are a healer.

Five Action Items from Future Self

Practitioner: Ask her: "Give me five action items for next 15 days so that I can get this job that you have in 30 days."

Client: Let go of control and trust the process.

Practitioner: And how are you controlling it right now?

Client: I think I'm desperate right now.

Practitioner: You are getting it. So you have to work with surrender, not with desperation.

What is the second action item she's saying?

Client: Giving 100% in preparing for the job. Believing in myself.

Practitioner: What? Is there still procrastination? How will you stop doubting yourself?

So can you stop doubting yourself now so that things can move? And whenever you are having procrastination, you can ask a question: "What are you fearful of? What can be your failure?"

And then question it again: "What if the situation is something else?" Because if you see, these are your fears - nothing else. And why are you wasting your time in fears?

So moving forward whenever there is one self-doubt, you will replace it with something big. Do you promise to do that this week?

Client: I'll do that.
"""


def ingest_1_1_sessions():
    """Ingest all three 1:1 session transcripts."""
    print("=" * 60)
    print("INGESTING 1:1 SESSION TRANSCRIPTS")
    print("=" * 60)
    print()
    
    sessions = [
        {
            "content": SESSION_1_CONTENT,
            "video_title": "1:1 Session - Soul Purpose & Fear Work",
            "primary_pillar": "wellness",
            "emotional_patterns": ["not_enough", "fear_of_judgment", "unworthiness"],
            "root_causes": ["self-doubt", "forgotten power", "fear conditioning"],
            "description": "Session 9 - Working on fear of driving/water, co-creation, shifting from ego to God's consciousness"
        },
        {
            "content": SESSION_2_CONTENT,
            "video_title": "1:1 Discovery Call - Health & Relationships",
            "primary_pillar": "relationship",
            "emotional_patterns": ["unworthiness", "rejection", "not_enough", "boundary_issues"],
            "root_causes": ["father wound", "unavailable partners pattern", "ancestral imprint", "health anxiety"],
            "description": "Discovery call covering health issues, relationship patterns, limiting beliefs, blueprint concept"
        },
        {
            "content": SESSION_3_CONTENT,
            "video_title": "1:1 Session - Career Transition & Goal Setting",
            "primary_pillar": "career",
            "emotional_patterns": ["control_perfectionism", "not_enough", "overwhelm_exhaustion"],
            "root_causes": ["lack of clarity", "self-doubt", "desperation vs surrender"],
            "description": "Focus protocol, RPM goal-setting tool, career transition, meeting future self visualization"
        }
    ]
    
    total_chunks = 0
    
    for i, session in enumerate(sessions, 1):
        print(f"\n[{i}/3] Ingesting: {session['video_title']}")
        print(f"      Pillar: {session['primary_pillar']}")
        print(f"      Patterns: {session['emotional_patterns']}")
        
        chunks = ingest_enhanced_coaching_transcript(
            text_content=session["content"],
            video_title=session["video_title"],
            primary_pillar=session["primary_pillar"],
            emotional_patterns=session["emotional_patterns"],
            root_causes=session["root_causes"],
            speaker="Shweta",
            youtube_url=None,
            session_type="one_on_one"
        )
        
        total_chunks += chunks
        print(f"      ✓ Added {chunks} chunks")
    
    print()
    print("=" * 60)
    print(f"INGESTION COMPLETE: {total_chunks} total chunks added")
    print("=" * 60)
    
    return total_chunks


if __name__ == "__main__":
    ingest_1_1_sessions()
