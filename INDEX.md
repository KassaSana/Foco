# 📋 Foco Interview Documentation Index

Welcome to the Foco technical interview preparation suite! This documentation is designed to help you defend your project in high-stakes technical interviews (Citadel, Jane Street, HRT, etc.).

---

## 🎯 **How to Use This Documentation**

### **For a 30-minute interview:**
1. Read **QUICK_REFERENCE.md** (5 minutes)
2. Memorize the 30-second pitch and key metrics
3. Practice whiteboard diagram (5 minutes)
4. Review code snippets (5 minutes)

### **For a 1-hour technical deep dive:**
1. Read **TECHNICAL_CHEATSHEET.md** in full (30 minutes)
2. Study all code examples and design patterns
3. Practice explaining 3 technical challenges
4. Review **SYSTEM_DESIGN_VISUAL.md** for whiteboarding

### **For system design round:**
1. Start with **SYSTEM_DESIGN_VISUAL.md**
2. Practice drawing component interaction diagram
3. Memorize data flow and threading model
4. Be ready to discuss scalability trade-offs

---

## 📚 **Document Hierarchy**

```
Documentation Suite
│
├─ QUICK_REFERENCE.md ⚡ [START HERE]
│   └─ 1-page cheat sheet
│   └─ 30-second pitch
│   └─ Key metrics to memorize
│   └─ Emergency interview prep (15 min read)
│
├─ TECHNICAL_CHEATSHEET.md 📖 [COMPREHENSIVE]
│   └─ Full system architecture
│   └─ Design patterns & algorithms
│   └─ Code examples with explanations
│   └─ Interview talking points
│   └─ Technical depth questions & answers
│   └─ Performance analysis
│   └─ Citadel-specific angles (45 min read)
│
├─ SYSTEM_DESIGN_VISUAL.md 🎨 [WHITEBOARDING]
│   └─ ASCII diagrams for all components
│   └─ Data flow visualizations
│   └─ State machine diagrams
│   └─ Threading model
│   └─ Whiteboard practice templates (30 min read)
│
└─ INDEX.md 📋 [THIS FILE]
    └─ Navigation guide
    └─ Study strategies
```

---

## 🎓 **Study Plan by Timeline**

### **1 Week Before Interview:**
- [ ] Day 1-2: Read TECHNICAL_CHEATSHEET.md thoroughly
- [ ] Day 3-4: Practice whiteboarding with SYSTEM_DESIGN_VISUAL.md
- [ ] Day 5: Code walkthrough - explain each component out loud
- [ ] Day 6: Mock interview with friend using QUICK_REFERENCE.md
- [ ] Day 7: Review and polish weak areas

### **1 Day Before Interview:**
- [ ] Morning: Re-read TECHNICAL_CHEATSHEET.md (30 min)
- [ ] Noon: Practice 30-second pitch 10 times
- [ ] Afternoon: Whiteboard practice (draw architecture 5 times)
- [ ] Evening: Review key metrics and code snippets

### **1 Hour Before Interview:**
- [ ] Read QUICK_REFERENCE.md cover to cover
- [ ] Memorize metrics: <2% CPU, 50MB RAM, 1000+ events
- [ ] Practice 30-second pitch 3 times
- [ ] Review closing statement

---

## 🔑 **Essential Topics to Master**

### **Architecture (Must Know):**
✅ 3-layer design (UI, Logic, Data)  
✅ 5 core components (Monitor, Manager, Enforcer, Classifier, Logger)  
✅ Event-driven architecture  
✅ Threading model (main + daemon)  

### **Code Patterns (Must Know):**
✅ Win32 window detection (`GetForegroundWindow`)  
✅ Pattern-matching classification  
✅ State machine (FocusState enum)  
✅ Daemon thread setup (`daemon=True`)  
✅ Atomic file writes  

### **Design Decisions (Must Explain):**
✅ Rule-based vs. ML classification  
✅ 1-second polling vs. event hooks  
✅ JSON files vs. SQLite  
✅ Dual-layer blocking (hosts + process)  
✅ Thread-safe single-writer pattern  

### **Performance (Must Memorize):**
✅ <2% CPU overhead  
✅ ~50MB memory footprint  
✅ 1 event/second capture rate  
✅ 85% classification accuracy  
✅ 40+ apps/sites blocked  

---

## 🎯 **Interview Format Strategies**

### **For Behavioral Rounds:**
- Use "Problem → Solution → Impact" framework
- Emphasize ADHD user research and iteration
- Quantify results (1,000+ events, 40+ blocks, 10+ users)

### **For Technical Rounds:**
- Start with high-level architecture diagram
- Drill down into 1-2 components in depth
- Discuss trade-offs and alternatives
- Show code snippets from memory

### **For System Design Rounds:**
- Draw component interaction first
- Explain data flow with arrows
- Discuss scalability bottlenecks
- Propose enterprise architecture

### **For Coding Rounds:**
- Implement classification logic (pattern matching)
- Implement state machine transitions
- Implement session tracking algorithm

---

## 🧠 **Memory Techniques**

### **The 5-5-5 Method:**
- **5 components:** Monitor, Manager, Enforcer, Classifier, Logger
- **5 metrics:** <2% CPU, 50MB RAM, 1000 events, 40 blocks, 85% accuracy
- **5 challenges:** Non-blocking UI, pseudo-productive, unbypassable blocking, thread safety, idle detection

