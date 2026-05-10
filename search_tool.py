from duckduckgo_search import DDGS

def get_market_research(startup_idea: str) -> str:
    """
    Startup ideyası əsasında internetdə qısa axtarış edir və 
    rəqiblər/bazar barədə real məlumatları qaytarır.
    """
    query = f"{startup_idea} competitors market size"
    
    # Ensure query length is reasonable for search
    if len(query) > 100:
        query = query[:100]
        
    results_text = "🌐 REAL-TIME INTERNET AXTARIŞ NƏTİCƏSİ:\n"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
        if not results:
            return results_text + "İnternetdə əlaqəli məlumat tapılmadı.\n"
            
        for i, r in enumerate(results, 1):
            title = r.get('title', 'Başlıq yoxdur')
            body = r.get('body', '')
            results_text += f"{i}. {title}\n   Xülasə: {body}\n\n"
            
        return results_text
    except Exception as e:
        return f"⚠️ İnternet axtarışı zamanı xəta baş verdi: {e}\n"
