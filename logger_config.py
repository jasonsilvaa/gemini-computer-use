#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Configuração de logging detalhado para Gemini Computer Use
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Níveis de log customizados
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para terminal"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class DetailedFormatter(logging.Formatter):
    """Formatter detalhado com informações completas"""
    
    def format(self, record):
        # Formato: [TIMESTAMP] [LEVEL] [MODULE:FUNCTION:LINE] MESSAGE
        format_str = (
            "[%(asctime)s] "
            "[%(levelname)-8s] "
            "[%(name)s:%(funcName)s:%(lineno)d] "
            "%(message)s"
        )
        formatter = logging.Formatter(format_str, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logger(
    name: str = "gemini_computer_use",
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console: bool = True,
    detailed: bool = True
) -> logging.Logger:
    """
    Configura um logger detalhado
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log (opcional)
        console: Se deve logar no console
        detailed: Se deve usar formato detalhado
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Nível de log
    log_level = level or os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(LOG_LEVELS.get(log_level, logging.INFO))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato detalhado
    if detailed:
        formatter = DetailedFormatter()
    else:
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
    
    # Handler para console
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        # Usar formatter colorido se suportado
        if sys.stdout.isatty():
            console_handler.setFormatter(ColoredFormatter(
                '[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s',
                datefmt='%H:%M:%S'
            ))
        else:
            console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Handler para arquivo
    if log_file:
        # Criar diretório se não existir
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtém um logger configurado
    
    Args:
        name: Nome do logger (usa o nome do módulo se None)
    
    Returns:
        Logger
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'gemini_computer_use')
    
    logger = logging.getLogger(name)
    
    # Se não tem handlers, configurar
    if not logger.handlers:
        setup_logger(name)
    
    return logger


# Logger padrão
default_logger = setup_logger()

