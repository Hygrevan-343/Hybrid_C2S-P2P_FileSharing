# 🔄 Hybrid C2S & P2P File Sharing System

A Python-based hybrid networking system that intelligently combines **Client-to-Server (C2S)** and **Peer-to-Peer (P2P)** architectures to improve file sharing scalability, load distribution, and fault tolerance.

---

![System Overview](https://github.com/yourusername/Hybrid_C2S-P2P_FileSharing/assets/yourimageid/hybrid-overview.png)

---

## 🌐 Project Overview

This system is built to simulate a real-world file-sharing architecture:
- Clients **first request files from a central server** (C2S).
- When the server reaches its **maximum connection threshold**, it **redirects clients to CDN (peer cache) servers**.
- Peer servers **cache previously fetched files**, enabling **efficient decentralized sharing**.

This hybrid design reduces server load and enhances the overall robustness and scalability of the network.

---

## ⚙️ Tech Stack

<img src="https://skillicons.dev/icons?i=python,github,vscode" />

- **Language**: Python 3.x  
- **Networking**: TCP using Python's `socket` module  
- **Concurrency**: Python `threading` for handling multiple connections  
- **Architecture**: Hybrid C2S and P2P  
- **File Handling**: Binary transfer with EOF markers

---

## 🗂️ Repository Structure

