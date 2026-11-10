// Preset test samples
const SAMPLES = {
    real_science: {
        title: "NASA James Webb Space Telescope Observes Atmospheric Details of Exoplanet",
        text: "Astronomers utilizing the James Webb Space Telescope have characterized the chemical composition of a distant exoplanet atmosphere. The spectral data revealed clear signatures of water vapor, sulfur dioxide, and carbon dioxide. Peer-reviewed findings published in Nature confirm theoretical models of planetary formation.",
        category: "Science"
    },
    fake_health: {
        title: "SHOCKING: Secret Miracle Plant Discovered in Himalayas Completely Cures All Cancers in 24 Hours!",
        text: "Big Pharma is desperately trying to hide this unbelievable miracle root! Scientists confirmed that drinking boiling lemon water with crushed Himalayan pine needles eliminates 100% of malignant cancer cells overnight! Doctors are panicking because this 1 dollar secret destroys their billion-dollar hospital profits. Share before this video is deleted!",
        category: "Health"
    },
    fake_finance: {
        title: "URGENT: World Bank Secretly Cancels All Cash Money Globally Effective Tomorrow Morning!",
        text: "Breaking exclusive report: Global banking elites held an emergency midnight summit and decided all paper currency and bank ATMs will be frozen at sunrise. Every citizen will have their savings confiscated into biometric microchip credits. Mainstream media won't tell you this, rush to the bank right now and withdraw everything!",
        category: "Business"
    },
    regional_hindi: {
        title: "सनसनीखेज: हिमालय में मिली चमत्कारी जड़ी-बूटी से कैंसर की रोकथाम का दावा",
        text: "सोशल मीडिया पर वायरल संदेश में दावा किया गया है कि उबले हुए नींबू और हिमालयन देवदार के अर्क से बना चमत्कारी मिश्रण घातक कैंसर कोशिकाओं को तुरंत नष्ट कर देता है। वैज्ञानिक और मंत्रालय इस अपुष्ट दावे की जांच कर रहे हैं।",
        category: "Health"
    }
};

let currentMode = 'text';

function switchInputMode(mode) {
    currentMode = mode;
    const tabText = document.getElementById('tab-btn-text');
    const tabUrl = document.getElementById('tab-btn-url');
    const paneText = document.getElementById('text-pane');
    const paneUrl = document.getElementById('url-pane');
    
    if (mode === 'url') {
        tabUrl.classList.add('active');
        tabText.classList.remove('active');
        paneUrl.classList.remove('hidden');
        paneText.classList.add('hidden');
    } else {
        tabText.classList.add('active');
        tabUrl.classList.remove('active');
        paneText.classList.remove('hidden');
        paneUrl.classList.add('hidden');
    }
}

function loadSample(key) {
    const s = SAMPLES[key];
    if (!s) return;
    switchInputMode('text');
    document.getElementById('news-title').value = s.title;
    document.getElementById('news-text').value = s.text;
    document.getElementById('news-category').value = s.category;
    document.getElementById('char-count').innerText = `${s.text.length} characters (min. 15 required)`;
    showToast(`Loaded sample: ${s.title.substring(0, 40)}...`, "info");
}

function resetForm() {
    document.getElementById('news-title').value = '';
    document.getElementById('news-text').value = '';
    document.getElementById('news-url').value = '';
    document.getElementById('char-count').innerText = '0 characters (min. 15 required)';
    document.getElementById('results-section').classList.add('hidden');
}

function switchDetailTab(tabId) {
    const tabs = document.querySelectorAll('.detail-tab');
    tabs.forEach(t => t.classList.remove('active'));
    
    const panes = document.querySelectorAll('.detail-pane');
    panes.forEach(p => p.classList.add('hidden'));
    
    const targetPane = document.getElementById(`pane-${tabId}`);
    if (targetPane) targetPane.classList.remove('hidden');
    
    // Highlight clicked tab
    event.currentTarget.classList.add('active');
}

async function submitAnalysis(e) {
    e.preventDefault();
    const btn = document.getElementById('btn-submit');
    const btnText = document.getElementById('btn-submit-text');
    const spinner = document.getElementById('btn-submit-spinner');
    
    const payload = {
        mode: currentMode,
        title: document.getElementById('news-title').value,
        text: document.getElementById('news-text').value,
        url: document.getElementById('news-url').value,
        category: document.getElementById('news-category').value
    };
    
    if (currentMode === 'text' && payload.text.trim().length < 15) {
        showToast("Please enter at least 15 characters of news text.", "warning");
        return;
    }
    if (currentMode === 'url' && !payload.url.trim()) {
        showToast("Please provide a valid article URL.", "warning");
        return;
    }
    
    btnText.classList.add('hidden');
    spinner.classList.remove('hidden');
    btn.disabled = true;
    
    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        
        if (!json.success) {
            showToast(json.error || "Analysis failed.", "error");
            return;
        }
        
        renderResults(json.data);
        showToast("Deep verification completed successfully!", "success");
    } catch (err) {
        showToast("Error executing analysis: " + err.message, "error");
    } finally {
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
        btn.disabled = false;
    }
}

