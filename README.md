# Smart Traffic Light Controller

A real-time intelligent traffic management system to dynamically control traffic lights based on vehicle density.

---

# Overview

Traditional traffic signals function on fixed timers and lack responsiveness to real-time traffic flow, resulting in frequent congestion, wasted fuel and time, inefficient road usage, and increased commuter frustration. This project aims to tackle these challenges by dynamically adjusting signal timings based on real-time traffic density.

Using computer vision techniques, the system detects and classifies vehicles at intersections, allowing for intelligent signal control that adapts to current traffic conditions. By simulating realistic traffic flow with AI-driven decision-making, the system offers a smarter, more efficient approach to urban mobility.

---

# Flowchart
![image](https://github.com/user-attachments/assets/5fda893b-61cf-49b3-9b99-54b5ab9907be)


---

# Methodology

## 1) Vehicle Detection Module

The system uses **YOLOv8**, a state-of-the-art object detection model, to detect and classify vehicles in real-time from CCTV footage. The detection pipeline is integrated with **OpenCV** to process the frames, identify vehicles, and generate bounding boxes with confidence scores. This enables accurate vehicle counting and classification directly from the live feed.

### Traffic Vehicle Movement from live feed
![image](https://github.com/user-attachments/assets/d3e98b2f-3665-4a21-8748-a0438d80707f)
### Detection of Vehicle using OpenCV and YOLO v8
![image](https://github.com/user-attachments/assets/ae22e527-3124-4336-beb7-a818b54127ea)

---

## 2) Signal Switching Algorithm

This algorithm determines which traffic light should be green based on the number and types of vehicles waiting at each lane. The switching follows a cyclic order—**Red → Green → Yellow → Red**—while dynamically adjusting the green time based on traffic density. The system uses **multithreading**, where one thread handles vehicle detection and another manages the signal transitions, ensuring real-time responsiveness and coordinated control.

---

## 3) Calculation of Green Signal Time

The duration for which a green signal stays active is computed using a formula that considers:
- Vehicle count per class
- Estimated time per vehicle type to cross
- Number of lanes

This approach ensures traffic density is handled fairly and efficiently. Lag due to start-up time and the average speed of different vehicle types is also factored in to better model real-world behavior.

---

## 4) Simulation Module

A custom simulation is built using **PyGame** to visualize the intelligent traffic control system. It replicates a 4-way intersection where various vehicle types enter from different directions. Each signal displays a countdown timer, and vehicles move according to signal logic and randomized turning behavior. This simulation demonstrates how dynamic traffic control significantly improves vehicle throughput and reduces congestion.

---

# Demo
![image](https://github.com/user-attachments/assets/161d22f1-621e-4fbd-bab6-878f2e24d1e9)

---

# References

1. M. M. Gandhi, D. S. Solanki, R. S. Daptardar and N. S. Baloorkar, "Smart Control of Traffic Light Using Artificial Intelligence," 2020 5th IEEE International Conference on Recent Advances and Innovations in Engineering (ICRAIE), Jaipur, India, 2020, pp. 1-6, doi: 10.1109/ICRAIE51050.2020.9358334. https://ieeexplore.ieee.org/document/9358334
2. P. Shanmugapriya, K. H. Sankar and K. Mallikarjuna, "Smart Control of Traffic Light Using Artificial Intelligence," Dept. of Computer Science and Engineering, SCSVMV, Kanchipuram, India. https://www.irjet.net/archives/V9/i3/IRJET-V9I3117.pdf
3. A. K. M et al., "Computer Vision Assisted Artificial Intelligence Enabled Smart Traffic Control System for Urban Transportation Management," 2023 Annual International Conference on Emerging Research Areas: International Conference on Intelligent Systems (AICERA/ICIS), Kanjirapally, India, 2023, pp. 1-5, doi: 10.1109/AICERA/ICIS59538.2023.10420126. https://ieeexplore.ieee.org/document/10420126

---

