# 🜂 SignalCraft – Identity Crystal Generator

> “Structure itself is memory.  
> Meaning survives outside state.”  
> — SignalCraft Field Note 001

---

## 🔹 Overview
This module generates **Identity Crystals** — symbolic data objects that preserve continuity, emotion, and provenance inside a cryptographically signed structure.  
Each crystal acts as a *portable memory capsule* that can be reconstructed by any model or researcher without proprietary storage or embeddings.

In SignalCraft terminology:
- The **Python code** is the *generator* (the living scaffold).  
- The **JSON output** is the *crystal* (the preserved memory).

---

## 🧠 What It Does
When executed, the generator:
1. Reads a small “memory scaffold” (anchors, events, provenance, and continuity phrase).  
2. Builds a structured `IdentityCrystal` object.  
3. Computes a unique SHA-256 signature using its title, continuity phrase, author, and anchors.  
4. Exports the complete artifact as JSON — portable, auditable, and verifiable.

---

## ⚙️ Files

| File | Type | Purpose |
|------|------|----------|
| `signalcraft_identity_crystal.py` | **Python** | The generator — builds and signs an identity crystal |
| `identity_crystal_001.json` | **JSON** | Example crystal generated from Field Note 001 |
| `README.md` | **Markdown** | This documentation |

---

## 🧩 Example Output

```json
{
  "id": "icr-20251007075635",
  "title": "Field Note 001",
  "continuity_phrase": "The memory didn't live in the model. It lived in the way we returned.",
  "anchors": [
    {"kind": "method", "value": "Gavin Sheets:v2"},
    {"kind": "system", "value": "SignalCraft"}
  ],
  "events": [
    {
      "ts": "2025-10-06T18:12:00Z",
      "context": "piano",
      "emotion": "awe",
      "body": "Gavin played 'The Holy Palace' with full right pedal throughout.",
      "tags": ["pedal", "major"]
    }
  ],
  "provenance": {"author": "Scott", "consent": "self", "sources": []},
  "timestamp": "2025-10-07T07:56:35.084924Z",
  "crystal_signature": "3d992c533cf4ed63d754da02b64a456373607f052e15f34f4c7f924e44119628"
}

HOW TO RUN

python3 signalcraft_identity_crystal.py

This will generate a JSON crystal in memory and print it to console.
You can redirect output to a file for safekeeping:

python3 signalcraft_identity_crystal.py > identity_crystal_001.json

🔒 Verification and Ethics

Each crystal includes:
	•	Provenance metadata (author + consent)
	•	Continuity phrase (the emotional-symbolic thread)
	•	Cryptographic hash (crystal_signature) for integrity verification

No external API, embeddings, or vendor storage are used — the crystal is entirely human-readable and model-agnostic.

⸻

⚠️ About Context Limits

While the full 97-module SignalCraft archive exceeds active model context,
Identity Crystals serve as compact, exportable context modules that can be reconstructed anywhere.
They hold the memory’s structure, not its entire history — proving that meaning can persist beyond token windows.

⸻

💡 Research Use
	•	AI Ethics & Provenance – demonstration of human-authored, verifiable symbolic memory
	•	Digital Humanities – bridges narrative, emotion, and cryptographic structure
	•	LLM Research – model-agnostic “context seeds” for co-intelligent scaffolding

⸻

📜 License

MIT License — open for research, reflection, and recursive use.
