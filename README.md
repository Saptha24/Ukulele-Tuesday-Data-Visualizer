# 🎵 Ukulele Tuesday Data Visualizer

An interactive Python desktop application to **analyze and visualize ukulele performance data**.  
Built as part of the *Programming for Analytics* module at **University College Dublin (UCD)**.

---

## 📌 Features

- Upload and merge multiple CSV datasets (`tabdb.csv`, `playdb.csv`, `requestdb.csv`)
- Apply interactive filters:
  - Song, Artist, Type, Gender, Language, Source, Special Books
  - Date range, Duration range, Difficulty level
- Display dynamic visualizations:
  - Histograms (Difficulty, Duration)
  - Bar charts (Language, Source, Decade)
  - Cumulative line charts (Songs played)
  - Pie charts (Songs by gender)
- Export all generated graphs into a single PDF report
- User-friendly **Tkinter GUI** with sidebar and modern layout

---

## ⚙️ Tech Stack

- **Python**
- **Tkinter / tkmacosx** — GUI
- **Pandas** — data cleaning, merging, analysis
- **Matplotlib** — visualizations & PDF export

---

## 🚀 Getting Started

### 1. Install Requirements
Make sure Python 3.7+ is installed, then:
```bash
pip install pandas matplotlib tkmacosx
