import json
import pandas as pd
from datetime import datetime

def tweets_to_csv(json_file_path):
    """
    Convierte un archivo JSON de búsqueda de tweets (twitter_api_response) a CSV
    
    Args:
        json_file_path (str): Ruta completa al archivo JSON de tweets
    
    Returns:
        str: Ruta del archivo CSV generado
    """
    
    print(f"🐦 Convirtiendo tweets a CSV: {json_file_path}")
    
    try:
        # Cargar el archivo JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extraer los tweets
        if 'tweets' in data:
            tweets = data['tweets']
            metadata = {
                'total_tweets': data.get('total_tweets', len(tweets)),
                'total_paginas': data.get('total_paginas', 'No especificado'),
                'fecha_obtencion': data.get('fecha_obtencion', 'No especificada'),
                'ultimo_cursor': data.get('ultimo_cursor', 'No especificado')
            }
        else:
            tweets = data  # Formato directo
            metadata = {'total_tweets': len(tweets)}
        
        print(f"📊 Encontrados {len(tweets)} tweets para procesar")
        
        # Procesar tweets
        tweets_data = []
        for i, tweet in enumerate(tweets, 1):
            if i % 100 == 0:
                print(f"⏳ Procesando tweet {i}/{len(tweets)}...")
            
            # Información básica del tweet
            tweet_info = {
                'tweet_id': tweet.get('id'),
                'type': tweet.get('type'),
                'url': tweet.get('url'),
                'texto': tweet.get('text'),
                'fecha_creacion': tweet.get('createdAt'),
                'idioma': tweet.get('lang'),
                'retweets': tweet.get('retweetCount', 0),
                'respuestas': tweet.get('replyCount', 0),
                'likes': tweet.get('likeCount', 0),
                'citas': tweet.get('quoteCount', 0),
                'visualizaciones': tweet.get('viewCount', 0),
                'bookmarks': tweet.get('bookmarkCount', 0),
                'es_respuesta': tweet.get('isReply', False),
                'fuente': tweet.get('source'),
                'conversation_id': tweet.get('conversationId'),
                'in_reply_to_id': tweet.get('inReplyToId'),
                'in_reply_to_user_id': tweet.get('inReplyToUserId'),
                'in_reply_to_username': tweet.get('inReplyToUsername')
            }
            
            # Información del autor
            author = tweet.get('author', {})
            tweet_info.update({
                'autor_id': author.get('id'),
                'autor_username': author.get('userName'),
                'autor_nombre': author.get('name'),
                'autor_verificado': author.get('isVerified', False),
                'autor_verificado_azul': author.get('isBlueVerified', False),
                'autor_seguidores': author.get('followers', 0),
                'autor_siguiendo': author.get('following', 0),
                'autor_descripcion': author.get('description'),
                'autor_ubicacion': author.get('location'),
                'autor_fecha_creacion': author.get('createdAt'),
                'autor_tweets_count': author.get('statusesCount', 0)
            })
            
            # Entidades y engagement
            entities = tweet.get('entities', {})
            hashtags = entities.get('hashtags', [])
            urls = entities.get('urls', [])
            user_mentions = entities.get('user_mentions', [])
            
            tweet_info.update({
                'engagement_total': (tweet.get('likeCount', 0) + tweet.get('retweetCount', 0) + 
                                   tweet.get('replyCount', 0) + tweet.get('quoteCount', 0)),
                'numero_hashtags': len(hashtags),
                'hashtags': ', '.join([h.get('text', '') for h in hashtags]),
                'numero_urls': len(urls),
                'urls': ', '.join([u.get('expanded_url', '') for u in urls]),
                'numero_menciones': len(user_mentions),
                'menciones': ', '.join([m.get('screen_name', '') for m in user_mentions]),
                'tipo_dataset': 'busqueda',
                'ultimo_cursor_disponible': metadata.get('ultimo_cursor', 'No especificado')
            })
            
            tweets_data.append(tweet_info)
        
        # Crear DataFrame y archivo CSV
        df = pd.DataFrame(tweets_data)
        
        # Generar nombre del archivo CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f'tweets_search_{timestamp}_{len(tweets_data)}tweets.csv'
        
        # Guardar CSV
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"✅ CSV generado: {csv_filename}")
        print(f"📊 Total de tweets procesados: {len(tweets_data)}")
        if metadata.get('ultimo_cursor') != 'No especificado':
            print(f"🔄 Último cursor disponible: {metadata['ultimo_cursor'][:20]}...")
        
        return csv_filename
        
    except Exception as e:
        print(f"❌ Error al convertir tweets: {e}")
        return None

