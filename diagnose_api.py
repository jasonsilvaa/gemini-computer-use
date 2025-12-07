#!/usr/bin/env python3
"""
Script para diagnosticar problemas com a API do Gemini
"""

import os
import sys
from google import genai
from logger_config import setup_logger, get_logger

logger = setup_logger("diagnose", level="INFO", detailed=True)

def test_api_connection():
    """Testa a conexão com a API do Gemini"""
    logger.info("=" * 60)
    logger.info("Diagnóstico da API do Gemini")
    logger.info("=" * 60)
    
    # Verificar variáveis de ambiente
    logger.info("\n1. Verificando variáveis de ambiente...")
    api_key = os.environ.get("GEMINI_API_KEY")
    use_vertexai = os.environ.get("USE_VERTEXAI", "false").lower() in ("true", "1")
    
    if api_key:
        logger.info(f"✅ GEMINI_API_KEY encontrada (primeiros 10 chars: {api_key[:10]}...)")
    else:
        logger.error("❌ GEMINI_API_KEY não encontrada!")
        return False
    
    logger.info(f"USE_VERTEXAI: {use_vertexai}")
    
    if use_vertexai:
        project = os.environ.get("VERTEXAI_PROJECT")
        location = os.environ.get("VERTEXAI_LOCATION")
        logger.info(f"VERTEXAI_PROJECT: {project}")
        logger.info(f"VERTEXAI_LOCATION: {location}")
    
    # Criar cliente
    logger.info("\n2. Criando cliente Gemini...")
    try:
        if use_vertexai:
            client = genai.Client(
                vertexai=True,
                project=os.environ.get("VERTEXAI_PROJECT"),
                location=os.environ.get("VERTEXAI_LOCATION"),
            )
            logger.info("✅ Cliente Vertex AI criado")
        else:
            client = genai.Client(api_key=api_key)
            logger.info("✅ Cliente API Key criado")
    except Exception as e:
        logger.error(f"❌ Erro ao criar cliente: {e}")
        return False
    
    # Testar chamada simples
    logger.info("\n3. Testando chamada à API...")
    try:
        model_name = "gemini-2.5-computer-use-preview-10-2025"
        logger.info(f"Modelo: {model_name}")
        
        response = client.models.generate_content(
            model=model_name,
            contents=[{"role": "user", "parts": [{"text": "Hello"}]}],
        )
        
        logger.info("✅ Resposta recebida da API")
        
        if response.candidates:
            logger.info(f"✅ Número de candidatos: {len(response.candidates)}")
            candidate = response.candidates[0]
            logger.info(f"✅ Finish reason: {candidate.finish_reason}")
            if candidate.content and candidate.content.parts:
                text = candidate.content.parts[0].text if candidate.content.parts[0].text else "N/A"
                logger.info(f"✅ Texto da resposta: {text[:100]}...")
        else:
            logger.error("❌ Resposta sem candidatos!")
            if hasattr(response, 'prompt_feedback'):
                logger.error(f"Prompt feedback: {response.prompt_feedback}")
            return False
        
        # Verificar metadata
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            logger.info(f"✅ Usage metadata: {response.usage_metadata}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DIAGNÓSTICO: API funcionando corretamente!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Erro ao chamar API: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        logger.info("\n" + "=" * 60)
        logger.error("❌ DIAGNÓSTICO: Problema detectado com a API")
        logger.info("=" * 60)
        return False


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)

