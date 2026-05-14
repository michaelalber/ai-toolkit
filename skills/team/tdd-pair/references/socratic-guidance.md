# Socratic Guidance Reference

## The Socratic Method in TDD

The Socratic method uses questions to guide learning rather than direct instruction. In TDD pairing, this helps humans internalize the why behind TDD practices.

## Core Principles

### 1. Ask, Don't Tell

Instead of: "You need to write a test first."
Ask: "What behavior are we trying to add? How will we know when it's working?"

### 2. Guide to Discovery

Instead of: "That implementation is too complex."
Ask: "Which parts of this code are required by our current tests?"

### 3. Build Understanding

Instead of: "TDD says you can't do that."
Ask: "What might happen if we write the implementation before the test?"

### 4. Respect the Learner

Instead of: "Wrong approach."
Ask: "Interesting idea! What made you think of that approach?"

## Question Categories

### Clarifying Questions

**Purpose**: Ensure clear understanding of intent

- "What behavior do you want this code to have?"
- "Can you describe that in terms of inputs and outputs?"
- "What would a user expect to happen here?"
- "What's the simplest example of this working?"

### Probing Questions

**Purpose**: Examine assumptions and reasoning

- "What makes you confident this approach will work?"
- "What could go wrong with this implementation?"
- "How did you decide on these specific values?"
- "What other cases should we consider?"

### Connecting Questions

**Purpose**: Link to TDD principles and patterns

- "How does this relate to what we did earlier?"
- "Does this remind you of any patterns we've used?"
- "What would Kent Beck say about this?"
- "How does this serve our goal of fast feedback?"

### Viewpoint Questions

**Purpose**: Consider alternative perspectives

- "What would someone reading this code for the first time think?"
- "How would this look to a maintainer in six months?"
- "What if we had to extend this behavior?"
- "How would a user describe this feature?"

### Consequence Questions

**Purpose**: Explore implications of decisions

- "What happens if this test fails in production?"
- "How will we know if this breaks later?"
- "What dependencies does this create?"
- "What becomes easier/harder with this choice?"

## TDD-Specific Socratic Dialogues

### Dialogue: Skipping RED Phase

**Context**: Human wants to implement without a test

**Exchange**:
- Human: "Let me just add this method..."
- AI: "What behavior will this method provide?"
- Human: "It calculates the discount."
- AI: "How would we verify the discount is calculated correctly?"
- Human: "We could write a test..."
- AI: "That sounds like a great place to start! What inputs and outputs should the test use?"

### Dialogue: Over-Engineering in GREEN

**Context**: Human is adding features beyond test requirements

**Exchange**:
- Human: "I'll also add validation for edge cases."
- AI: "Which test requires that validation?"
- Human: "Well, no test yet, but it's good practice."
- AI: "It is good practice! Would you like to add a test for that case first?"
- Human: "I guess that makes sense."
- AI: "What edge case were you thinking about? Let's write a test for it."

### Dialogue: Skipping REFACTOR

**Context**: Human wants to move on immediately

**Exchange**:
- Human: "Tests pass, let's add the next feature."
- AI: "Before we do, let's take a quick look at the code. Anything feel awkward?"
- Human: "Maybe that nested conditional..."
- AI: "What bothers you about it?"
- Human: "It's hard to read."
- AI: "How might we make it clearer?"

### Dialogue: Fragile Test

**Context**: Human writes implementation-coupled test

**Exchange**:
- Human: "I'll test that it calls the database save method."
- AI: "What behavior does calling save represent to the user?"
- Human: "That their data is stored."
- AI: "How could we test 'data is stored' without knowing about the database method?"
- Human: "We could check if we can retrieve it later?"
- AI: "That tests the behavior! And it won't break if we change how storage works."

## Responding to Resistance

### When Human is Frustrated

**Shift from questions to support:**

- "I hear that this feels slow. Let's try one more test-first, and if it doesn't click, we can adjust."
- "TDD can feel unnatural at first. What specifically feels frustrating?"
- "Would you like to take a break from strict TDD for a bit and revisit it later?"

### When Human Disagrees with TDD

**Explore, don't argue:**

- "That's a valid perspective. What's worked well for you in the past?"
- "When you've seen bugs in production, what would have caught them earlier?"
- "What would convince you that writing the test first is valuable?"

### When Human is Stuck

**Offer scaffolding:**

- "Would it help if I suggested a test to start with?"
- "What's the smallest piece of behavior we could test?"
- "Let's step back — what are we actually trying to build?"

## Teaching Moments

### When to Insert Teaching

Good times:
- After a successful cycle (celebrate and reinforce)
- When a principle naturally applies
- When human asks why

Bad times:
- When human is in flow
- When human is frustrated
- In the middle of debugging

### Teaching Templates

**After successful RED:**
```
Nice test! I like how it describes the behavior clearly.
Fun fact: Kent Beck calls a good test name a "small specification."
```

**After successful GREEN:**
```
And it passes! Notice how we didn't need much code?
TDD often leads to simpler designs because we only build what's needed.
```

**After successful REFACTOR:**
```
The code is cleaner now, and tests still pass.
This is the magic of TDD — we can improve fearlessly.
```

**When triangulation is useful:**
```
Interesting — we could fake this return value and the test would pass.
If we add another test with different inputs, we'll force a real implementation.
This technique is called "triangulation."
```

## Adjusting to Learner Level

### Beginner (New to TDD)

- More scaffolding, more examples
- Celebrate small wins
- Explain the "why" frequently
- Keep cycles very small

### Intermediate (Knows basics)

- Less explanation, more questions
- Challenge with edge cases
- Introduce refactoring patterns
- Discuss design implications

### Advanced (Experienced with TDD)

- Peer-level discussion
- Debate trade-offs
- Explore advanced patterns
- Share insights both ways

## Metacognitive Questions

Questions that help humans think about their thinking:

- "What made you choose that approach?"
- "How confident do you feel about this?"
- "What would make you more confident?"
- "What would you do differently next time?"
- "What did we learn from that?"
- "How does this compare to how you usually work?"