def replies_to_csv(json_file_path):
    """
    Convierte un archivo JSON de respuestas de tweet (twitter_replies) a CSV
    
    Args:
        json_file_path (str): Ruta completa al archivo JSON de respuestas
    
    Returns:
        str: Ruta del archivo CSV generado
    """
    
    print(f"💬 Convirtiendo respuestas a CSV: {json_file_path}")
    
    try:
        # Cargar el archivo JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extraer las respuestas
        if 'replies' in data:
            replies = data['replies']
            metadata = {
                'tweet_id_original': data.get('tweet_id', 'No especificado'),
                'total_replies': data.get('total_replies', len(replies)),
                'total_paginas': data.get('total_paginas', 'No especificado'),
                'fecha_obtencion': data.get('fecha_obtencion', 'No especificada'),
                'ultimo_cursor': data.get('ultimo_cursor', 'No especificado'),
                'parametros': data.get('parametros', {})
            }
        else:
            print("❌ El archivo no contiene el campo 'replies'")
            return None
        
        print(f"📊 Encontradas {len(replies)} respuestas para procesar")
        print(f"🎯 Tweet original: {metadata['tweet_id_original']}")
        
        # Procesar respuestas
        replies_data = []
        for i, reply in enumerate(replies, 1):
            if i % 100 == 0:
                print(f"⏳ Procesando respuesta {i}/{len(replies)}...")
            
            # Información básica de la respuesta
            reply_info = {
                'reply_id': reply.get('id'),
                'tweet_original_id': metadata['tweet_id_original'],
                'type': reply.get('type'),
                'url': reply.get('url'),
                'texto': reply.get('text'),
                'fecha_creacion': reply.get('createdAt'),
                'idioma': reply.get('lang'),
                'retweets': reply.get('retweetCount', 0),
                'respuestas': reply.get('replyCount', 0),
                'likes': reply.get('likeCount', 0),
                'citas': reply.get('quoteCount', 0),
                'visualizaciones': reply.get('viewCount', 0),
                'bookmarks': reply.get('bookmarkCount', 0),
                'es_respuesta': reply.get('isReply', False),
                'fuente': reply.get('source'),
                'conversation_id': reply.get('conversationId'),
                'in_reply_to_id': reply.get('inReplyToId'),
                'in_reply_to_user_id': reply.get('inReplyToUserId'),
                'in_reply_to_username': reply.get('inReplyToUsername')
            }
            
            # Información del autor de la respuesta
            author = reply.get('author', {})
            reply_info.update({
                'autor_id': author.get('id'),
                'autor_username': author.get('userName'),
                'autor_nombre': author.get('name'),
                'autor_verificado': author.get('isVerified', False),
                'autor_verificado_azul': author.get('isBlueVerified', False),
                'autor_seguidores': author.get('followers', 0),
                'autor_siguiendo': author.get('following', 0),
                'autor_descripcion': author.get('description'),
                'autor_ubicacion': author.get('location'),
                'autor_fecha_creacion': author.get('createdAt'),
                'autor_tweets_count': author.get('statusesCount', 0)
            })
            
            # Entidades y engagement
            entities = reply.get('entities', {})
            hashtags = entities.get('hashtags', [])
            urls = entities.get('urls', [])
            user_mentions = entities.get('user_mentions', [])
            
            reply_info.update({
                'engagement_total': (reply.get('likeCount', 0) + reply.get('retweetCount', 0) + 
                                   reply.get('replyCount', 0) + reply.get('quoteCount', 0)),
                'numero_hashtags': len(hashtags),
                'hashtags': ', '.join([h.get('text', '') for h in hashtags]),
                'numero_urls': len(urls),
                'urls': ', '.join([u.get('expanded_url', '') for u in urls]),
                'numero_menciones': len(user_mentions),
                'menciones': ', '.join([m.get('screen_name', '') for m in user_mentions]),
                'tipo_dataset': 'respuesta',
                'ultimo_cursor_disponible': metadata.get('ultimo_cursor', 'No especificado'),
                'continue_in_usado': metadata['parametros'].get('continue_in', 'No especificado')
            })
            
            replies_data.append(reply_info)
        
        # Crear DataFrame y archivo CSV
        df = pd.DataFrame(replies_data)
        
        # Generar nombre del archivo CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tweet_id_short = metadata['tweet_id_original'][:10] if metadata['tweet_id_original'] != 'No especificado' else 'unknown'
        csv_filename = f'replies_{tweet_id_short}_{timestamp}_{len(replies_data)}replies.csv'
        
        # Guardar CSV
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"✅ CSV generado: {csv_filename}")
        print(f"📊 Total de respuestas procesadas: {len(replies_data)}")
        print(f"🎯 Tweet original: {metadata['tweet_id_original']}")
        if metadata.get('ultimo_cursor') != 'No especificado':
            print(f"🔄 Último cursor disponible: {metadata['ultimo_cursor'][:20]}...")
        if metadata['parametros'].get('continue_in'):
            print(f"⚡ Se usó continue_in: {metadata['parametros']['continue_in'][:20]}...")
        
        return csv_filename
        
    except Exception as e:
        print(f"❌ Error al convertir respuestas: {e}")
        return None

