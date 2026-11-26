# ABR Algorithms & QoE Model

1. **Throughput-Based**: Uses the harmonic mean of the last 5 segment throughputs with a `0.85` safety margin.
2. **Buffer-Based (BBA-0)**: Maps buffer occupancy linearly between reservoir ($6\text{s}$) and cushion ($20\text{s}$) to the bitrate ladder.
3. **BOLA-Inspired**: Maximizes $(V(u_m + \gamma) - B) / R_m$ using logarithmic utility $u_m = \ln(R_m / R_{\min})$.
4. **Hybrid MPC**: Balances logarithmic/linear bitrate utility against bandwidth-headroom stall penalties and bitrate-switch smoothness penalties.

**Composite QoE**:
$$\text{QoE} = \frac{\bar{R}}{1000} - 4.3 \cdot \frac{T_{\text{stall}}}{N} - 0.5 \cdot \frac{\overline{|\Delta R|}}{1000}$$
