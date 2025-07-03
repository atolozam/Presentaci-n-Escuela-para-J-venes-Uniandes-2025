from pysentimiento import create_analyzer
import pandas as pd

def analyze_sentiment(text, lenguage='es'):
    """
    Analiza el sentimiento de un texto en español.
    
    Args:
        text (str): El texto a analizar.
        language (str): El idioma del texto. Por defecto es 'es' para español.
        
    Returns:
        dict: Un diccionario con los resultados del análisis de sentimiento.
    """
    analyzer = create_analyzer(task="sentiment", lang="es")
    result = analyzer.predict(text)
    result_sentiment = result.output
    result_probas = result.probas
    return result_sentiment, result_probas

def detect_hate_speech(text, language='es'):
    """
    Detecta discurso de odio en un texto en español.
    
    Args:
        text (str): El texto a analizar.
        language (str): El idioma del texto. Por defecto es 'es' para español.
        
    Returns:
        dict: Un diccionario con los resultados de la detección de discurso de odio.
    """
    analyzer = create_analyzer(task="hate_speech", lang="es")
    result = analyzer.predict(text)
    return result

def create_replies_dataframe_fixed(archivos_replies):
    """
    Versión corregida que funciona correctamente.
    """
    base = pd.DataFrame()  
    
    for archivo in archivos_replies:  
        print(f"📄 {archivo}")
        df = pd.read_csv(archivo)
        
        base = pd.concat([base, df], ignore_index=True)
        print(f"   Total: {len(base)} respuestas")
    
    return base