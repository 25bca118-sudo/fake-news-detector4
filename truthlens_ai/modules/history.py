import json
from truthlens_ai.database.db_manager import execute_insert, execute_query, execute_scalar, execute_update

def save_analysis_record(data: dict) -> int:
    """Persists a complete multi-module analysis record into database."""
    query = """
    INSERT INTO analyses (
        user_id, title, url, content_snippet, language, category, final_verdict,
        credibility_score, ml_confidence, ml_prediction, deep_learning_score,
        deep_learning_prediction, sentiment_data, source_data, evidence_data,
        xai_highlights, report_filename
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    lang_val = data.get('language')
    if isinstance(lang_val, dict):
        lang_str = lang_val.get('name', 'English')
    else:
        lang_str = str(lang_val or 'English')

    params = (
        data.get('user_id'),
        data.get('title', 'Untitled'),
        data.get('url'),
        data.get('content_snippet', '')[:500],
        lang_str,
        data.get('category', 'General'),
        data.get('final_verdict'),
        data.get('credibility_score', 0.0),
        data.get('ml_confidence', 0.0),
        json.dumps(data.get('ml_prediction', {})),
        data.get('deep_learning_score', 0.0),
        json.dumps(data.get('deep_learning_prediction', {})),
        json.dumps(data.get('sentiment_data', {})),
        json.dumps(data.get('source_data', {})),
        json.dumps(data.get('evidence_data', {})),
        json.dumps(data.get('xai_highlights', {})),
        data.get('report_filename')
    )
    return execute_insert(query, params)

def get_user_history(user_id: int | None = None, search: str = "", verdict_filter: str = "", limit: int = 20, offset: int = 0) -> list[dict]:
    """Retrieves analysis history filtered by user, search keywords, and verdict."""
    conditions = ["1=1"]
    params = []
    
    if user_id is not None:
        conditions.append("user_id = ?")
        params.append(user_id)
        
    if search:
        conditions.append("(title LIKE ? OR content_snippet LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
        
    if verdict_filter and verdict_filter != "all":
        conditions.append("final_verdict LIKE ?")
        params.append(f"%{verdict_filter}%")
        
    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT id, user_id, title, url, content_snippet, category, final_verdict,
               credibility_score, ml_confidence, report_filename, created_at
        FROM analyses 
        WHERE {where_clause}
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    return execute_query(query, params)

def get_analysis_details(analysis_id: int) -> dict | None:
    """Retrieves full details of a single analysis record."""
    record = execute_scalar("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    if not record:
        return None
        
    # Unpack JSON columns
    for col in ['ml_prediction', 'deep_learning_prediction', 'sentiment_data', 'source_data', 'evidence_data', 'xai_highlights']:
        if record.get(col):
            try:
                record[col] = json.loads(record[col])
            except Exception:
                pass
    return record

def delete_analysis_record(analysis_id: int, user_id: int | None = None) -> bool:
    """Deletes an analysis record with optional ownership verification."""
    if user_id is not None:
        execute_update("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id))
    else:
        execute_update("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    return True
