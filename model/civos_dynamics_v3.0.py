import os
import numpy as np
import matplotlib.pyplot as plt

# --- 0. Environmental Assurance Layer ---
output_dir = '/home/workdir/artifacts'
os.makedirs(output_dir, exist_ok=True)

# --- 1. Time-Dependent External Pressure Function X(t) ---
def X_t(t, k=0.1, t0=50.0):
    """
    Models the non-homogeneous external erosion velocity (Silent Invasion vector).
    """
    return 1.0 / (1.0 + np.exp(-k * (t - t0)))

# --- 2. CivOS v3.0 Hybrid Simulation Kernel ---
def run_civos_v3_core(num_paths=100, t_max=200, dt=0.1, scenario='none'):
    """
    Executes a synchronized multi-path hybrid simulation coupling continuous 
    multivariate SDE layers with a non-homogeneous discrete Markov Phase Layer.
    """
    N_steps = int(t_max / dt)
    t_axis = np.linspace(0, t_max, N_steps)
    
    # Continuous State Vector X(t) Buffers [num_paths, N_steps]
    C_paths = np.zeros((num_paths, N_steps)) # L1: Protocol (Cohesion)
    I_paths = np.zeros((num_paths, N_steps)) # L2: Isolation
    N_paths = np.zeros((num_paths, N_steps)) # L3: Narrative Coherence
    S_paths = np.zeros((num_paths, N_steps)) # L4: Institutional (Structural Integrity)
    M_paths = np.zeros((num_paths, N_steps)) # L5: Memory Layer
    
    # Discrete State L7 Phase Layer Buffer [num_paths, N_steps]
    phase_paths = np.zeros((num_paths, N_steps), dtype=int)
    
    # L8 Projection Layer (Y-space) Buffers
    Y_C_paths = np.zeros((num_paths, N_steps))
    Y_I_paths = np.zeros((num_paths, N_steps))
    
    # Initial Conditions (t=0)
    C_paths[:, 0] = 0.8   # High baseline Cohesion
    I_paths[:, 0] = 0.1   # Low baseline Isolation
    N_paths[:, 0] = 0.9   # Strong initial Narrative Coherence
    S_paths[:, 0] = 0.85  # Stable Structural Integrity
    M_paths[:, 0] = 0.9   # Intact Civilizational Memory
    phase_paths[:, 0] = 0 # 0: Stable Phase
    
    # SDE System Parameters (Drift Coefficients)
    epsilon, delta, kappa = 0.04, 0.05, 0.04
    alpha, beta, gamma, xi = 0.04, 0.03, 0.05, 0.03
    phi, psi = 0.04, 0.03
    mu, nu = 0.05, 0.04
    eta, lmbda = 0.03, 0.03
    
    # Volatility Parameters (Diffusion Coefficients σ)
    sigma_C, sigma_I, sigma_N, sigma_S, sigma_M = 0.015, 0.015, 0.020, 0.010, 0.005
    
    np.random.seed(42)
    
    # Dynamic Simulation Loop
    for i in range(1, N_steps):
        ti = t_axis[i-1]
        X = X_t(ti)
        
        # Governance Input Matrix Allocation
        G_kpi = 0.0
        G_rescue = 0.0
        
        # Dynamic Intervention Threshold Trigger (t=40.0)
        if ti >= 40.0:
            if scenario == 'KPI_enforcement':
                G_kpi = 1.0
            elif scenario == 'IPP_rescue':
                G_rescue = 1.0
        
        for p in range(num_paths):
            C = C_paths[p, i-1]
            I = I_paths[p, i-1]
            N = N_paths[p, i-1]
            S = S_paths[p, i-1]
            M = M_paths[p, i-1]
            current_phase = phase_paths[p, i-1]
            
            # Scenario-Dependent Parameter Modulation (Overfitting vs Bootloader Rescue)
            w1 = 0.15 if G_kpi > 0 else 0.0
            w2 = 0.15 if G_kpi > 0 else 0.0
            w3 = 0.20 if G_kpi > 0 else 0.0
            ch = 0.25 if G_rescue > 0 else 0.0
            phi_boot = 0.20 if G_rescue > 0 else 0.0
            
            # 3.1 Multivariate SDE Core Equations (Euler-Maruyama Integration)
            dC_drift = (epsilon * M * C * (1.0 - C) - (delta * I + kappa * X + w1) * C) * dt
            dI_drift = (((alpha * (1.0 - N) + beta * (1.0 - S) + xi * X) * (1.0 - I)) - gamma * C * I) * dt
            dN_drift = (phi * M * N * (1.0 - N) - (psi * I + w2) * N) * dt
            dS_drift = (mu * C * S * (1.0 - S) - (nu * I + w3) * S + ch) * dt
            dM_drift = (-(eta * I + lmbda * X) * M + phi_boot * C * (1.0 - M)) * dt
            
            # Wiener Process Generation
            dW_C = np.random.normal(0, np.sqrt(dt))
            dW_I = np.random.normal(0, np.sqrt(dt))
            dW_N = np.random.normal(0, np.sqrt(dt))
            dW_S = np.random.normal(0, np.sqrt(dt))
            dW_M = np.random.normal(0, np.sqrt(dt))
            
            # Bounded State Extraction [0.0, 1.0]
            C_paths[p, i] = np.clip(C + dC_drift + sigma_C * C * (1.0 - C) * dW_C, 0.0, 1.0)
            I_paths[p, i] = np.clip(I + dI_drift + sigma_I * I * (1.0 - I) * dW_I, 0.0, 1.0)
            N_paths[p, i] = np.clip(N + dN_drift + sigma_N * (1.0 - N) * dW_N, 0.0, 1.0)
            S_paths[p, i] = np.clip(S + dS_drift + sigma_S * dW_S, 0.0, 1.0)
            M_paths[p, i] = np.clip(M + dM_drift + sigma_M * dW_M, 0.0, 1.0)
            
            # 3.2 Non-Homogeneous L7 Markov Transition Engine
            P_base = np.array([
                [0.95, 0.04, 0.01, 0.0,  0.0],   # 0: Stable
                [0.05, 0.80, 0.13, 0.02, 0.0],   # 1: Latent
                [0.0,  0.10, 0.70, 0.18, 0.02],  # 2: Weakening
                [0.0,  0.0,  0.08, 0.72, 0.20],  # 3: Critical
                [0.0,  0.0,  0.0,  0.0,  1.0 ]   # 4: Collapsed (Absorbing State)
            ])
            
            # Dynamic Modulation Matrix Driven by Real Space Vulnerabilities Delta_fail
            Delta_fail = 0.05 * (1.0 - C) + 0.05 * I + 0.05 * (1.0 - M) + 0.05 * X
            
            P = P_base.copy()
            P[0, 1] += Delta_fail + (0.10 * G_kpi)
            P[1, 2] += Delta_fail
            P[2, 3] += Delta_fail
            P[3, 4] += Delta_fail + (0.25 * G_kpi)
            
            if G_rescue > 0:
                P[1, 0] += 0.15
                P[2, 1] += 0.20
                P[3, 2] += 0.25
                P[3, 4] *= 0.10
                P[2, 4] *= 0.10
                
            # Row Normalization (Conservation of Probability Mass)
            P = P / P.sum(axis=1, keepdims=True)
            
            # Execute Non-Absorbed Phase Transitions
            if current_phase != 4:
                phase_paths[p, i] = np.random.choice(5, p=P[current_phase])
            else:
                phase_paths[p, i] = 4
                
            # 4. L8 Projection Layer Matrix Formulation (Non-Injective IPP Mapping)
            Y_C_paths[p, i] = np.clip(C_paths[p, i] + 0.35 * G_kpi, 0.0, 1.0)
            Y_I_paths[p, i] = np.clip(I_paths[p, i] - 0.25 * G_kpi, 0.0, 1.0)
            
    return t_axis, C_paths, M_paths, Y_C_paths, phase_paths

