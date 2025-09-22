# TCP-like UDP and Congestion Control

**Course:** COL334 - Computer Networks  
**Authors:**  
- Umesh Kumar (2022CS11115)  
- Aditya Sahu (2022CS11113)  

---

## 📌 Overview

This project explores **reliability mechanisms** implemented over UDP and studies **congestion control** algorithms such as TCP Reno and TCP CUBIC. The assignment is divided into three main parts:

1. **Reliability over UDP**
2. **Congestion Control (TCP Reno-like)**
3. **CUBIC Congestion Control**

Each part includes implementation, performance analysis, and visual results with key observations.

---

## 🔹 Part 1: Reliability

Reliability mechanisms were implemented on top of UDP to ensure dependable file transfers between a server and client.

### Plot 1: Average Time Taken vs Loss Percentage
- **Observation:**  
  - With **Fast Recovery (blue line):** Transfer time increases gradually with packet loss, as prompt retransmissions reduce delays.  
  - Without Fast Recovery (red line): Transfer time increases sharply, relying on timeouts and causing cumulative delays.  
- **Trend:** Fast recovery significantly improves performance at higher loss rates (>2%).

### Plot 2: Average Time Taken vs Link Delay
- **Observation:**  
  - File transfer time increases linearly with network delay.  
  - With Fast Recovery enabled, transfers are consistently faster.  
- **Trend:** Fast recovery remains effective even under high delays.

---

## 🔹 Part 2: Congestion Control (TCP Reno-like)

### Efficiency

#### Plot 1: Throughput vs Packet Loss Percentage
- At **0% loss**, throughput peaks around **6 MBps**.  
- Even slight packet loss (0.5%–1%) causes sharp drops due to Reno’s **AIMD** behavior.  
- Throughput is approximately proportional to **1 / √p**, consistent with the Reno throughput model.

#### Plot 2: Throughput vs Link Delay (at 1% loss)
- At **0 ms delay**, throughput is ~18 MBps.  
- Throughput drops sharply with even small delays (e.g., <3 MBps at 25 ms).  
- At higher delays (>50 ms), throughput stabilizes below 1 MBps.  
- **Trend:** Throughput is inversely proportional to **RTT**.

### Fairness

#### Plot 1: Two Servers with Different Link Delays
- When delays are similar, throughputs are close.  
- As the delay difference increases, the lower-delay server dominates.  
- Despite this, fairness remains reasonable (not fully inverse to delay).

#### Jain’s Fairness Index (JFI) vs Link Delay
- JFI ≈ 1 when delays are equal.  
- JFI decreases with higher delay asymmetry but remains around **0.8** even at 100 ms difference, showing TCP’s inherent fairness mechanisms.

---

## 🔹 Part 3: CUBIC Congestion Control

TCP CUBIC is optimized for high-bandwidth, high-latency networks, using a cubic growth function for aggressive window expansion.

### Efficiency

#### Plot 1: Throughput vs Packet Loss Percentage (20 ms delay)
- CUBIC throughput decreases with packet loss, similar to Reno.  
- Performs **better than Reno at low loss rates**, due to cubic growth.  
- Throughput ∝ **1 / p^0.75**, making it less sensitive to packet loss compared to Reno.

#### Plot 2: Throughput vs Link Delay (0% loss)
- Similar to Reno, but CUBIC achieves **higher throughput** for the same delays.  
- Throughput decreases hyperbolically with delay.  
- More efficient in **high-delay networks** compared to Reno.

### Fairness

#### Plot 1: Instantaneous Throughput at 2 ms Delay
- **Reno (red):** Sawtooth throughput pattern due to AIMD, with sharp drops after losses.  
- **CUBIC (blue):** Smoother growth with fewer drastic drops, leading to more stable throughput.

#### Plot 2: Instantaneous Throughput at 25 ms Delay
- **Reno:** Larger oscillations, poor recovery in high-delay environments.  
- **CUBIC:** Steady cubic growth, better exploitation of bandwidth, and higher sustained throughput.

---

## 📊 Key Takeaways

- **Fast Recovery** significantly improves reliability over UDP, especially under packet loss.  
- **TCP Reno:** Sensitive to packet loss and delay, throughput ∝ 1 / (RTT × √p).  
- **TCP CUBIC:** Outperforms Reno in both low-loss and high-delay environments, with throughput ∝ 1 / p^0.75.  
- **Fairness:** Both Reno and CUBIC maintain reasonable fairness across flows, though Reno suffers more under asymmetric delays.  

---

## 📁 Project Structure

- **Part 1:** Reliability over UDP  
- **Part 2:** TCP Reno-like Congestion Control  
- **Part 3:** TCP CUBIC Congestion Control  
- Includes plots, analysis, and discussion of results.

---

## 🚀 How to Run
1. Compile the source files using the provided Makefile (if included).  
2. Run server and client programs for each part.  
3. Adjust parameters (loss %, delay) to reproduce results.  
4. Generate plots and compare results against provided observations.

---

## 📝 Authors
- **Umesh Kumar** (2022CS11115)  
- **Aditya Sahu** (2022CS11113)  

