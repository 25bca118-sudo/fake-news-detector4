import os
import sys
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from truthlens_ai.config import (
    SECRET_KEY, DATABASE_PATH, UPLOAD_DIR, REPORTS_DIR, WEIGHTS, THRESHOLDS
)
from truthlens_ai.database.db_manager import init_db
from truthlens_ai.modules import (
    security, auth, ingestion, nlp_processor, ml_detector, deep_learning,
    explainable_ai, source_credibility, fact_verification, image_forensics,
    sentiment_clickbait, multilingual, analytics, history, report_generator
)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['REPORTS_FOLDER'] = str(REPORTS_DIR)
# Initialize DB on boot
init_db()

# --- WEB PAGE ROUTES ---
@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

@app.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html', user=session.get('user'))

@app.route('/image-verify')
def image_verify_view():
    return render_template('image_verify.html', user=session.get('user'))

@app.route('/history')
def history_view():
    return render_template('history.html', user=session.get('user'))

@app.route('/login')
def login_view():
    return render_template('login.html', user=session.get('user'))

# --- AUTH API ENDPOINTS ---
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    success, msg, user_id = auth.register_user(username, email, password)
    if not success:
        return jsonify({'success': False, 'message': msg}), 400
        
    session['user'] = {'id': user_id, 'username': username, 'email': email}
    return jsonify({'success': True, 'message': msg, 'user': session['user']})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    identifier = data.get('username_or_email', '')
    password = data.get('password', '')
    
    success, msg, user_data = auth.authenticate_user(identifier, password)
    if not success:
        return jsonify({'success': False, 'message': msg}), 401
        
    session['user'] = user_data
    return jsonify({'success': True, 'message': msg, 'user': user_data})

@app.route('/api/auth/logout', methods=['POST', 'GET'])
def api_logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/api/auth/me')
def api_me():
    return jsonify({'user': session.get('user')})

# --- ANALYSIS API (MODULES 2 to 11, 14, 15) ---
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json() or {}
    input_mode = data.get('mode', 'text') # 'text' or 'url'
    raw_text = data.get('text', '').strip()
    title = data.get('title', '').strip()
    url = data.get('url', '').strip()
    category = data.get('category', 'General')
    
    origin_domain = ""
    author = ""
    pub_date = ""
    
    # 1. URL Extraction if mode is URL
    if input_mode == 'url':
        if not url:
            return jsonify({'success': False, 'error': 'Please provide a valid news URL.'}), 400
            
        ext_res = ingestion.extract_article_from_url(url)
        if not ext_res['success']:
            return jsonify({'success': False, 'error': ext_res['error']}), 400
            
        art = ext_res['data']
        raw_text = art['content']
        title = art['title']
        origin_domain = art['domain']
        author = art['author']
        pub_date = art['publication_date']
    else:
        # Direct text input validation
        valid, msg = security.validate_input_length(raw_text, min_chars=15)
        if not valid:
            return jsonify({'success': False, 'error': msg}), 400
        if not title:
            first_line = raw_text.split('.')[0]
            title = first_line[:80] + ("..." if len(first_line) > 80 else "")
            
    # 2. Multilingual Processing (Module 11)
    multi_res = multilingual.process_multilingual_text(raw_text)
    processed_text = multi_res['processed_text']
    lang_info = multi_res['language']
    
    # 3. NLP Feature Extraction (Module 3)
    linguistic_feats = nlp_processor.analyze_linguistic_features(raw_text)
    entities = nlp_processor.extract_named_entities(raw_text)
    
    # 4. Traditional ML Classification (Module 4)
    ml_res = ml_detector.predict_ml(processed_text)
    
    # 5. Deep Learning Contextual DistilBERT (Module 5)
    dl_res = deep_learning.predict_deep_learning(processed_text)
    
    # 6. Explainable AI Feature Attribution (Module 6)
    xai_res = explainable_ai.explain_prediction(raw_text[:2000])
    
    # 7. Source Credibility Assessment (Module 7)
    source_res = source_credibility.analyze_source(origin_domain or url, author=author)
    
    # 8. Fact-Checking Evidence Matching (Module 8)
    fact_res = fact_verification.verify_claims(raw_text)
    
    # 9. Sentiment & Clickbait Detection (Module 10)
    sentiment_res = sentiment_clickbait.analyze_sentiment_and_emotion(raw_text)
    clickbait_res = sentiment_clickbait.detect_clickbait(f"{title} {raw_text[:300]}")
    
    # 10. Compound Credibility Score Calculation (0-100)
    ml_score = ml_res['real_probability'] # 0 to 100
    dl_score = dl_res['real_probability'] # 0 to 100
    src_score = source_res['credibility_score'] # 0 to 100
    fact_score = fact_res['verification_score'] # 0 to 100
    cb_penalty = clickbait_res['clickbait_score'] * 0.10 # up to 10 pt deduction
    
    # Adaptive weighting depending on origin URL presence
    if input_mode == 'url' and origin_domain:
        raw_compound_score = (
            (ml_score * 0.35) +
            (dl_score * 0.25) +
            (src_score * 0.20) +
            (fact_score * 0.20) -
            cb_penalty
        )
    else:
        # Direct submission re-balances across model & fact evidence
        raw_compound_score = (
            (ml_score * 0.45) +
            (dl_score * 0.35) +
            (fact_score * 0.20) -
            cb_penalty
        )
        
    compound_score = round(max(5.0, min(99.0, raw_compound_score)), 1)
    
    # Determine Final Verdict
    if compound_score >= 60.0:
        final_verdict = "Likely Genuine"
        verdict_badge = "badge-genuine"
    elif compound_score <= 40.0:
        final_verdict = "Potentially Fake"
        verdict_badge = "badge-fake"
    else:
        final_verdict = "Inconclusive / Mixed Evidence"
        verdict_badge = "badge-inconclusive"
        
    analysis_payload = {
        'title': title,
        'domain': origin_domain or "Direct Submission",
        'author': author or "Unspecified",
        'publication_date': pub_date or "N/A",
        'category': category,
        'language': lang_info,
        'final_verdict': final_verdict,
        'verdict_badge': verdict_badge,
        'credibility_score': compound_score,
        'ml_prediction': ml_res,
        'deep_learning_prediction': dl_res,
        'xai_highlights': xai_res,
        'source_data': source_res,
        'evidence_data': fact_res,
        'sentiment_data': {
            'sentiment': sentiment_res,
            'clickbait': clickbait_res
        },
        'linguistic_features': linguistic_feats,
        'named_entities': entities,
        'content_snippet': raw_text[:400]
    }
    
    # 11. Generate PDF Report (Module 14)
    try:
        report_file = report_generator.generate_pdf_report(analysis_payload)
        analysis_payload['report_filename'] = report_file
        analysis_payload['report_url'] = f"/reports/{report_file}"
    except Exception as e:
        analysis_payload['report_filename'] = None
        analysis_payload['report_error'] = str(e)
        
    # 12. Persist to Database (Module 13)
    user_id = session.get('user', {}).get('id') if session.get('user') else None
    analysis_payload['user_id'] = user_id
    record_id = history.save_analysis_record(analysis_payload)
    analysis_payload['analysis_id'] = record_id
    
    return jsonify({
        'success': True,
        'data': analysis_payload
    })