# --- 3. Operational Orchestration & Visualization Setup ---
t_max = 200
num_paths = 100
dt = 0.1

t_axis, C_kpi, M_kpi, Y_C_kpi, phase_kpi = run_civos_v3_core(num_paths, t_max, dt, scenario='KPI_enforcement')
_, C_rsc, M_rsc, Y_C_rsc, phase_rsc = run_civos_v3_core(num_paths, t_max, dt, scenario='IPP_rescue')

# Helper function to compute dynamic state occupancy ratios
def get_occupancy(phase_p, steps):
    occ = np.zeros((5, steps))
    for t in range(steps):
        counts = np.bincount(phase_p[:, t], minlength=5)
        occ[:, t] = counts / num_paths
    return occ

occ_kpi = get_occupancy(phase_kpi, len(t_axis))
occ_rsc = get_occupancy(phase_rsc, len(t_axis))

# Multi-Panel Layout Assembly
fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=True)
states = ['Stable', 'Latent', 'Weakening', 'Critical', 'Collapsed']
colors = ['#22c55e', '#3b82f6', '#eab308', '#f97316', '#ef4444']

# --- Panel A: Scenario A (KPI Enforcement) SDE Micro-Dynamics ---
axes[0, 0].plot(t_axis, np.mean(C_kpi, axis=0), label='Real Cohesion (C)', color='#1A2E44', linewidth=2.5)
axes[0, 0].plot(t_axis, np.mean(Y_C_kpi, axis=0), label='Dashboard Metric (Y_C)', color='green', linestyle='--', linewidth=2.5)
axes[0, 0].plot(t_axis, np.mean(M_kpi, axis=0), label='Civilizational Memory (M)', color='purple', alpha=0.7)
axes[0, 0].axvline(x=40, color='red', linestyle=':')
axes[0, 0].set_title("Scenario A (KPI) - Multivariate SDE & Projection Distortion", fontsize=11, fontweight='bold')
axes[0, 0].set_ylabel("Continuous State Value")
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].legend()

