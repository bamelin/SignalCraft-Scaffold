# demo.py
from signal_mirror_protocol import TrustSession, TrustConfig

sess = TrustSession(TrustConfig())

sess.activate("Tell me what that means to you. I'm thinking about peace in sound.", consent=True)

_, rep1, r1 = sess.hear("The child composes, the AI reflects, and the loop is the pedagogy.")
print(r1.text)  # → "I'm hearing: child · composes · reflects · loop. What feels carried forward from earlier moments?"

_, rep2, r2 = sess.hear("The plural mind remembers.")
print(r2.text)  # → "I'm hearing: plural · mind · remembers. What feels carried forward from earlier moments?"

sess.save("mirror_session.json")