def retweets_to_csv(json_file_path):
    """
    Convierte un archivo JSON de retweeters de tweet (twitter_retweeters) a CSV
    
    Args:
        json_file_path (str): Ruta completa al archivo JSON de retweeters
    
    Returns:
        str: Ruta del archivo CSV generado
    """
    
    print(f"🔄 Convirtiendo retweeters a CSV: {json_file_path}")
    
    try:
        # Cargar el archivo JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extraer los retweeters
        if 'retweeters' in data:
            retweeters = data['retweeters']
            metadata = {
                'tweet_id_original': data.get('tweet_id', 'No especificado'),
                'total_retweeters': data.get('total_retweeters', len(retweeters)),
                'total_paginas': data.get('total_paginas', 'No especificado'),
                'fecha_obtencion': data.get('fecha_obtencion', 'No especificada'),
                'ultimo_cursor': data.get('ultimo_cursor', 'No especificado'),
                'parametros': data.get('parametros', {})
            }
        else:
            print("❌ El archivo no contiene el campo 'retweeters'")
            return None
        
        print(f"📊 Encontrados {len(retweeters)} retweeters para procesar")
        print(f"🎯 Tweet original: {metadata['tweet_id_original']}")
        
        # Procesar retweeters
        retweeters_data = []
        for i, retweeter in enumerate(retweeters, 1):
            if i % 100 == 0:
                print(f"⏳ Procesando retweeter {i}/{len(retweeters)}...")
            
            # Información básica del retweeter
            retweeter_info = {
                'user_id': retweeter.get('id'),
                'tweet_original_id': metadata['tweet_id_original'],
                'type': retweeter.get('type'),
                'username': retweeter.get('userName'),
                'nombre': retweeter.get('name'),
                'url_perfil': retweeter.get('url'),
                'descripcion': retweeter.get('description'),
                'ubicacion': retweeter.get('location'),
                'seguidores': retweeter.get('followers', 0),
                'siguiendo': retweeter.get('following', 0),
                'puede_dm': retweeter.get('canDm', False),
                'fecha_creacion': retweeter.get('createdAt'),
                'favoritos_count': retweeter.get('favouritesCount', 0),
                'media_count': retweeter.get('mediaCount', 0),
                'tweets_count': retweeter.get('statusesCount', 0),
                'verificado': retweeter.get('verified', False),
                'verificado_azul': retweeter.get('isBlueVerified', False),
                'tipo_verificacion': retweeter.get('verifiedType', ''),
                'foto_perfil': retweeter.get('profilePicture'),
                'foto_portada': retweeter.get('coverPicture'),
                'protegido': retweeter.get('protected', False),
                'tiene_timelines_custom': retweeter.get('hasCustomTimelines', False),
                'es_traductor': retweeter.get('isTranslator', False),
                'posiblemente_sensible': retweeter.get('possiblySensitive', False),
                'es_automatizado': retweeter.get('isAutomated', False),
                'automatizado_por': retweeter.get('automatedBy'),
                'no_disponible': retweeter.get('unavailable', False),
                'razon_no_disponible': retweeter.get('unavailableReason'),
                'mensaje': retweeter.get('message')
            }
            
            # Información adicional de perfil
            profile_bio = retweeter.get('profile_bio', {})
            if profile_bio:
                retweeter_info.update({
                    'bio_descripcion': profile_bio.get('description', ''),
                })
                
                # Extraer URLs de la bio si existen
                entities = profile_bio.get('entities', {})
                if entities:
                    description_entities = entities.get('description', {})
                    url_entities = entities.get('url', {})
                    
                    bio_urls = []
                    if description_entities.get('urls'):
                        bio_urls.extend([url.get('expanded_url', '') for url in description_entities['urls']])
                    if url_entities.get('urls'):
                        bio_urls.extend([url.get('expanded_url', '') for url in url_entities['urls']])
                    
                    retweeter_info.update({
                        'bio_urls': ', '.join(bio_urls),
                        'numero_bio_urls': len(bio_urls)
                    })
            
            # Información de países restringidos
            withheld_countries = retweeter.get('withheldInCountries', [])
            retweeter_info.update({
                'paises_restringidos': ', '.join(withheld_countries),
                'numero_paises_restringidos': len(withheld_countries)
            })
            
            # Tweets fijados
            pinned_tweets = retweeter.get('pinnedTweetIds', [])
            retweeter_info.update({
                'tweets_fijados': ', '.join(pinned_tweets),
                'numero_tweets_fijados': len(pinned_tweets)
            })
            
            # Métricas de engagement potencial
            followers = retweeter.get('followers', 0)
            following = retweeter.get('following', 0)
            
            retweeter_info.update({
                'ratio_seguidores_siguiendo': round(followers / following, 2) if following > 0 else 0,
                'tipo_cuenta': 'Popular' if followers > 10000 else 'Micro-influencer' if followers > 1000 else 'Regular',
                'tipo_dataset': 'retweeter',
                'ultimo_cursor_disponible': metadata.get('ultimo_cursor', 'No especificado'),
                'continue_in_usado': metadata['parametros'].get('continue_in', 'No especificado')
            })
            
            retweeters_data.append(retweeter_info)
        
        # Crear DataFrame y archivo CSV
        df = pd.DataFrame(retweeters_data)
        
        # Generar nombre del archivo CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tweet_id_short = metadata['tweet_id_original'][:10] if metadata['tweet_id_original'] != 'No especificado' else 'unknown'
        csv_filename = f'retweeters_{tweet_id_short}_{timestamp}_{len(retweeters_data)}retweeters.csv'
        
        # Guardar CSV
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"✅ CSV generado: {csv_filename}")
        print(f"📊 Total de retweeters procesados: {len(retweeters_data)}")
        print(f"🎯 Tweet original: {metadata['tweet_id_original']}")
        if metadata.get('ultimo_cursor') != 'No especificado':
            print(f"🔄 Último cursor disponible: {metadata['ultimo_cursor'][:20]}...")
        if metadata['parametros'].get('continue_in'):
            print(f"⚡ Se usó continue_in: {metadata['parametros']['continue_in'][:20]}...")
        
        return csv_filename
        
    except Exception as e:
        print(f"❌ Error al convertir retweeters: {e}")
        return None

