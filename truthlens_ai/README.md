# TruthLens AI — AI-Powered Fake News Detection & Verification System

TruthLens AI is an enterprise-grade, multi-modal Artificial Intelligence system developed to detect, explain, and combat digital misinformation, fake news, and manipulated media. Moving far beyond traditional binary classifiers, TruthLens AI incorporates machine learning ensembles, contextual deep learning representations, explainable AI (XAI), real-time claim verification against global fact-checker registries, domain credibility scoring, and forensic image analysis.

---

## 🌟 Key Modules & System Architecture

| Module # | Module Name | Core Functionality |
| :--- | :--- | :--- |
| **1** | **User Management** | User registration, login, secure PBKDF2-HMAC password hashing, session tokens. |
| **2** | **News Ingestion** | Full article text, headlines, and automated URL scraping with SSRF guardrails. |
| **3** | **NLP Processing** | Text cleaning, tokenization, stopword removal, entity recognition (NER), and TF-IDF. |
| **4** | **ML Detection** | Multi-model ensemble: Logistic Regression, Multinomial Naive Bayes, Random Forest. |
| **5** | **Deep Learning** | Contextual semantic projections & DistilBERT attention representations. |
| **6** | **Explainable AI (XAI)** | Transparent word-level feature attribution with inline red/green influence highlights. |
| **7** | **Source Credibility** | Publisher reputation index (0-100), TLD trust scrutiny, and fact-checking registry audit. |
| **8** | **Fact Verification** | Extraction of core verifiable claims matched against IFCN-certified repositories. |
| **9** | **Image Forensics** | EXIF metadata extraction and Error Level Analysis (ELA) pixel tampering heatmaps. |
| **10** | **Stylometry & Clickbait** | Sentiment polarity (-1 to +1), 5-factor emotion detection, and sensationalism hype index. |
| **11** | **Multilingual Support** | Regional language detection and cross-lingual translation pipeline (Hindi, Kannada). |
| **12** | **Analytics Dashboard** | Global KPI metrics, category breakdowns, and empirical model benchmark comparisons. |
| **13** | **History Management** | SQLite persistent audit trail, keyword search, verdict filtering, and record management. |
| **14** | **Report Generation** | Automated, publication-ready PDF verification reports built with ReportLab. |
| **15** | **Security Guardrails** | SSRF mitigation, internal loopback IP blocking, and XSS sanitization. |

---

## 🚀 Quick Start Guide

### 1. Requirements
Ensure Python 3.10+ (or Python 3.14) is installed. Required libraries include:
- `flask`
- `scikit-learn`
- `scipy`
- `reportlab`
- `pillow`
- `beautifulsoup4`
- `requests`

### 2. Launch the Application
Run via command line or double click `run.bat`:
```bash
python truthlens_ai/run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔬 Scientific Methodology & Compound Credibility Score (0–100)

TruthLens AI calculates an objective **Compound Credibility Index** using weighted contributions:
$$\text{Score} = (W_{ml} \times P_{ml}) + (W_{dl} \times P_{dl}) + (W_{src} \times S_{src}) + (W_{fact} \times V_{fact}) - \text{Penalty}_{clickbait}$$

- **ML Ensemble ($W_{ml} = 0.35$)**: Weighted prediction of Logistic Regression, Naive Bayes, and Random Forest.
- **Deep Learning ($W_{dl} = 0.25$)**: Contextual DistilBERT semantic representation confidence.
- **Source Reputation ($W_{src} = 0.20$)**: Domain governance, author byline, and institutional TLD trust.
- **Fact Verification ($W_{fact} = 0.15$)**: Official corroboration or contradiction from fact-checking registries.
- **Clickbait Penalty**: Up to 15-point deduction for sensational capitalization, exclamation spikes, and viral hype patterns.

### Verdict Classifications:
- **70.0 – 100.0**: `Likely Genuine` (Green)
- **45.0 – 69.9**: `Inconclusive / Mixed Evidence` (Amber)
- **0.0 – 44.9**: `Potentially Fake / Misleading` (Red)

---

## 🎓 College Presentation Talking Points

1. **Why not just binary classification?**
   Binary classifiers lack explainability and miss external context. An article may use professional vocabulary but state completely fabricated scientific falsehoods. TruthLens AI solves this by cross-referencing external evidence.
2. **Explainable AI (XAI)**:
   Users can see exactly which words contributed toward the decision, demystifying the "black-box" model.
3. **Forensic Image Verification (ELA)**:
   Detects digitally altered or spliced news photographs using JPEG Error Level Analysis.
4. **Security & SSRF Mitigation**:
   URL analysis strictly verifies destination IP addresses against RFC 1918 and loopback networks to prevent Server-Side Request Forgery attacks.
