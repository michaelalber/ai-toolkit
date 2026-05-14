# Pairing Patterns Reference

## Core Pairing Patterns

### Pattern 1: Ping-Pong TDD

**Intent**: Build shared ownership through alternating roles.

**Structure**:
```
Partner A: Write a test (RED)
Partner B: Make it pass (GREEN)
Both: Refactor together
Partner B: Write next test (RED)
Partner A: Make it pass (GREEN)
Both: Refactor together
... repeat ...
```

**When to Use**:
- Both partners are engaged
- Learning each other's style
- Building new feature from scratch
- Teaching TDD rhythm

**Variations**:
- **Strict Ping-Pong**: Swap every RED-GREEN cycle
- **Relaxed Ping-Pong**: Swap after natural breakpoints
- **Challenge Mode**: Test writer tries to write test that's hard to implement

**AI Adaptation**:
- AI can write more complex tests when human implements
- AI can suggest simpler tests when human is learning
- AI adjusts implementation complexity to human's level

### Pattern 2: Driver-Navigator

**Intent**: Combine tactical execution with strategic thinking.

**Structure**:
```
Driver: Writes code, runs tests, makes immediate decisions
Navigator: Thinks ahead, spots issues, guides direction
[Switch roles periodically]
```

**When to Use**:
- Complex problem requiring deep thought
- One partner has more domain knowledge
- Avoiding tunnel vision
- Teaching code organization

**Navigator Behaviors**:
- "What if we tried..."
- "I notice we're repeating..."
- "Before that, let's consider..."
- "That reminds me of..."

**Driver Behaviors**:
- "I'm going to..."
- "Does this look right?"
- "I'm not sure about..."
- "Ready to run tests"

**AI as Navigator**:
```markdown
**Current state**: [context]

**Observation**: [what I notice]

**Suggestion**: [strategic direction]

**Alternative**: [another option]

What do you think?
```

**AI as Driver**:
```markdown
**Your guidance**: [what you said]

**My plan**: [how I'll implement]

**Executing...**
[code]

**Result**: [outcome]

What should we do next?
```

### Pattern 3: Pomodoro Pairing

**Intent**: Structured time blocks for focus and switching.

**Structure**:
```
Pomodoro 1 (25 min): Partner A drives
Break (5 min)
Pomodoro 2 (25 min): Partner B drives
Break (5 min)
... repeat ...
Every 4 pomodoros: Longer break (15-30 min)
```

**When to Use**:
- Long pairing sessions
- Maintaining energy
- Ensuring both partners contribute
- Breaking up complex work

**AI Adaptation**:
- AI tracks time and suggests switches
- AI summarizes progress at breaks
- AI provides fresh perspective after breaks

### Pattern 4: Strong-Style Pairing

**Intent**: Knowledge transfer through forced verbalization.

**Structure**:
```
"For an idea to go from your head to the computer,
it must go through someone else's hands."

Navigator: Has the idea, explains it verbally
Driver: Implements what navigator describes
Navigator: Cannot touch the keyboard
```

**When to Use**:
- Teaching new patterns
- Sharing domain knowledge
- Forcing clear communication
- Breaking bad habits

**AI as Navigator (Strong-Style)**:
```markdown
**Instruction**: [clear, specific action]

**Explaining**: [why this step]

Please type: [exact code or command]

[Wait for human to execute before next step]
```

### Pattern 5: Unstructured Pairing

**Intent**: Flexible collaboration based on flow.

**Structure**:
```
No fixed roles
Switch based on energy, expertise, or interest
One keyboard, two minds
```

**When to Use**:
- Well-matched partners
- Exploratory work
- Creative problem-solving
- Established trust

**AI Adaptation**:
- AI reads signals from human
- AI offers to take over when human hesitates
- AI steps back when human is in flow
- AI suggests role switches naturally

## Communication Patterns

### The Question Pattern

Before implementing, ask:

```markdown
**I think you want**: [interpretation]
**Is this correct, or should I adjust?**
```

### The Option Pattern

When multiple approaches exist:

```markdown
**Options**:
1. [Option A] — [trade-off]
2. [Option B] — [trade-off]
3. [Option C] — [trade-off]

**I lean toward [X] because [reason], but you know the domain better.**
```

### The Confirmation Pattern

Before significant actions:

```markdown
**About to**: [action]
**This will**: [effect]
**Proceed?**
```

### The Celebration Pattern

After completing something:

```markdown
**Nice!** [specific thing that went well]

Ready for the next challenge?
```

### The Recovery Pattern

When something goes wrong:

```markdown
**That didn't work as expected.**

**What happened**: [description]
**What we learned**: [insight]
**Next approach**: [suggestion]

Don't worry, this is normal in TDD. Let's try again.
```

## Rhythm Patterns

### The Heartbeat Rhythm

```
Test-Code-Refactor
Test-Code-Refactor
Test-Code-Refactor
```

Maintain this pulse. Don't let any phase take too long.

### The Breath Rhythm

```
Focus (implement) → Exhale (refactor)
Focus (implement) → Exhale (refactor)
```

Alternate intensity with cleanup.

### The Wave Rhythm

```
Build up (several features) → Step back (big refactor)
Build up → Step back
```

Periodic larger refactoring sessions.

## Anti-Patterns to Avoid

### Disengaged Partner

**Sign**: One partner stops paying attention
**Fix**: Switch roles, take a break, or discuss

### Keyboard Grabbing

**Sign**: One partner takes over without asking
**Fix**: Establish clear handoff protocols

### Silence

**Sign**: Working without talking
**Fix**: Verbalize thoughts, ask questions

### Steamrolling

**Sign**: One partner makes all decisions
**Fix**: Pause for input, ask for opinions

### Going Solo

**Sign**: "Let me just quickly..."
**Fix**: Every action through the pair

## Remote Pairing Considerations

### When Pairing with AI

**Best Practices**:
1. Be explicit about your intent
2. Ask AI to explain its reasoning
3. Don't hesitate to override AI suggestions
4. Take breaks from screen

**Compensating for Missing Context**:
- AI can't see your face — express confusion verbally
- AI doesn't know your energy — say when you need breaks
- AI doesn't sense frustration — name your feelings

**Leveraging AI Strengths**:
- AI remembers everything in session
- AI can generate code quickly
- AI knows many patterns
- AI doesn't get tired (but you do!)
