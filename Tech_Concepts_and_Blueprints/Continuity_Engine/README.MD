how to run
	1.	save as continuity_engine_min.py
	2.	pip install fastapi uvicorn pydantic
	3.	uvicorn continuity_engine_min:app --reload
	4.	hit:

	•	POST /invoke → {"actor":"human","pattern_mode":"live","prompt":"hello"}
	•	POST /reflect → {"session_id":"...","content":"...", "ethics":{"principle":"reflection","confidence":0.9}}
	•	GET /audit?session_id=...