# --- IMAGE FORENSICS API (MODULE 9) ---
@app.route('/api/image-verify', methods=['POST'])
def api_image_verify():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file uploaded.'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Selected file is empty.'}), 400
        
    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({'success': False, 'error': 'Invalid filename.'}), 400
    # Avoid overwriting an earlier upload with the same name.
    stem, suffix = os.path.splitext(filename)
    filename = f"{stem}_{os.urandom(6).hex()}{suffix.lower()}"
    save_path = UPLOAD_DIR / filename
    file.save(str(save_path))
    
    # 1. EXIF Metadata
    exif = image_forensics.extract_image_exif(save_path)
    
    # 2. Error Level Analysis (ELA)
    ela_filename, manip_score, is_tampered = image_forensics.perform_error_level_analysis(save_path)
    
    # 3. Reverse search links
    reverse_links = image_forensics.generate_reverse_search_links(query_terms=Path(filename).stem)
    
    return jsonify({
        'success': True,
        'data': {
            'original_image': f"/uploads/{filename}",
            'ela_image': f"/uploads/{ela_filename}",
            'manipulation_score': manip_score,
            'is_tampered': is_tampered,
            'tampering_verdict': "High Tampering Probability" if is_tampered else "Authentic / Unmodified",
            'exif_metadata': exif,
            'reverse_search': reverse_links
        }
    })

# --- DASHBOARD & HISTORY APIS (MODULES 12, 13) ---
@app.route('/api/analytics')
def api_analytics():
    summary = analytics.get_dashboard_summary()
    return jsonify({'success': True, 'data': summary})

@app.route('/api/history')
def api_history():
    search = request.args.get('search', '')
    verdict = request.args.get('verdict', 'all')
    user_id = session.get('user', {}).get('id') if session.get('user') else None
    items = history.get_user_history(user_id=user_id, search=search, verdict_filter=verdict)
    return jsonify({'success': True, 'data': items})

@app.route('/api/history/<int:record_id>', methods=['GET', 'DELETE'])
def api_history_item(record_id):
    user_id = session.get('user', {}).get('id') if session.get('user') else None
    if request.method == 'DELETE':
        history.delete_analysis_record(record_id, user_id=user_id)
        return jsonify({'success': True, 'message': 'Record deleted successfully.'})
    else:
        record = history.get_analysis_details(record_id)
        if not record:
            return jsonify({'success': False, 'error': 'Record not found.'}), 404
        return jsonify({'success': True, 'data': record})

# --- FILE SERVING ENDPOINTS ---
@app.route('/reports/<filename>')
def serve_report(filename):
    return send_from_directory(app.config['REPORTS_FOLDER'], filename, as_attachment=False)

@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("TruthLens AI server starting on http://127.0.0.1:5000 ...")
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', '5000')),
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )
