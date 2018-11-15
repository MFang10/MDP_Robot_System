# MDP_Robot_System
This repository contains the source codes of a robot system running on Raspberry Pi. This system was part of the CZ3004 Multi-Disciplinary Project.

# Objective of this project is to create a autonomous robot that 
1) explores an unknown map without bumping into the walls (with real-time updates on the Android App)
2) plans a fastest path from the Start Zone (bottom left corner) to the Goal Zone (top right corner) while passing through a predefined way point
3) performs image detection on random arrow image pasted on the maze wall and report their locations (with real-time updates on the Android App)

The complete system consists of Arduino control, Raspberry Pi as the communication centre, Algorithm for path planning and localization, and an Android App as the console. This repository covers the Raspberry Pi Communication, Image Detection and Main Algprithm. The main algorithm runs directly on the Raspberry Pi.

# DOCUMENTATION
System for deployment: FinalSystem
Refer to the two PDF files in the repository for detailed explantion for 'FinalSystem'.

# Acknowledgement
Special thanks to Gerald Lim Jun Ji for writing the Arduino communication module in this repository.
