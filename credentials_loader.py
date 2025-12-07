#!/usr/bin/env python3
"""
Módulo para carregar credenciais de arquivo JSON de forma segura
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CredentialsLoader:
    """Classe para carregar e gerenciar credenciais de arquivos"""
    
    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Inicializa o carregador de credenciais
        
        Args:
            credentials_file: Caminho para o arquivo de credenciais
        """
        self.credentials_file = Path(credentials_file)
        self._credentials: Optional[Dict] = None
        
    def load(self) -> Dict:
        """
        Carrega credenciais do arquivo
        
        Returns:
            Dicionário com as credenciais carregadas
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            json.JSONDecodeError: Se o arquivo não for JSON válido
        """
        if self._credentials is not None:
            return self._credentials
            
        if not self.credentials_file.exists():
            logger.warning(f"Arquivo de credenciais não encontrado: {self.credentials_file}")
            logger.info(f"Crie um arquivo {self.credentials_file} baseado em credentials.example.json")
            return {}
        
        try:
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                self._credentials = json.load(f)
            logger.info(f"Credenciais carregadas de {self.credentials_file}")
            return self._credentials
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON do arquivo de credenciais: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
            raise
    
    def get_credentials(self, service: str) -> Optional[Dict[str, str]]:
        """
        Obtém credenciais para um serviço específico
        
        Args:
            service: Nome do serviço (ex: 'github', 'google')
            
        Returns:
            Dicionário com email e password, ou None se não encontrado
        """
        if self._credentials is None:
            self.load()
        
        if not self._credentials:
            return None
            
        return self._credentials.get(service.lower())
    
    def get_email(self, service: str) -> Optional[str]:
        """
        Obtém apenas o email de um serviço
        
        Args:
            service: Nome do serviço
            
        Returns:
            Email ou None se não encontrado
        """
        creds = self.get_credentials(service)
        if creds:
            return creds.get('email')
        return None
    
    def get_password(self, service: str) -> Optional[str]:
        """
        Obtém apenas a senha de um serviço
        
        Args:
            service: Nome do serviço
            
        Returns:
            Senha ou None se não encontrado
        """
        creds = self.get_credentials(service)
        if creds:
            return creds.get('password')
        return None
    
    def format_query_with_credentials(self, query: str, service: str = "github") -> str:
        """
        Substitui placeholders na query com credenciais reais
        
        Args:
            query: Query original que pode conter placeholders
            service: Nome do serviço para buscar credenciais
            
        Returns:
            Query com credenciais substituídas
        """
        email = self.get_email(service)
        password = self.get_password(service)
        
        if not email or not password:
            logger.warning(f"Credenciais não encontradas para {service}")
            return query
        
        # Substituir placeholders comuns
        formatted_query = query.replace("{email}", email)
        formatted_query = formatted_query.replace("{EMAIL}", email)
        formatted_query = formatted_query.replace("{password}", password)
        formatted_query = formatted_query.replace("{PASSWORD}", password)
        formatted_query = formatted_query.replace("{senha}", password)
        formatted_query = formatted_query.replace("{SENHA}", password)
        
        # Substituir referências genéricas
        formatted_query = formatted_query.replace("o email fornecido", email)
        formatted_query = formatted_query.replace("a senha fornecida", password)
        formatted_query = formatted_query.replace("o endereço de email fornecido", email)
        formatted_query = formatted_query.replace("a senha fornecida", password)
        
        return formatted_query


# Instância global para uso fácil
_loader = None

def get_loader() -> CredentialsLoader:
    """Obtém a instância global do carregador de credenciais"""
    global _loader
    if _loader is None:
        _loader = CredentialsLoader()
    return _loader

def load_credentials(service: str = "github") -> Optional[Dict[str, str]]:
    """Função auxiliar para carregar credenciais rapidamente"""
    return get_loader().get_credentials(service)

def format_query(query: str, service: str = "github") -> str:
    """Função auxiliar para formatar query com credenciais"""
    return get_loader().format_query_with_credentials(query, service)