### **MEDAL Framework (for each component):**
- **M**echanism: How it works technically
- **E**xample: Code snippet showing usage
- **D**ecision: Why this approach vs. alternatives
- **A**lternative: What else you considered
- **L**imitation: Trade-offs and constraints

---

## 💡 **Pro Tips**

1. **Bring printed QUICK_REFERENCE.md** - Review in waiting room
2. **Practice whiteboarding** - Draw architecture 20+ times until muscle memory
3. **Memorize 3 code snippets** - Win32 detection, classification, threading
4. **Prepare 3 challenge stories** - Explain problem, solution, result
5. **Know your numbers** - Metrics are more memorable than features
6. **Connect to interviewer's domain** - Trading systems have similar patterns
7. **Be honest about limitations** - Shows maturity and critical thinking

---

## 🚀 **High-Priority Sections**

If you only have 30 minutes, read these sections in order:

1. **QUICK_REFERENCE.md** - Entire document (10 min)
2. **TECHNICAL_CHEATSHEET.md** - Executive Summary + Architecture (10 min)
3. **SYSTEM_DESIGN_VISUAL.md** - Component Interaction Diagram (5 min)
4. Practice 30-second pitch out loud (5 min)

---

## 📊 **Self-Assessment Checklist**

Before your interview, verify you can:

- [ ] Explain architecture in 30 seconds
- [ ] Draw component diagram from memory in 60 seconds
- [ ] Explain threading model clearly
- [ ] Write Win32 detection code on whiteboard
- [ ] Discuss 3 technical challenges with solutions
- [ ] Explain rule-based vs. ML trade-off
- [ ] Describe jail mode dual-layer blocking
- [ ] Recite key metrics (<2% CPU, 50MB, 1000+, 40+, 85%)
- [ ] Answer "why not ML?" convincingly
- [ ] Connect to trading systems (Citadel-specific)

---

## 🎤 **Sample Interview Questions & Answers**

### **Q: "Walk me through the architecture of Foco."**
**A:** "Foco has a 3-layer architecture. The **UI layer** is a Tkinter dashboard with 3 tabs. The **logic layer** contains 5 components: Activity Monitor polls Win32 APIs every second, Category Engine classifies work into 4 categories, Focus Manager runs Pomodoro/Deep Work timers, Productivity Enforcer blocks distractions through hosts file and process termination, and Stats Calculator aggregates metrics. The **data layer** uses JSON files for session storage and Win32 APIs for OS integration."

*(See QUICK_REFERENCE.md page 1 for more)*

### **Q: "How do you ensure the UI doesn't freeze during monitoring?"**
**A:** "I use a daemon thread for background monitoring that polls every 1 second, separate from the Tkinter mainloop thread. The daemon writes to DataLogger, the UI thread reads from it. Single-writer/multiple-reader pattern means no locks needed. The daemon=True flag ensures the thread terminates cleanly when the user closes the app."

*(See TECHNICAL_CHEATSHEET.md "Core Design Patterns" section)*

### **Q: "Why pattern matching instead of machine learning?"**
**A:** "Three reasons: **Speed** - pattern matching runs in O(n) time with no inference latency. **Interpretability** - users need to understand why their activity was classified. **Simplicity** - no training data collection, no model versioning, no deployment complexity. I get 85% accuracy which is sufficient for a personal productivity tool."

*(See QUICK_REFERENCE.md "Design Decisions" section)*

---

## 🏆 **Final Checklist (Print This)**

**Night Before:**
- [ ] Read all 3 documents at least once
- [ ] Practice 30-second pitch 10 times
- [ ] Draw architecture diagram 5 times
- [ ] Get 8 hours of sleep

**Morning Of:**
- [ ] Review QUICK_REFERENCE.md
- [ ] Practice whiteboarding once
- [ ] Memorize key metrics

**In Waiting Room:**
- [ ] Read QUICK_REFERENCE.md one more time
- [ ] Visualize drawing architecture diagram
- [ ] Take 3 deep breaths

**During Interview:**
- [ ] Lead with 30-second pitch when asked "tell me about Foco"
- [ ] Draw as you explain (visual + verbal)
- [ ] Use numbers to support claims
- [ ] Connect to interviewer's domain

---

## 📞 **Document Quick Links**

- **Emergency Prep (15 min):** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Full Technical (45 min):** [TECHNICAL_CHEATSHEET.md](TECHNICAL_CHEATSHEET.md)
- **Whiteboarding (30 min):** [SYSTEM_DESIGN_VISUAL.md](SYSTEM_DESIGN_VISUAL.md)
- **Main README:** [README.md](README.md)

---

## 🎯 **Success Metrics**

You're ready when you can:
1. Pitch Foco in 30 seconds confidently
2. Draw architecture in 60 seconds clearly
3. Explain 3 technical challenges fluently
4. Discuss trade-offs thoughtfully
5. Connect to interviewer's domain naturally

---

**Good luck with your Citadel interview! You've built something impressive. Now go show them why.** 🚀

---

*Last Updated: February 2026*  
*Optimized for: Citadel, Jane Street, HRT, Two Sigma, Jump Trading technical interviews*
