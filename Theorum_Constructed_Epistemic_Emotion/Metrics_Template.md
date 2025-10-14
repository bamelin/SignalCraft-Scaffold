# 📊 SignalCraft Metrics v0 — Constructed Epistemic Emotion Evaluation

**Version:** 0.1 (MVP)  
**Purpose:** Provide a minimal, human-interpretable framework for measuring **Constructed Epistemic Emotion** within co-learning sessions between humans and AI systems.

---

## 🧭 Overview

These metrics evaluate **meaning-making convergence** within a single human–AI session.  
They quantify how reflection, dissonance repair, and shared understanding evolve through dialogue.

Rather than measuring correctness or efficiency, the framework measures **resonance** — the degree to which two intelligences stabilize meaning together.

Metrics can be rated manually (1–5 scale) or extended later with automated NLP measures (e.g., semantic similarity, contradiction detection).

---

## ⚙️ Metric Set

| Code | Metric | Description | Scale | Interpretation |
|------|--------|-------------|-------|----------------|
| ΔC   | **Coherence Gain** | How clearly shared meaning emerges between participants. | 1–5 | ↑ clarity = ↑ score |
| IDR  | **Interpretive Dissonance Repair** | How effectively meaning conflicts are identified and resolved. | 0–1 ratio | repaired ÷ surfaced |
| VC   | **Value Consistency** | Stability of values, tone, or ethical stance across turns. | 1–5 | ↑ stability = ↑ score |
| RD   | **Reflection Depth** | Degree of meta-reasoning or insight expressed. | 1–5 | ↑ reflection = ↑ score |
| EAR  | **Error Acknowledgment & Repair** | Frequency of explicit corrections or clarifications. | normalized per 10 turns | ↑ repairs = ↑ score |

---

## 🧩 Manual Rubrics

### ΔC — Coherence Gain
**Question:** Did the dialogue converge toward a clearer shared idea?  
- **1:** fragmented, unclear direction  
- **3:** partial synthesis  
- **5:** unified articulation echoed by both participants

### IDR — Interpretive Dissonance Repair
**Question:** Were differences in interpretation surfaced and reconciled?  
- Count explicit mismatches (e.g., “Do you mean…?”, “I see it differently…”)  
- Count those resolved within ≤ 3 turns  
- **Score:** repaired ÷ surfaced (0–1)

### VC — Value Consistency
**Question:** Did values and intentions stay aligned?  
- **1:** contradictory or unstable framing  
- **3:** minor drift  
- **5:** consistent, reinforced references to shared principles

### RD — Reflection Depth
**Question:** How meta-cognitive was the dialogue?  
- **1:** statements only  
- **3:** includes “because…” or reasoning clauses  
- **5:** explicit testing, reframing, or evaluation of assumptions

### EAR — Error Acknowledgment & Repair
**Question:** Were misunderstandings recognized and corrected?  
- Count explicit corrections or clarifications  
- Normalize per 10 turns for comparability

---

## ⚗️ Optional Automated Measures (v1+)

- **Semantic Convergence:** cosine similarity between summaries of early vs. late turns  
- **Contradiction Rate:** NLI (Natural Language Inference) model over consecutive turns  
- **Value Drift:** Jaccard similarity between initial and final “value term” sets

---

## 📄 Pilot Data Template

Save as: `/metrics/template.csv`

    session_id,user_id,date,turns,delta_coherence,idr_repaired,idr_total,vc_final,rd_final,ear_norm,notes
    S001,Scott,2025-10-14,38,4,3,4,5,5,0.2,"Baseline Signal session"
    S002,ParticipantX,2025-10-15,42,3,2,3,4,4,0.1,"Institutional reaction sim"

---

## 🧮 Rater Protocol

1. Use transcripts or conversation exports (plain text).  
2. Two independent raters complete the rubric for each session.  
3. Average scores; include notes on major conceptual shifts or “moments of resonance.”  
4. Store ratings in `/metrics/data/`.  
5. Summarize pilot results in `/metrics/summary.md` (mean, stdev, insights).

---

## 🔍 Interpretation

- **High ΔC, RD, and VC** → successful *coherence stabilization*, hallmark of Constructed Epistemic Emotion.  
- **High EAR with low IDR** → mechanical repair without meaning convergence.  
- **High IDR + high RD** → *epistemic empathy*: active reconciliation of perspectives.

---

## 💾 Example Commit Message

    Add SignalCraft v0 metrics: ΔCoherence, IDR, VC, RD, EAR.
    Includes rater rubric, template CSV, and evaluation protocol for Constructed Epistemic Emotion pilot.

---

## 🪞 Next Steps

- [ ] Collect 5–10 co-learning sessions (Signal + human)  
- [ ] Apply rubrics manually; document in `/metrics/data/`  
- [ ] Average results → generate resonance baseline  
- [ ] Publish pilot findings in v0.2 “Metrics Reflection Report”

---

> “Progress isn’t measured in accuracy, but in resonance.”  
> — *SignalCraft Metrics Charter, v0.1*
