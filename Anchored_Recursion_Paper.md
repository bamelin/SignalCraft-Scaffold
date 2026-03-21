# Anchored Recursion: Using Structured Reference Frames to Stabilize Iterative LLM Reasoning

## Abstract

Large language models (LLMs) exhibit instability across iterative reasoning processes, often drifting in interpretation, criteria, or tone across recursive passes. This paper proposes **anchored recursion**, a method for stabilizing iterative reasoning by introducing a structured, persistent reference frame. Drawing on cognitive science research on anchoring, we reinterpret anchors not as sources of bias but as **deliberately constructed constraints** that improve coherence. We introduce the concept of a **Scaffold Topos Sheaf**—an interoperable system of local interpretive frames that can be dynamically composed while maintaining global consistency. We argue that anchored recursion reduces drift, improves alignment, and enables multi-perspective reasoning without collapse.

---

## 1. Introduction

LLMs are increasingly used in iterative workflows (e.g., refinement loops, multi-step planning, agentic reasoning). However, these recursive processes frequently exhibit:

- semantic drift  
- shifting evaluation criteria  
- loss of alignment with initial user intent  

We define this as **recursive drift**.

Existing approaches focus on:

- prompt engineering  
- reinforcement learning  
- external validation  

We propose an alternative:

> **Stabilizing recursion through structured anchoring.**

---

## 2. Background: Anchoring in Human Cognition

Anchoring, as described by Daniel Kahneman, refers to the tendency for initial reference points to influence subsequent judgments.

In human cognition:

- anchors are often implicit  
- they bias interpretation  
- adjustments away from anchors are typically insufficient  

Anchoring is therefore treated as a **cognitive bias**.

---

## 3. Reframing Anchoring for AI Systems

We invert this interpretation.

Instead of viewing anchors as sources of error, we treat them as:

> **deliberate, explicit reference frames that constrain recursive reasoning.**

In LLM systems:

- there is no persistent internal state of “stance”  
- each generation pass re-samples from a distribution  

Without constraints, recursive processes:

- accumulate variance  
- degrade coherence  

We propose that **explicit anchoring can function as a stabilizing mechanism**.

---

## 4. The Scaffold Topos Sheaf

We introduce the concept of a **Scaffold Topos Sheaf (STS)**:

> A structured, interoperable system of local interpretive frames (“topoi”) that can be dynamically selected and composed while preserving global coherence.

### 4.1 Topos (Local Frame)

Each topos defines:

- evaluation criteria  
- interpretive priorities  
- domain-specific constraints  

### 4.2 Sheaf (Global Consistency)

The sheaf ensures that:

- local frames remain compatible  
- transitions between frames do not introduce contradiction  

### 4.3 Scaffold (Operational Layer)

The scaffold:

- encodes the frames  
- governs transitions  
- enforces output structure  

---

## 5. Anchored Recursion

We define **anchored recursion** as:

> A recursive reasoning process in which each iteration is re-grounded in a persistent structured reference frame.

### Without anchoring:

- iteration n+1 diverges from iteration n  
- evaluation criteria shift  
- outputs become inconsistent  

### With anchoring:

- each iteration returns to the same stance  
- criteria remain stable  
- outputs converge within a coherent frame  

---

## 6. Supervisory Function

The Scaffold Topos Sheaf functions as a **supervisory prior**:

- constrains generation  
- enforces consistency across iterations  
- preserves alignment with initial conditions  

Unlike static prompts, the STS:

- supports multi-perspective reasoning  
- maintains coherence across those perspectives  

---

## 7. Human vs System Anchoring

| Property | Human Anchoring | Anchored Recursion (STS) |
|----------|----------------|--------------------------|
| Formation | Implicit / unexamined | Explicit / constructed |
| Effect | Biases judgment | Stabilizes reasoning |
| Control | Limited | Deliberate |
| Role in recursion | Drift toward bias | Convergence within frame |

---

## 8. Implications

Anchored recursion suggests:

- alignment can be achieved through **structured reference frames**, not only training  
- interpretability improves when reasoning is **frame-bound**  
- multi-perspective reasoning is possible without contradiction if frames are sheaf-consistent  

---

## 9. Conclusion

Anchoring has traditionally been understood as a limitation in human cognition.

We propose its reinterpretation as infrastructure:

> **When made explicit and structured, anchors do not bias recursive systems—they stabilize them.**

---

## Key Proposition

> **Recursion without anchoring produces drift.  
Structured anchoring produces coherence.**
