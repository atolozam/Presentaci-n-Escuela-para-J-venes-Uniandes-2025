import requests
import json
import time
from datetime import datetime

def get_tweets_by_search(search_query, limit_tweets=None):
    """
    Obtiene todos los tweets usando paginación correctamente
    """
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    
    # 🔑 Reemplaza con tu API key real
    headers = {"X-API-Key": "1deb4be30bd949899650f493714c46f3"}
    
    # 📋 Query Parameters base
    base_params = {
        "query": search_query,
        "queryType": "Latest"
    }
    
    # Lista para almacenar todos los tweets
    todos_los_tweets = []
    cursor = ""  # Primera página empieza con cursor vacío
    pagina_actual = 1
    
    print("🌐 Iniciando obtención de tweets con paginación...")
    print(f"Query: {base_params['query']}")
    if limit_tweets:
        print(f"📊 Límite de tweets: {limit_tweets}")
    else:
        print("📊 Sin límite - obteniendo todos los tweets disponibles")
    print("=" * 50)
    
    while True:
        print(f"📄 Procesando página {pagina_actual}...")
        
        # Preparar parámetros para esta página
        params = base_params.copy()
        if cursor:  # Solo agregar cursor si no está vacío
            params["cursor"] = cursor
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'tweets' in data:
                    tweets_pagina = data.get('tweets', [])
                    has_next_page = data.get('has_next_page', False)
                    next_cursor = data.get('next_cursor', '')
                    
                    print(f"✅ Página {pagina_actual}: {len(tweets_pagina)} tweets obtenidos")
                    
                    # Agregar tweets de esta página a la lista total
                    todos_los_tweets.extend(tweets_pagina)
                    
                    # Verificar si hemos alcanzado el límite de tweets
                    if limit_tweets and len(todos_los_tweets) >= limit_tweets:
                        # Truncar la lista si excede el límite
                        todos_los_tweets = todos_los_tweets[:limit_tweets]
                        print(f"🎯 Límite de {limit_tweets} tweets alcanzado")
                        break
                    
                    # Verificar si hay más páginas
                    if has_next_page and next_cursor:
                        cursor = next_cursor
                        pagina_actual += 1
                        print(f"➡️  Hay más páginas. Cursor siguiente: {next_cursor[:20]}...")
                        
                        # Pausa entre requests para evitar rate limiting
                        time.sleep(1)
                    else:
                        print("🏁 No hay más páginas disponibles")
                        break
                        
                elif data.get('status') == 'success':
                    # Formato alternativo con campo status
                    tweets_pagina = data.get('tweets', [])
                    has_next_page = data.get('has_next_page', False)
                    next_cursor = data.get('next_cursor', '')
                    
                    print(f"✅ Página {pagina_actual}: {len(tweets_pagina)} tweets obtenidos")
                    todos_los_tweets.extend(tweets_pagina)
                    
                    # Verificar si hemos alcanzado el límite de tweets
                    if limit_tweets and len(todos_los_tweets) >= limit_tweets:
                        # Truncar la lista si excede el límite
                        todos_los_tweets = todos_los_tweets[:limit_tweets]
                        print(f"🎯 Límite de {limit_tweets} tweets alcanzado")
                        break
                    
                    if has_next_page and next_cursor:
                        cursor = next_cursor
                        pagina_actual += 1
                        print(f"➡️  Hay más páginas. Cursor siguiente: {next_cursor[:20]}...")
                        time.sleep(1)
                    else:
                        print("🏁 No hay más páginas disponibles")
                        break
                else:
                    print(f"❌ Error en respuesta: {data.get('message', 'Formato de respuesta no reconocido')}")
                    print(f"💡 Respuesta completa para debug: {json.dumps(data, indent=2)[:500]}...")
                    break
                    
            elif response.status_code == 401:
                print("🔐 Error 401: API Key inválida")
                break
            elif response.status_code == 403:
                print("🚫 Error 403: Acceso prohibido")
                break
            elif response.status_code == 429:
                print("⏰ Error 429: Límite de rate excedido - esperando 60 segundos...")
                time.sleep(60)
                continue
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Respuesta: {response.text}")
                break
                
        except Exception as e:
            print(f"💥 Error en página {pagina_actual}: {e}")
            break
    
    # Guardar todos los tweets obtenidos
    if todos_los_tweets:
        resultado_final = {
            "tweets": todos_los_tweets,
            "total_tweets": len(todos_los_tweets),
            "total_paginas": pagina_actual,
            "fecha_obtencion": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ultimo_cursor": cursor  # Guardar el último cursor para poder continuar
        }
        
        # Generar timestamp para el nombre del archivo
        current_datetime = datetime.now()
        current_time_str = current_datetime.strftime("%Y%m%d_%H%M%S")
        
        # Guardar en el archivo en raw_data
        with open(f'raw_data/twitter_search_request_{current_time_str}.json', 'w', encoding='utf-8') as f:
            json.dump(resultado_final, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN FINAL:")
        print(f"✅ Total de tweets obtenidos: {len(todos_los_tweets)}")
        print(f"💾 Datos guardados en 'raw_data/twitter_search_request_{current_time_str}.json'")
        
        return resultado_final
    else:
        print("❌ No se obtuvieron tweets")
        return None

def get_tweet_responses(tweet_id, limit_responses=None, since_time=None, until_time=None, continue_in=None):
    """
    Obtiene todas las respuestas (replies) de un tweet usando paginación
    
    Args:
        tweet_id (str): ID del tweet original para obtener sus respuestas
        limit_responses (int, optional): Límite máximo de respuestas a obtener. Si es None, obtiene todas.
        since_time (int, optional): Timestamp unix en segundos - obtener respuestas desde esta fecha
        until_time (int, optional): Timestamp unix en segundos - obtener respuestas hasta esta fecha
        continue_in (str, optional): Cursor desde donde continuar una búsqueda previa. Si se proporciona, 
                                   inicia desde este cursor en lugar del principio.
    
    Returns:
        dict: Diccionario con todas las respuestas obtenidas
    """
    url = "https://api.twitterapi.io/twitter/tweet/replies"
    
    # 🔑 Usar la misma API key
    headers = {"X-API-Key": "1deb4be30bd949899650f493714c46f3"}
    
    # 📋 Query Parameters base
    base_params = {
        "tweetId": tweet_id
    }
    
    # Agregar parámetros opcionales si están presentes
    if since_time:
        base_params["sinceTime"] = since_time
    if until_time:
        base_params["untilTime"] = until_time
    
    # Lista para almacenar todas las respuestas
    todas_las_respuestas = []
    cursor = continue_in if continue_in else ""  # Usar continue_in si se proporciona, sino empezar desde el principio
    pagina_actual = 1
    
    print("🌐 Iniciando obtención de respuestas con paginación...")
    print(f"Tweet ID: {tweet_id}")
    if limit_responses:
        print(f"📊 Límite de respuestas: {limit_responses}")
    else:
        print("📊 Sin límite - obteniendo todas las respuestas disponibles")
    
    if continue_in:
        print(f"🔄 Continuando desde cursor: {continue_in[:20]}...")
        print("⚠️  NOTA: Al continuar desde un cursor, el contador de páginas se reinicia")
    
    print("=" * 50)
    
    while True:
        print(f"📄 Procesando página {pagina_actual}...")
        
        # Preparar parámetros para esta página
        params = base_params.copy()
        if cursor:  # Solo agregar cursor si no está vacío
            params["cursor"] = cursor
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                
                # Verificar si la respuesta es exitosa
                if data.get('status') == 'success':
                    # Para replies, la API devuelve los tweets en el campo 'tweets' (no 'replies')
                    respuestas_pagina = data.get('tweets', [])
                    has_next_page = data.get('has_next_page', False)
                    next_cursor = data.get('next_cursor', '')
                    
                    print(f"✅ Página {pagina_actual}: {len(respuestas_pagina)} respuestas obtenidas")
                    
                    # Agregar respuestas de esta página a la lista total
                    todas_las_respuestas.extend(respuestas_pagina)
                    
                    # Verificar si hemos alcanzado el límite de respuestas
                    if limit_responses and len(todas_las_respuestas) >= limit_responses:
                        # Truncar la lista si excede el límite
                        todas_las_respuestas = todas_las_respuestas[:limit_responses]
                        print(f"🎯 Límite de {limit_responses} respuestas alcanzado")
                        break
                    
                    # Verificar si hay más páginas y el cursor cambió
                    if has_next_page and next_cursor and next_cursor != cursor:
                        cursor = next_cursor
                        pagina_actual += 1
                        print(f"➡️  Hay más páginas. Cursor siguiente: {next_cursor[:20]}...")
                        print(f"💡 Para continuar desde aquí usar: continue_in='{next_cursor}'")
                        
                        # Pausa entre requests para evitar rate limiting
                        time.sleep(1)
                    else:
                        if next_cursor == cursor:
                            print("🔄 Cursor no cambió - terminando para evitar bucle infinito")
                        else:
                            print("🏁 No hay más páginas disponibles")
                        break
                else:
                    print(f"❌ Error en respuesta: {data.get('message', 'Formato de respuesta no reconocido')}")
                    print(f"💡 Respuesta completa para debug: {json.dumps(data, indent=2)[:500]}...")
                    break
                    
            elif response.status_code == 401:
                print("🔐 Error 401: API Key inválida")
                break
            elif response.status_code == 403:
                print("🚫 Error 403: Acceso prohibido")
                break
            elif response.status_code == 429:
                print("⏰ Error 429: Límite de rate excedido - esperando 60 segundos...")
                time.sleep(60)
                continue
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Respuesta: {response.text}")
                break
                
        except Exception as e:
            print(f"💥 Error en página {pagina_actual}: {e}")
            break
    
    # Guardar todas las respuestas obtenidas
    if todas_las_respuestas:
        resultado_final = {
            "tweet_id": tweet_id,
            "replies": todas_las_respuestas,
            "total_replies": len(todas_las_respuestas),
            "total_paginas": pagina_actual,
            "fecha_obtencion": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ultimo_cursor": cursor,  # Guardar el último cursor para poder continuar
            "parametros": {
                "since_time": since_time,
                "until_time": until_time,
                "limit_responses": limit_responses,
                "continue_in": continue_in
            }
        }
        
        # Generar timestamp para el nombre del archivo
        current_datetime = datetime.now()
        current_time_str = current_datetime.strftime("%Y%m%d_%H%M%S")
        
        # Guardar en el archivo en raw_data
        with open(f'raw_data/twitter_replies_{tweet_id}_{current_time_str}.json', 'w', encoding='utf-8') as f:
            json.dump(resultado_final, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN FINAL:")
        print(f"✅ Total de respuestas obtenidas: {len(todas_las_respuestas)}")
        print(f"💾 Datos guardados en 'raw_data/twitter_replies_{tweet_id}_{current_time_str}.json'")
        
        return resultado_final
    else:
        print("❌ No se obtuvieron respuestas")
        return None

def get_tweet_retweets(tweet_id, limit_responses=None, continue_in=None):
    """
    Obtiene todos los retweeters de un tweet usando paginación
    
    Args:
        tweet_id (str): ID del tweet original para obtener sus retweeters
        limit_responses (int, optional): Límite máximo de retweeters a obtener. Si es None, obtiene todos.
        continue_in (str, optional): Cursor desde donde continuar una búsqueda previa. Si se proporciona, 
                                   inicia desde este cursor en lugar del principio.
    
    Returns:
        dict: Diccionario con todos los retweeters obtenidos
    """
    url = "https://api.twitterapi.io/twitter/tweet/retweeters"
    
    # 🔑 Usar la misma API key
    headers = {"X-API-Key": "1deb4be30bd949899650f493714c46f3"}
    
    # 📋 Query Parameters base
    base_params = {
        "tweetId": tweet_id
    }
    
    # Lista para almacenar todos los retweeters
    todos_los_retweeters = []
    cursor = continue_in if continue_in else ""  # Usar continue_in si se proporciona, sino empezar desde el principio
    pagina_actual = 1
    
    print("🌐 Iniciando obtención de retweeters con paginación...")
    print(f"Tweet ID: {tweet_id}")
    if limit_responses:
        print(f"📊 Límite de retweeters: {limit_responses}")
    else:
        print("📊 Sin límite - obteniendo todos los retweeters disponibles")
    
    if continue_in:
        print(f"🔄 Continuando desde cursor: {continue_in[:20]}...")
        print("⚠️  NOTA: Al continuar desde un cursor, el contador de páginas se reinicia")
    
    print("=" * 50)
    
    while True:
        print(f"📄 Procesando página {pagina_actual}...")
        
        # Preparar parámetros para esta página
        params = base_params.copy()
        if cursor:  # Solo agregar cursor si no está vacío
            params["cursor"] = cursor
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Debug: Mostrar la estructura de la respuesta
                print(f"🔍 Debug - Claves en respuesta: {list(data.keys())}")
                print(f"📝 Debug - Status en respuesta: {data.get('status', 'NO ENCONTRADO')}")
                
                # Verificar si la respuesta es exitosa
                # Para retweeters, la API puede no incluir 'status', pero si tiene 'users' es exitosa
                if data.get('status') == 'success' or 'users' in data:
                    # Para retweeters, la API devuelve los usuarios en el campo 'users'
                    retweeters_pagina = data.get('users', [])
                    has_next_page = data.get('has_next_page', False)
                    next_cursor = data.get('next_cursor', '')
                    
                    print(f"✅ Página {pagina_actual}: {len(retweeters_pagina)} retweeters obtenidos")
                    
                    # Agregar retweeters de esta página a la lista total
                    todos_los_retweeters.extend(retweeters_pagina)
                    
                    # Verificar si hemos alcanzado el límite de retweeters
                    if limit_responses and len(todos_los_retweeters) >= limit_responses:
                        # Truncar la lista si excede el límite
                        todos_los_retweeters = todos_los_retweeters[:limit_responses]
                        print(f"🎯 Límite de {limit_responses} retweeters alcanzado")
                        break
                    
                    # Verificar si hay más páginas y el cursor cambió
                    if has_next_page and next_cursor and next_cursor != cursor:
                        cursor = next_cursor
                        pagina_actual += 1
                        print(f"➡️  Hay más páginas. Cursor siguiente: {next_cursor[:20]}...")
                        print(f"💡 Para continuar desde aquí usar: continue_in='{next_cursor}'")
                        
                        # Pausa entre requests para evitar rate limiting
                        time.sleep(1)
                    else:
                        if next_cursor == cursor:
                            print("🔄 Cursor no cambió - terminando para evitar bucle infinito")
                        else:
                            print("🏁 No hay más páginas disponibles")
                        break
                else:
                    print(f"❌ Error en respuesta: {data.get('message', 'Formato de respuesta no reconocido')}")
                    print(f"💡 Respuesta completa para debug: {json.dumps(data, indent=2)[:500]}...")
                    break
                    
            elif response.status_code == 401:
                print("🔐 Error 401: API Key inválida")
                break
            elif response.status_code == 403:
                print("🚫 Error 403: Acceso prohibido")
                break
            elif response.status_code == 429:
                print("⏰ Error 429: Límite de rate excedido - esperando 60 segundos...")
                time.sleep(60)
                continue
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Respuesta: {response.text}")
                break
                
        except Exception as e:
            print(f"💥 Error en página {pagina_actual}: {e}")
            break
    
    # Guardar todos los retweeters obtenidos
    if todos_los_retweeters:
        resultado_final = {
            "tweet_id": tweet_id,
            "retweeters": todos_los_retweeters,
            "total_retweeters": len(todos_los_retweeters),
            "total_paginas": pagina_actual,
            "fecha_obtencion": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ultimo_cursor": cursor,  # Guardar el último cursor para poder continuar
            "parametros": {
                "limit_responses": limit_responses,
                "continue_in": continue_in
            }
        }
        
        # Generar timestamp para el nombre del archivo
        current_datetime = datetime.now()
        current_time_str = current_datetime.strftime("%Y%m%d_%H%M%S")
        
        # Guardar en el archivo en raw_data
        with open(f'raw_data/twitter_retweeters_{tweet_id}_{current_time_str}.json', 'w', encoding='utf-8') as f:
            json.dump(resultado_final, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN FINAL:")
        print(f"✅ Total de retweeters obtenidos: {len(todos_los_retweeters)}")
        print(f"💾 Datos guardados en 'raw_data/twitter_retweeters_{tweet_id}_{current_time_str}.json'")
        
        return resultado_final
    else:
        print("❌ No se obtuvieron retweeters")
        return None