function renderResults(data) {
    const resultsSec = document.getElementById('results-section');
    resultsSec.classList.remove('hidden');
    resultsSec.scrollIntoView({ behavior: 'smooth' });
    
    // 1. Title & Chips
    document.getElementById('result-title').innerText = data.title;
    document.getElementById('chip-domain').innerHTML = `<i class="fa-solid fa-globe"></i> ${data.domain}`;
    document.getElementById('chip-category').innerHTML = `<i class="fa-solid fa-tag"></i> ${data.category}`;
    document.getElementById('chip-lang').innerHTML = `<i class="fa-solid fa-language"></i> ${data.language.name || 'English'}`;
    
    // 2. Score Circle & Verdict Pill
    const scoreVal = data.credibility_score;
    document.getElementById('score-value').innerText = Math.round(scoreVal);
    
    const circle = document.getElementById('score-circle');
    const pill = document.getElementById('verdict-pill');
    pill.innerText = data.final_verdict;
    
    let ringColor = '#10b981'; // Green
    if (data.final_verdict.includes('Fake')) {
        ringColor = '#f43f5e'; // Red
        pill.className = 'verdict-pill badge-fake';
    } else if (data.final_verdict.includes('Genuine')) {
        ringColor = '#10b981';
        pill.className = 'verdict-pill badge-genuine';
    } else {
        ringColor = '#f59e0b'; // Amber
        pill.className = 'verdict-pill badge-inconclusive';
    }
    circle.style.background = `conic-gradient(${ringColor} 0% ${scoreVal}%, #1e293b ${scoreVal}% 100%)`;
    circle.style.boxShadow = `0 0 25px ${ringColor}40`;
    
    // 3. PDF Button
    const pdfBtn = document.getElementById('btn-download-pdf');
    if (data.report_url) {
        pdfBtn.href = data.report_url;
        pdfBtn.style.display = 'inline-flex';
    } else {
        pdfBtn.style.display = 'none';
    }
    
    // 4. KPI Highlights
    const ml = data.ml_prediction;
    const dl = data.deep_learning_prediction;
    const src = data.source_data;
    const cb = data.sentiment_data.clickbait;
    
    document.getElementById('kpi-ml').innerText = `${ml.confidence_score}%`;
    document.getElementById('kpi-ml-sub').innerText = `Ensemble: ${ml.verdict}`;
    document.getElementById('kpi-dl').innerText = `${dl.confidence_score}%`;
    document.getElementById('kpi-dl-sub').innerText = `Context: ${dl.prediction}`;
    document.getElementById('kpi-source').innerText = `${src.credibility_score} / 100`;
    document.getElementById('kpi-source-sub').innerText = src.status;
    document.getElementById('kpi-clickbait').innerText = `${cb.clickbait_score} / 100`;
    document.getElementById('kpi-clickbait-sub').innerText = cb.rating;
    
    // 5. XAI Highlights Rendering
    const xai = data.xai_highlights;
    document.getElementById('xai-rendered-content').innerHTML = xai.rendered_html || data.content_snippet;
    document.getElementById('xai-disclaimer').innerText = xai.disclaimer || '';
    
    const topWordsBox = document.getElementById('top-words-list');
    topWordsBox.innerHTML = '';
    (xai.top_influential_terms || []).forEach(item => {
        const span = document.createElement('span');
        const isGen = item.direction === 'Genuine';
        span.className = `word-pill ${isGen ? 'pill-genuine' : 'pill-fake'}`;
        span.innerHTML = `${item.word} <code>(${item.weight > 0 ? '+' : ''}${item.weight})</code>`;
        topWordsBox.appendChild(span);
    });
    
    // 6. Multi-Model Bars
    const lr = ml.models.logistic_regression;
    const nb = ml.models.naive_bayes;
    const rf = ml.models.random_forest;
    
    document.getElementById('badge-lr').innerText = lr.prediction;
    document.getElementById('badge-lr').className = `model-badge ${lr.prediction === 'Genuine' ? 'badge-genuine' : 'badge-fake'}`;
    document.getElementById('lr-real-val').innerText = `${lr.real_confidence}%`;
    document.getElementById('lr-fake-val').innerText = `${lr.fake_confidence}%`;
    document.getElementById('lr-real-bar').style.width = `${lr.real_confidence}%`;
    document.getElementById('lr-fake-bar').style.width = `${lr.fake_confidence}%`;
    
    document.getElementById('badge-nb').innerText = nb.prediction;
    document.getElementById('badge-nb').className = `model-badge ${nb.prediction === 'Genuine' ? 'badge-genuine' : 'badge-fake'}`;
    document.getElementById('nb-real-val').innerText = `${nb.real_confidence}%`;
    document.getElementById('nb-fake-val').innerText = `${nb.fake_confidence}%`;
    document.getElementById('nb-real-bar').style.width = `${nb.real_confidence}%`;
    document.getElementById('nb-fake-bar').style.width = `${nb.fake_confidence}%`;
    
    document.getElementById('badge-rf').innerText = rf.prediction;
    document.getElementById('badge-rf').className = `model-badge ${rf.prediction === 'Genuine' ? 'badge-genuine' : 'badge-fake'}`;
    document.getElementById('rf-real-val').innerText = `${rf.real_confidence}%`;
    document.getElementById('rf-fake-val').innerText = `${rf.fake_confidence}%`;
    document.getElementById('rf-real-bar').style.width = `${rf.real_confidence}%`;
    document.getElementById('rf-fake-bar').style.width = `${rf.fake_confidence}%`;
    
    document.getElementById('badge-dl').innerText = dl.prediction;
    document.getElementById('badge-dl').className = `model-badge ${dl.prediction === 'Likely Genuine' ? 'badge-genuine' : 'badge-fake'}`;
    document.getElementById('dl-real-val').innerText = `${dl.real_probability}%`;
    document.getElementById('dl-fake-val').innerText = `${dl.fake_probability}%`;
    document.getElementById('dl-real-bar').style.width = `${dl.real_probability}%`;
    document.getElementById('dl-fake-bar').style.width = `${dl.fake_probability}%`;
    
    // 7. Fact Verification Claims & Evidence
    const fact = data.evidence_data;
    const claimsList = document.getElementById('claims-list');
    claimsList.innerHTML = '';
    (fact.extracted_claims || []).forEach(c => {
        const li = document.createElement('li');
        li.innerText = c;
        claimsList.appendChild(li);
    });
    
    const suppList = document.getElementById('supporting-evidence-list');
    suppList.innerHTML = '';
    if ((fact.supporting_evidence || []).length === 0) {
        suppList.innerHTML = '<p class="text-dim">No supporting entries indexed in fact registry.</p>';
    } else {
        fact.supporting_evidence.forEach(e => {
            suppList.innerHTML += `
                <div class="evidence-item">
                    <div class="evidence-source">${e.source}</div>
                    <span class="evidence-verdict badge-genuine">${e.verdict}</span>
                    <p class="evidence-summary">${e.summary}</p>
                    <a href="${e.url}" target="_blank" class="evidence-link"><i class="fa-solid fa-arrow-up-right-from-square"></i> Verified Reference Link</a>
                </div>
            `;
        });
    }
    
    const contraList = document.getElementById('contradicting-evidence-list');
    contraList.innerHTML = '';
    if ((fact.contradicting_evidence || []).length === 0) {
        contraList.innerHTML = '<p class="text-dim">No contradicting debunks identified for this claim.</p>';
    } else {
        fact.contradicting_evidence.forEach(e => {
            contraList.innerHTML += `
                <div class="evidence-item">
                    <div class="evidence-source">${e.source}</div>
                    <span class="evidence-verdict badge-fake">${e.verdict}</span>
                    <p class="evidence-summary">${e.summary}</p>
                    <a href="${e.url}" target="_blank" class="evidence-link"><i class="fa-solid fa-arrow-up-right-from-square"></i> Fact-Checker Source Link</a>
                </div>
            `;
        });
    }
    
    // 8. Source Credibility Tab
    document.getElementById('source-domain-name').innerText = `Domain: ${src.domain || 'Direct Text'}`;
    document.getElementById('source-status-pill').innerText = src.status;
    document.getElementById('source-score-num').innerText = `${src.credibility_score} / 100`;
    document.getElementById('source-description').innerText = src.details;
    
    const badgesBox = document.getElementById('source-badges');
    badgesBox.innerHTML = '';
    (src.badges || []).forEach(b => {
        badgesBox.innerHTML += `<span class="chip"><i class="fa-solid fa-shield-check"></i> ${b}</span>`;
    });
    
    // 9. Sentiment & Clickbait
    const sent = data.sentiment_data.sentiment;
    document.getElementById('sent-label').innerText = sent.sentiment_label;
    document.getElementById('sent-polarity').innerText = sent.polarity;
    document.getElementById('sent-subjectivity').innerText = sent.subjectivity;
    document.getElementById('emotion-dominant').innerText = sent.dominant_emotion;
    
    const emotionBox = document.getElementById('emotion-breakdown');
    emotionBox.innerHTML = '';
    for (const [em, pct] of Object.entries(sent.emotion_distribution || {})) {
        emotionBox.innerHTML += `
            <div class="prob-row"><span>${em.toUpperCase()}:</span><span>${pct}%</span></div>
            <div class="progress-bar"><div class="progress-fill fill-green" style="width: ${pct}%; background: #a855f7;"></div></div>
        `;
    }
    
    document.getElementById('cb-rating').innerText = cb.rating;
    document.getElementById('cb-score').innerText = cb.clickbait_score;
    const trigs = document.getElementById('cb-triggers-box');
    trigs.innerHTML = '';
    (cb.trigger_phrases_detected || []).forEach(tp => {
        trigs.innerHTML += `<span class="chip text-rose"><i class="fa-solid fa-fire"></i> "${tp}"</span>`;
    });
}
