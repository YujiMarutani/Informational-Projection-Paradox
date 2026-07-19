import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Page Configuration & Professional Styling ---
st.set_page_config(
    page_title="CivOS v3.0 Survival Engine",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Civilization-OS v3.0: Survival & Hazard Engine")
st.markdown("""
This interactive simulation materializes the **Informational Projection Paradox (IPP)** and 
**CivOS v3.0 macro-dynamics** It bridges continuous multivariate SDE layers with a 5-state 
non-homogeneous Markov Chain to analyze system reliability, survival functions, and instantaneous hazard rates
""")

# --- 2. Sidebar Parameters (Interactive UI Core) ---
st.sidebar.header("🕹️ Simulation Parameters")

# Time-Dependent External Pressure X(t) Controls
st.sidebar.subheader("L6 External Pressure Vector")
k_val = st.sidebar.slider("Erosion Velocity (k)", min_value=0.01, max_value=0.50, value=0.10, step=0.01)
t0_val = st.sidebar.slider("Pressure Inflection Step (t0)", min_value=10.0, max_value=100.0, value=50.0, step=5.0)

# Path Configuration
st.sidebar.subheader("Monte Carlo Configurations")
num_paths = st.sidebar.number_input("Number of Simulated Paths", min_value=100, max_value=5000, value=1000, step=100)
t_max = 150
dt = 0.1
N_steps = int(t_max / dt)

# --- 3. Mathematical Simulation Kernel ---
def X_t(t, k, t0):
    return 1.0 / (1.0 + np.exp(-k * (t - t0)))

@st.cache_data
def run_interactive_core(num_paths, t_max, dt, k, t0, scenario):
    N_steps = int(t_max / dt)
    t_axis = np.linspace(0, t_max, N_steps)
    
    # Pre-allocate State Matrix Arrays
    C_paths = np.zeros((num_paths, N_steps))
    M_paths = np.zeros((num_paths, N_steps))
    phase_paths = np.zeros((num_paths, N_steps), dtype=int)
    Y_C_paths = np.zeros((num_paths, N_steps))
    
    # Initial Baseline Values
    C_paths[:, 0] = 0.8
    M_paths[:, 0] = 0.9
    phase_paths[:, 0] = 0
    
    # Fixed Core Drift Parameters
    epsilon, delta, kappa = 0.04, 0.05, 0.04
    eta, lmbda = 0.03, 0.03
    sigma_C, sigma_M = 0.015, 0.005
    
    np.random.seed(42)
    
    for i in range(1, N_steps):
        ti = t_axis[i-1]
        X = X_t(ti, k, t0)
        
        G_kpi = 1.0 if (scenario == 'KPI_enforcement' and ti >= 40.0) else 0.0
        G_rescue = 1.0 if (scenario == 'IPP_rescue' and ti >= 40.0) else 0.0
        
        w1 = 0.15 * G_kpi
        phi_boot = 0.20 * G_rescue
        
        for p in range(num_paths):
            C = C_paths[p, i-1]
            M = M_paths[p, i-1]
            current_phase = phase_paths[p, i-1]
            
            # SDE Layer Execution
            dC_drift = (epsilon * M * C * (1.0 - C) - (delta * 0.2 + kappa * X + w1) * C) * dt
            dM_drift = (-(eta * 0.2 + lmbda * X) * M + phi_boot * C * (1.0 - M)) * dt
            
            dW_C = np.random.normal(0, np.sqrt(dt))
            dW_M = np.random.normal(0, np.sqrt(dt))
            
            C_paths[p, i] = np.clip(C + dC_drift + sigma_C * C * (1.0 - C) * dW_C, 0.0, 1.0)
            M_paths[p, i] = np.clip(M + dM_drift + sigma_M * dW_M, 0.0, 1.0)
            
            # Non-Homogeneous Markov Matrix Calculation
            P_base = np.array([
                [0.95, 0.04, 0.01, 0.0,  0.0],
                [0.05, 0.80, 0.13, 0.02, 0.0],
                [0.0,  0.10, 0.70, 0.18, 0.02],
                [0.0,  0.0,  0.08, 0.72, 0.20],
                [0.0,  0.0,  0.0,  0.0,  1.0 ]
            ])
            
            Delta_fail = 0.05 * (1.0 - C_paths[p, i]) + 0.05 * (1.0 - M_paths[p, i]) + 0.05 * X
            
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
                
            P = P / P.sum(axis=1, keepdims=True)
            
            if current_phase != 4:
                phase_paths[p, i] = np.random.choice(5, p=P[current_phase])
            else:
                phase_paths[p, i] = 4
                
            # L8 Projection Equation (Dashboard Distortion)
            Y_C_paths[p, i] = np.clip(C_paths[p, i] + 0.35 * G_kpi, 0.0, 1.0)
            
    return t_axis, C_paths, Y_C_paths, phase_paths

# --- 4. Process Simulation & Compute Metrics ---
with st.spinner("Computing 3 distinct scenario matrix paths..."):
    t_axis, C_base, Y_base, ph_base = run_interactive_core(num_paths, t_max, dt, k_val, t0_val, 'none')
    _, C_kpi, Y_kpi, ph_kpi = run_interactive_core(num_paths, t_max, dt, k_val, t0_val, 'KPI_enforcement')
    _, C_rsc, Y_rsc, ph_rsc = run_interactive_core(num_paths, t_max, dt, k_val, t0_val, 'IPP_rescue')

# Compute Survival S(t) and Hazard h(t) Metrics
def compute_reliability(ph_matrix):
    steps = ph_matrix.shape[1]
    S_t = np.zeros(steps)
    for t in range(steps):
        S_t[t] = np.sum(ph_matrix[:, t] != 4) / num_paths
        
    hazard_t = np.zeros(steps)
    for t in range(1, steps):
        if S_t[t-1] > 0:
            hazard_t[t] = (S_t[t-1] - S_t[t]) / S_t[t-1]
    return S_t, hazard_t

S_base, h_base = compute_reliability(ph_base)
S_kpi, h_kpi = compute_reliability(ph_kpi)
S_rsc, h_rsc = compute_reliability(ph_rsc)

# --- 5. UI Layout Tabs (Data Visualizer) ---
tab1, tab2, tab3 = st.tabs(["📊 Survival Analysis Functions", "📈 SDE vs Dashboard Gap", "🗺️ L7 Phase Occupancy Evolution"])

with tab1:
    st.subheader("Reliability Engineering Metrics")
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    
    # Survival Curves Plot
    ax[0].plot(t_axis, S_base, label="Baseline", color="#6B7280")
    ax[0].plot(t_axis, S_kpi, label="Scenario A (KPI Overfitting)", color="#ef4444", linewidth=2)
    ax[0].plot(t_axis, S_rsc, label="Scenario B (IPP Rescue)", color="#3b82f6", linewidth=2)
    ax[0].axvline(x=40, color="black", linestyle=":", alpha=0.5)
    ax[0].set_title("Civilization Survival Function S(t) - Probability of Non-Collapse")
    ax[0].set_ylabel("Probability")
    ax[0].legend()
    ax[0].grid(True, alpha=0.2)
    
    # Hazard Curves Plot
    h_kpi_smooth = np.convolve(h_kpi, np.ones(5)/5, mode='same')
    h_rsc_smooth = np.convolve(h_rsc, np.ones(5)/5, mode='same')
    ax[1].plot(t_axis[2:-2], h_base[2:-2], color="#6B7280")
    ax[1].plot(t_axis[2:-2], h_kpi_smooth[2:-2], color="#ef4444", linewidth=2)
    ax[1].plot(t_axis[2:-2], h_rsc_smooth[2:-2], color="#3b82f6", linewidth=2)
    ax[1].axvline(x=40, color="black", linestyle=":", alpha=0.5)
    ax[1].set_title("Instantaneous Hazard Rate h(t) - Failure Probability Curve")
    ax[1].set_xlabel("Continuous Time Progression")
    ax[1].set_ylabel("Hazard Probability")
    ax[1].grid(True, alpha=0.2)
    
    st.pyplot(fig)

with tab2:
    st.subheader("The IPP Reality Disconnect")
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    
    # Scenario A Paradox
    ax[0].plot(t_axis, np.mean(C_kpi, axis=0), label="Real Cohesion (X-space)", color="#1A2E44")
    ax[0].plot(t_axis, np.mean(Y_kpi, axis=0), label="Metric Dashboard (Y-space)", color="green", linestyle="--")
    ax[0].axvline(x=40, color="red", linestyle=":")
    ax[0].set_title("Scenario A: Optimization Failure")
    ax[0].set_ylabel("State Magnitude")
    ax[0].legend()
    ax[0].grid(True, alpha=0.2)
    
    # Scenario B Paradox
    ax[1].plot(t_axis, np.mean(C_rsc, axis=0), label="Real Cohesion (X-space)", color="#1A2E44")
    ax[1].plot(t_axis, np.mean(Y_rsc, axis=0), label="Metric Dashboard (Y-space)", color="green", linestyle="--")
    ax[1].axvline(x=40, color="blue", linestyle=":")
    ax[1].set_title("Scenario B: Structural Protocol Rescue")
    ax[1].legend()
    ax[1].grid(True, alpha=0.2)
    
    st.pyplot(fig)

with tab3:
    st.subheader("L7 Non-Homogeneous State Markov Ratios")
    col1, col2 = st.columns(2)
    states = ['Stable', 'Latent', 'Weakening', 'Critical', 'Collapsed']
    colors = ['#22c55e', '#3b82f6', '#eab308', '#f97316', '#ef4444']
    
    def calculate_occupancy_matrix(ph_matrix):
        steps = ph_matrix.shape[1]
        occ = np.zeros((5, steps))
        for t in range(steps):
            counts = np.bincount(ph_matrix[:, t], minlength=5)
            occ[:, t] = counts / num_paths
        return occ

    with col1:
        st.markdown("**Scenario A (KPI Enforcement) State Transition Stack**")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.stackplot(t_axis, calculate_occupancy_matrix(ph_kpi), labels=states, colors=colors, alpha=0.85)
        ax1.axvline(x=40, color="black", linestyle=":")
        ax1.set_ylabel("Occupancy Probability")
        st.pyplot(fig1)
        
    with col2:
        st.markdown("**Scenario B (IPP Rescue) State Transition Stack**")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.stackplot(t_axis, calculate_occupancy_matrix(ph_rsc), labels=states, colors=colors, alpha=0.85)
        ax2.axvline(x=40, color="black", linestyle=":")
        st.pyplot(fig2)
