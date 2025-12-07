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
Interface Web para Gemini Computer Use
Acesse em: http://localhost:8080 (ou porta especificada)
"""

from flask import Flask, render_template_string, request, jsonify, Response
import threading
import queue
import base64
import json
import os
import time
from io import BytesIO

from agent import BrowserAgent
from computers import BrowserbaseComputer, PlaywrightComputer, EnvState

PLAYWRIGHT_SCREEN_SIZE = (1440, 900)

app = Flask(__name__)

# Estado global
agent_state = {
    'is_running': False,
    'logs': [],
    'latest_screenshot': None,
    'status': 'Pronto',
    'current_url': None,
    'agent_thread': None,
    'log_queue': queue.Queue(),
    'screenshot_queue': queue.Queue(),
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Computer Use - Interface Web</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
        @media (max-width: 1024px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
        .panel {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }
        .panel h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 600;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        .buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        .btn-danger:hover:not(:disabled) {
            background: #c0392b;
        }
        .btn-secondary {
            background: #95a5a6;
            color: white;
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .logs {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 8px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.6;
        }
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-left: 3px solid transparent;
        }
        .log-entry.info {
            border-left-color: #3498db;
        }
        .log-entry.warning {
            border-left-color: #f39c12;
        }
        .log-entry.error {
            border-left-color: #e74c3c;
        }
        .screenshot-container {
            background: #1e1e1e;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .screenshot-container img {
            max-width: 100%;
            max-height: 600px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .status-bar {
            background: #34495e;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-indicator.ready {
            background: #2ecc71;
        }
        .status-indicator.running {
            background: #f39c12;
            animation: pulse 1.5s infinite;
        }
        .status-indicator.error {
            background: #e74c3c;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Gemini Computer Use</h1>
            <p>Interface Web para Automação de Navegador com IA</p>
        </div>
        
        <div class="content">
            <div class="panel">
                <h2>⚙️ Configurações</h2>
                <form id="configForm">
                    <div class="form-group">
                        <label for="query">Query (Tarefa):</label>
                        <textarea id="query" name="query" placeholder="Ex: Go to Google and type 'Hello World' into the search bar" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="env">Ambiente:</label>
                        <select id="env" name="env">
                            <option value="playwright">Playwright (Local)</option>
                            <option value="browserbase">Browserbase (Remoto)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="initial_url">URL Inicial:</label>
                        <input type="url" id="initial_url" name="initial_url" value="https://www.google.com">
                    </div>
                    
                    <div class="form-group">
                        <label for="model">Modelo:</label>
                        <input type="text" id="model" name="model" value="gemini-2.5-computer-use-preview-10-2025">
                    </div>
                    
                    <div class="form-group">
                        <div class="checkbox-group">
                            <input type="checkbox" id="highlight_mouse" name="highlight_mouse">
                            <label for="highlight_mouse">Destacar posição do mouse</label>
                        </div>
                    </div>
                    
                    <div class="buttons">
                        <button type="button" class="btn-primary" id="startBtn" onclick="startAgent()">▶ Iniciar</button>
                        <button type="button" class="btn-danger" id="stopBtn" onclick="stopAgent()" disabled>⏹ Parar</button>
                        <button type="button" class="btn-secondary" onclick="clearLogs()">🗑 Limpar</button>
                    </div>
                </form>
            </div>
            
            <div class="panel">
                <h2>📸 Screenshot</h2>
                <div class="screenshot-container" id="screenshotContainer">
                    <p style="color: #888;">Nenhuma screenshot disponível</p>
                </div>
            </div>
        </div>
        
        <div class="panel" style="margin: 20px;">
            <h2>📋 Logs</h2>
            <div class="logs" id="logs"></div>
        </div>
        
        <div class="status-bar">
            <div>
                <span class="status-indicator ready" id="statusIndicator"></span>
                <span id="statusText">Pronto</span>
            </div>
            <div id="currentUrl" style="font-size: 12px; opacity: 0.8;"></div>
        </div>
    </div>
    
    <script>
        let updateInterval;
        
        function addLog(message, level = 'info') {
            const logsDiv = document.getElementById('logs');
            const entry = document.createElement('div');
            entry.className = `log-entry ${level}`;
            const timestamp = new Date().toLocaleTimeString();
            entry.textContent = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
            logsDiv.appendChild(entry);
            logsDiv.scrollTop = logsDiv.scrollHeight;
        }
        
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('statusText').textContent = data.status;
                    const indicator = document.getElementById('statusIndicator');
                    indicator.className = 'status-indicator ' + (data.is_running ? 'running' : 'ready');
                    
                    if (data.current_url) {
                        document.getElementById('currentUrl').textContent = data.current_url;
                    }
                    
                    const startBtn = document.getElementById('startBtn');
                    const stopBtn = document.getElementById('stopBtn');
                    startBtn.disabled = data.is_running;
                    stopBtn.disabled = !data.is_running;
                });
        }
        
        function updateLogs() {
            fetch('/api/logs')
                .then(r => r.json())
                .then(data => {
                    const logsDiv = document.getElementById('logs');
                    const currentLength = logsDiv.children.length;
                    if (data.logs.length > currentLength) {
                        data.logs.slice(currentLength).forEach(log => {
                            addLog(log.message, log.level);
                        });
                    }
                });
        }
        
        function updateScreenshot() {
            fetch('/api/screenshot')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('screenshotContainer');
                    if (data.screenshot) {
                        container.innerHTML = `<img src="data:image/png;base64,${data.screenshot}" alt="Screenshot">`;
                    }
                });
        }
        
        function startAgent() {
            const form = document.getElementById('configForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            data.highlight_mouse = document.getElementById('highlight_mouse').checked;
            
            fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    addLog('Agente iniciado', 'info');
                    updateStatus();
                } else {
                    addLog('Erro: ' + data.error, 'error');
                }
            });
        }
        
        function stopAgent() {
            fetch('/api/stop', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    addLog('Solicitação de parada enviada', 'warning');
                    updateStatus();
                });
        }
        
        function clearLogs() {
            fetch('/api/clear_logs', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    document.getElementById('logs').innerHTML = '';
                    addLog('Logs limpos', 'info');
                });
        }
        
        // Atualizar status, logs e screenshot periodicamente
        updateInterval = setInterval(() => {
            updateStatus();
            updateLogs();
            updateScreenshot();
        }, 1000);
        
        // Atualizar ao carregar
        updateStatus();
        updateLogs();
        addLog('Interface carregada. Pronto para usar!', 'info');
    </script>
</body>
</html>
"""


