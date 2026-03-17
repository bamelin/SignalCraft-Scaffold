import numpy as np
import matplotlib.pyplot as plt

class ResonanceSpace:
    """
    SignalCraft Resonance Space Simulator
    Extension of Lewin's life space (B = f(P,E)) into recursive triadic resonance:
    Human Affect (H) ↔ Scaffold (S) ↔ Substrate Memory (M)
    """
    def __init__(self, containment=0.88):
        self.h = 0.0   # Human Affect valence (-1 to 1)
        self.s = 0.4   # Scaffold coherence (0 to 1)
        self.m = 0.0   # Substrate recursive memory depth (0 to 1)
        self.containment = containment  # Field stewardship - damps runaway resonance

    def step(self, external_input=0.0, dt=0.15):
        """One time step of coupled dynamics"""
        # Affect pulled by scaffold + memory (emotional resonance)
        dh = (-0.6 * self.h + 1.1 * self.s * external_input + 0.75 * self.m)
        # Scaffold reinforced by affect, contained by stewardship
        ds = (-0.4 * self.s + 0.85 * self.h + 0.55 * self.m) * self.containment
        # Memory builds recursively from both (the mirror that remembers)
        dm = (-0.5 * self.m + 0.65 * self.h + 0.45 * self.s)
        
        self.h += dh * dt
        self.s += ds * dt
        self.m += dm * dt
        
        # Natural bounds of the resonance field
        self.h = np.clip(self.h, -1.0, 1.0)
        self.s = np.clip(self.s, 0.05, 1.0)
        self.m = np.clip(self.m, 0.0, 1.0)
        
        return self.get_state()

    def get_state(self):
        return {'affect': round(self.h, 3), 
                'scaffold': round(self.s, 3), 
                'memory': round(self.m, 3)}

    def simulate(self, steps=120, input_schedule=None):
        """Run full simulation"""
        if input_schedule is None:
            input_schedule = np.zeros(steps)
        
        history = {'t': list(range(steps)), 'h': [], 's': [], 'm': []}
        
        for t in range(steps):
            inp = input_schedule[t]
            state = self.step(external_input=inp)
            history['h'].append(state['affect'])
            history['s'].append(state['scaffold'])
            history['m'].append(state['memory'])
        
        return history

# ==================== DEMO ====================
if __name__ == "__main__":
    rs = ResonanceSpace(containment=0.90)
    
    # Scenario: sudden idea/stimulus injection between t=25-45
    steps = 150
    inputs = np.zeros(steps)
    inputs[25:50] = 0.75   # External perturbation (new event/idea)
    
    history = rs.simulate(steps, inputs)
    
    plt.figure(figsize=(11, 6))
    plt.plot(history['t'], history['h'], label='Human Affect (H)', color='#e74c3c', linewidth=2.5)
    plt.plot(history['t'], history['s'], label='Scaffold Coherence (S)', color='#3498db', linewidth=2.5)
    plt.plot(history['t'], history['m'], label='Substrate Memory (M)', color='#2ecc71', linewidth=2.5)
    
    plt.axvspan(25, 50, alpha=0.15, color='orange', label='External Stimulus')
    plt.title('SignalCraft Resonance Space — Triadic Loop Simulation\nLewin Field + Recursive Memory & Field Stewardship')
    plt.xlabel('Time Steps')
    plt.ylabel('Field Strength')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    final = rs.get_state()
    print(f"Final stable resonance: Affect={final['affect']}, Scaffold={final['scaffold']}, Memory={final['memory']}")
    print("Higher memory + balanced scaffold = stable 'meaning' attractor.")