# --- Panel B: Scenario A (KPI Enforcement) L7 Phase Occupancy ---
axes[1, 0].stackplot(t_axis, occ_kpi, labels=states, colors=colors, alpha=0.85)
axes[1, 0].axvline(x=40, color='black', linestyle=':')
axes[1, 0].set_title("Scenario A (KPI) - L7 Phase Occupancy Evolution", fontsize=11, fontweight='bold')
axes[1, 0].set_ylabel("Occupancy Probability")

# --- Panel C: Scenario B (IPP Rescue) SDE Micro-Dynamics ---
axes[0, 1].plot(t_axis, np.mean(C_rsc, axis=0), label='Real Cohesion (C)', color='#1A2E44', linewidth=2.5)
axes[0, 1].plot(t_axis, np.mean(Y_C_rsc, axis=0), label='Dashboard Metric (Y_C)', color='green', linestyle='--', linewidth=2.5)
axes[0, 1].plot(t_axis, np.mean(M_rsc, axis=0), label='Civilizational Memory (M)', color='purple', alpha=0.7)
axes[0, 1].axvline(x=40, color='blue', linestyle=':')
axes[0, 1].set_title("Scenario B (Rescue) - Multivariate SDE & Projection Distortion", fontsize=11, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)

# --- Panel D: Scenario B (IPP Rescue) L7 Phase Occupancy ---
axes[1, 1].stackplot(t_axis, occ_rsc, labels=states, colors=colors, alpha=0.85)
axes[1, 1].axvline(x=40, color='black', linestyle=':')
axes[1, 1].set_title("Scenario B (Rescue) - L7 Phase Occupancy Evolution", fontsize=11, fontweight='bold')

for ax in axes[1]:
    ax.set_xlabel("Continuous Time Steps (dt=0.1)")

plt.tight_layout()
plot_path = os.path.join(output_dir, 'civos_v3.0_hybrid_simulation.png')
plt.savefig(plot_path, dpi=300)
print(f"CivOS v3.0 core execution complete. Hybrid trajectory saved to {plot_path}")