class BrowserAgentWebWrapper(BrowserAgent):
    """Wrapper do BrowserAgent para interface web"""
    
    def __init__(self, browser_computer, query, model_name, state):
        super().__init__(browser_computer, query, model_name, verbose=False)
        self.state = state
        
    def handle_action(self, action):
        """Override para capturar screenshots"""
        result = super().handle_action(action)
        
        if isinstance(result, EnvState):
            # Adicionar screenshot à fila
            self.state['screenshot_queue'].put(result.screenshot)
            self.state['current_url'] = result.url
            self._log(f"Ação executada: {action.name}", "info")
            self._log(f"URL atual: {result.url}", "info")
        
        return result
        
    def _log(self, message, level="info"):
        """Adicionar log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'level': level
        }
        self.state['log_queue'].put(log_entry)
        self.state['logs'].append(log_entry)
        # Manter apenas os últimos 1000 logs
        if len(self.state['logs']) > 1000:
            self.state['logs'] = self.state['logs'][-1000:]
            
    def run_one_iteration(self):
        """Override para capturar logs"""
        from google.genai.types import FinishReason
        
        try:
            self._log("Gerando resposta do Gemini Computer Use...", "info")
            response = self.get_model_response()
        except Exception as e:
            self._log(f"Erro ao gerar resposta: {e}", "error")
            return "COMPLETE"
            
        if not response.candidates:
            self._log("Resposta sem candidatos!", "error")
            return "COMPLETE"
            
        candidate = response.candidates[0]
        if candidate.content:
            self._contents.append(candidate.content)
            
        reasoning = self.get_text(candidate)
        function_calls = self.extract_function_calls(candidate)
        
        if (
            not function_calls
            and not reasoning
            and candidate.finish_reason == FinishReason.MALFORMED_FUNCTION_CALL
        ):
            return "CONTINUE"
            
        if not function_calls:
            self._log(f"Loop do agente concluído: {reasoning}", "info")
            self.final_reasoning = reasoning
            return "COMPLETE"
            
        # Log das chamadas de função
        for function_call in function_calls:
            call_info = f"Função: {function_call.name}"
            if function_call.args:
                args_str = str(function_call.args)
                if len(args_str) > 100:
                    args_str = args_str[:100] + "..."
                call_info += f" | Args: {args_str}"
            self._log(call_info, "info")
            
        if reasoning:
            self._log(f"Raciocínio: {reasoning}", "info")
                
        # Processar chamadas de função
        function_responses = []
        for function_call in function_calls:
            extra_fr_fields = {}
            if function_call.args and (
                safety := function_call.args.get("safety_decision")
            ):
                decision = self._get_safety_confirmation(safety)
                if decision == "TERMINATE":
                    self._log("Loop do agente terminado pelo usuário", "warning")
                    return "COMPLETE"
                extra_fr_fields["safety_acknowledgement"] = "true"
                
            self._log(f"Executando: {function_call.name}...", "info")
            fc_result = self.handle_action(function_call)
            
            if isinstance(fc_result, EnvState):
                from google.genai.types import FunctionResponse, FunctionResponsePart, FunctionResponseBlob
                function_responses.append(
                    FunctionResponse(
                        name=function_call.name,
                        response={
                            "url": fc_result.url,
                            **extra_fr_fields,
                        },
                        parts=[
                            FunctionResponsePart(
                                inline_data=FunctionResponseBlob(
                                    mime_type="image/png", data=fc_result.screenshot
                                )
                            )
                        ],
                    )
                )
            elif isinstance(fc_result, dict):
                from google.genai.types import FunctionResponse
                function_responses.append(
                    FunctionResponse(name=function_call.name, response=fc_result)
                )
                
        from google.genai.types import Content, Part
        self._contents.append(
            Content(
                role="user",
                parts=[Part(function_response=fr) for fr in function_responses],
            )
        )
        
        # Limpar screenshots antigas
        from agent import MAX_RECENT_TURN_WITH_SCREENSHOTS, PREDEFINED_COMPUTER_USE_FUNCTIONS
        turn_with_screenshots_found = 0
        for content in reversed(self._contents):
            if content.role == "user" and content.parts:
                has_screenshot = False
                for part in content.parts:
                    if (
                        part.function_response
                        and part.function_response.parts
                        and part.function_response.name
                        in PREDEFINED_COMPUTER_USE_FUNCTIONS
                    ):
                        has_screenshot = True
                        break
                        
                if has_screenshot:
                    turn_with_screenshots_found += 1
                    if turn_with_screenshots_found > MAX_RECENT_TURN_WITH_SCREENSHOTS:
                        for part in content.parts:
                            if (
                                part.function_response
                                and part.function_response.parts
                                and part.function_response.name
                                in PREDEFINED_COMPUTER_USE_FUNCTIONS
                            ):
                                part.function_response.parts = None
                                
        return "CONTINUE"
        
    def _get_safety_confirmation(self, safety):
        """Override - sempre continuar na interface web"""
        if safety["decision"] != "require_confirmation":
            raise ValueError(f"Decisão de segurança desconhecida: {safety['decision']}")
            
        self._log("Serviço de segurança requer confirmação - continuando automaticamente", "warning")
        return "CONTINUE"


def run_agent_thread(config, state):
    """Executa o agente em uma thread separada"""
    try:
        state['is_running'] = True
        state['status'] = 'Executando...'
        
        env_name = config.get('env', 'playwright')
        initial_url = config.get('initial_url', 'https://www.google.com')
        highlight_mouse = config.get('highlight_mouse', False)
        model_name = config.get('model', 'gemini-2.5-computer-use-preview-10-2025')
        query = config.get('query', '')
        
        # Criar ambiente
        if env_name == "playwright":
            env = PlaywrightComputer(
                screen_size=PLAYWRIGHT_SCREEN_SIZE,
                initial_url=initial_url,
                highlight_mouse=highlight_mouse,
            )
        elif env_name == "browserbase":
            env = BrowserbaseComputer(
                screen_size=PLAYWRIGHT_SCREEN_SIZE,
                initial_url=initial_url
            )
        else:
            raise ValueError(f"Ambiente desconhecido: {env_name}")
        
        # Criar agente
        with env as browser_computer:
            agent = BrowserAgentWebWrapper(
                browser_computer=browser_computer,
                query=query,
                model_name=model_name,
                state=state
            )
            agent.agent_loop()
            
        state['status'] = 'Concluído'
        state['is_running'] = False
        
    except Exception as e:
        state['status'] = f'Erro: {str(e)}'
        state['is_running'] = False
        import traceback
        state['log_queue'].put({
            'timestamp': time.strftime("%H:%M:%S"),
            'message': f"Erro: {str(e)}\n{traceback.format_exc()}",
            'level': 'error'
        })


@app.route('/')
def index():
    """Página principal"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/status', methods=['GET'])
def get_status():
    """Obter status atual"""
    # Processar fila de screenshots
    try:
        while True:
            screenshot = agent_state['screenshot_queue'].get_nowait()
            agent_state['latest_screenshot'] = screenshot
    except queue.Empty:
        pass
    
    return jsonify({
        'is_running': agent_state['is_running'],
        'status': agent_state['status'],
        'current_url': agent_state.get('current_url')
    })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Obter logs"""
    # Processar fila de logs
    try:
        while True:
            log_entry = agent_state['log_queue'].get_nowait()
            agent_state['logs'].append(log_entry)
            if len(agent_state['logs']) > 1000:
                agent_state['logs'] = agent_state['logs'][-1000:]
    except queue.Empty:
        pass
    
    return jsonify({'logs': agent_state['logs']})


@app.route('/api/screenshot', methods=['GET'])
def get_screenshot():
    """Obter screenshot atual"""
    screenshot = agent_state.get('latest_screenshot')
    if screenshot:
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        return jsonify({'screenshot': screenshot_b64})
    return jsonify({'screenshot': None})


@app.route('/api/start', methods=['POST'])
def start_agent():
    """Iniciar agente"""
    if agent_state['is_running']:
        return jsonify({'success': False, 'error': 'Agente já está em execução'})
    
    config = request.json
    if not config.get('query'):
        return jsonify({'success': False, 'error': 'Query é obrigatória'})
    
    # Limpar estado anterior
    agent_state['logs'] = []
    agent_state['latest_screenshot'] = None
    agent_state['current_url'] = None
    
    # Iniciar thread
    thread = threading.Thread(
        target=run_agent_thread,
        args=(config, agent_state),
        daemon=True
    )
    thread.start()
    agent_state['agent_thread'] = thread
    
    return jsonify({'success': True})


@app.route('/api/stop', methods=['POST'])
def stop_agent():
    """Parar agente"""
    agent_state['is_running'] = False
    agent_state['status'] = 'Parando...'
    return jsonify({'success': True})


@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    """Limpar logs"""
    agent_state['logs'] = []
    return jsonify({'success': True})


if __name__ == '__main__':
    import sys
    # Permitir especificar porta via argumento ou usar 8080 como padrão
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    
    print("=" * 60)
    print("Gemini Computer Use - Interface Web")
    print("=" * 60)
    print(f"Acesse em: http://localhost:{port}")
    print("Pressione Ctrl+C para parar o servidor")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)

