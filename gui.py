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

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import os
import sys
from io import BytesIO
from PIL import Image, ImageTk
import time
import platform

# Configurações específicas para macOS
if platform.system() == "Darwin":
    # Configurar para usar o framework Python do macOS
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
    # Tentar usar o Python do sistema se disponível
    try:
        import tkinter
    except ImportError:
        print("Erro: tkinter não está disponível. Por favor, instale Python com suporte a tkinter.")
        sys.exit(1)

from agent import BrowserAgent
from computers import BrowserbaseComputer, PlaywrightComputer, EnvState

PLAYWRIGHT_SCREEN_SIZE = (1440, 900)


class BrowserAgentGUI:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Gemini Computer Use - Interface Gráfica")
            self.root.geometry("1200x800")
            
            # Configurações específicas para macOS
            if platform.system() == "Darwin":
                try:
                    # Tentar configurar o estilo nativo
                    style = ttk.Style()
                    style.theme_use('aqua')
                except:
                    pass  # Se não funcionar, usar o padrão
        except Exception as e:
            print(f"Erro ao inicializar a interface: {e}")
            raise
        
        # Variáveis de controle
        self.is_running = False
        self.agent_thread = None
        self.log_queue = queue.Queue()
        self.screenshot_queue = queue.Queue()
        
        # Variáveis de configuração
        self.env_var = tk.StringVar(value="playwright")
        self.query_var = tk.StringVar()
        self.initial_url_var = tk.StringVar(value="https://www.google.com")
        self.highlight_mouse_var = tk.BooleanVar(value=False)
        self.model_var = tk.StringVar(value="gemini-2.5-computer-use-preview-10-2025")
        
        self.setup_ui()
        self.check_log_queue()
        self.check_screenshot_queue()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Gemini Computer Use", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame de configuração
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Query
        ttk.Label(config_frame, text="Query:").grid(row=0, column=0, sticky=tk.W, pady=5)
        query_entry = ttk.Entry(config_frame, textvariable=self.query_var, width=60)
        query_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Ambiente
        ttk.Label(config_frame, text="Ambiente:").grid(row=1, column=0, sticky=tk.W, pady=5)
        env_combo = ttk.Combobox(
            config_frame, 
            textvariable=self.env_var, 
            values=("playwright", "browserbase"),
            state="readonly",
            width=57
        )
        env_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # URL Inicial
        ttk.Label(config_frame, text="URL Inicial:").grid(row=2, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(config_frame, textvariable=self.initial_url_var, width=60)
        url_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Modelo
        ttk.Label(config_frame, text="Modelo:").grid(row=3, column=0, sticky=tk.W, pady=5)
        model_entry = ttk.Entry(config_frame, textvariable=self.model_var, width=60)
        model_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Highlight Mouse
        highlight_check = ttk.Checkbutton(
            config_frame, 
            text="Destacar posição do mouse", 
            variable=self.highlight_mouse_var
        )
        highlight_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Botões de controle
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="▶ Iniciar", 
            command=self.start_agent,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="⏹ Parar", 
            command=self.stop_agent,
            state=tk.DISABLED,
            width=15
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(
            button_frame, 
            text="🗑 Limpar Logs", 
            command=self.clear_logs,
            width=15
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Frame de conteúdo (logs e screenshot)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Frame de logs
        log_frame = ttk.LabelFrame(content_frame, text="Logs", padding="10")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            width=50, 
            height=25,
            font=("Courier", 10)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.config(state=tk.DISABLED)
        
        # Frame de screenshot
        screenshot_frame = ttk.LabelFrame(content_frame, text="Screenshot", padding="10")
        screenshot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        screenshot_frame.columnconfigure(0, weight=1)
        screenshot_frame.rowconfigure(0, weight=1)
        
        self.screenshot_label = ttk.Label(
            screenshot_frame, 
            text="Nenhuma screenshot disponível",
            anchor=tk.CENTER
        )
        self.screenshot_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def log(self, message, level="INFO"):
        """Adiciona mensagem à fila de logs"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.log_queue.put(log_entry)
        
    def update_screenshot(self, screenshot_bytes):
        """Atualiza a screenshot na interface"""
        self.screenshot_queue.put(screenshot_bytes)
        
    def check_log_queue(self):
        """Verifica e processa mensagens da fila de logs"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_log_queue)
            
    def check_screenshot_queue(self):
        """Verifica e processa screenshots da fila"""
        try:
            while True:
                screenshot_bytes = self.screenshot_queue.get_nowait()
                self.display_screenshot(screenshot_bytes)
        except queue.Empty:
            pass
        finally:
            self.root.after(500, self.check_screenshot_queue)
            
    def display_screenshot(self, screenshot_bytes):
        """Exibe a screenshot na interface"""
        try:
            image = Image.open(BytesIO(screenshot_bytes))
            # Redimensionar para caber no frame (max 600x400)
            max_width, max_height = 600, 400
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.screenshot_label.config(image=photo, text="")
            self.screenshot_label.image = photo  # Manter referência
        except Exception as e:
            self.log(f"Erro ao exibir screenshot: {e}", "ERROR")
            
    def clear_logs(self):
        """Limpa os logs"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Logs limpos")
        
    def start_agent(self):
        """Inicia o agente em uma thread separada"""
        if self.is_running:
            messagebox.showwarning("Aviso", "O agente já está em execução!")
            return
            
        query = self.query_var.get().strip()
        if not query:
            messagebox.showerror("Erro", "Por favor, insira uma query!")
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Executando...")
        
        self.log(f"Iniciando agente com query: {query}")
        self.log(f"Ambiente: {self.env_var.get()}")
        self.log(f"URL inicial: {self.initial_url_var.get()}")
        self.log(f"Modelo: {self.model_var.get()}")
        
        # Iniciar thread do agente
        self.agent_thread = threading.Thread(
            target=self.run_agent,
            daemon=True
        )
        self.agent_thread.start()
        
    def stop_agent(self):
        """Para o agente"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.status_var.set("Parando...")
        self.log("Solicitação de parada recebida")
        # Nota: A parada real depende da implementação do agente
        
    def run_agent(self):
        """Executa o agente (chamado em thread separada)"""
        try:
            env_name = self.env_var.get()
            initial_url = self.initial_url_var.get()
            highlight_mouse = self.highlight_mouse_var.get()
            model_name = self.model_var.get()
            query = self.query_var.get()
            
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
            
            # Criar agente customizado para capturar logs e screenshots
            with env as browser_computer:
                agent = BrowserAgentGUIWrapper(
                    browser_computer=browser_computer,
                    query=query,
                    model_name=model_name,
                    gui=self
                )
                agent.agent_loop()
                
            self.log("Agente concluído com sucesso!")
            self.status_var.set("Concluído")
            
        except Exception as e:
            error_msg = f"Erro ao executar agente: {str(e)}"
            self.log(error_msg, "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            self.status_var.set(f"Erro: {str(e)}")
            messagebox.showerror("Erro", error_msg)
        finally:
            self.is_running = False
            self.root.after(0, self.reset_ui)
            
    def reset_ui(self):
        """Reseta a UI após o agente terminar"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if not self.is_running:
            self.status_var.set("Pronto")


class BrowserAgentGUIWrapper(BrowserAgent):
    """Wrapper do BrowserAgent para capturar logs e screenshots para a GUI"""
    
    def __init__(self, browser_computer, query, model_name, gui, verbose=False):
        super().__init__(browser_computer, query, model_name, verbose=verbose)
        self.gui = gui
        
    def handle_action(self, action):
        """Override para capturar screenshots"""
        result = super().handle_action(action)
        
        # Se o resultado contém screenshot, enviar para a GUI
        if hasattr(result, 'screenshot'):
            self.gui.update_screenshot(result.screenshot)
            self.gui.log(f"Ação executada: {action.name}")
            if hasattr(result, 'url'):
                self.gui.log(f"URL atual: {result.url}")
        
        return result
        
    def run_one_iteration(self):
        """Override para capturar logs - chama o método original e adiciona logs"""
        from google.genai.types import FinishReason
        
        # Gerar resposta
        try:
            self.gui.log("Gerando resposta do Gemini Computer Use...")
            response = self.get_model_response()
        except Exception as e:
            self.gui.log(f"Erro ao gerar resposta: {e}", "ERROR")
            return "COMPLETE"
            
        if not response.candidates:
            self.gui.log("Resposta sem candidatos!", "ERROR")
            return "COMPLETE"
            
        candidate = response.candidates[0]
        if candidate.content:
            self._contents.append(candidate.content)
            
        reasoning = self.get_text(candidate)
        function_calls = self.extract_function_calls(candidate)
        
        # Retry em caso de função malformada
        if (
            not function_calls
            and not reasoning
            and candidate.finish_reason == FinishReason.MALFORMED_FUNCTION_CALL
        ):
            return "CONTINUE"
            
        if not function_calls:
            self.gui.log(f"Loop do agente concluído: {reasoning}")
            self.final_reasoning = reasoning
            return "COMPLETE"
            
        # Log das chamadas de função
        for function_call in function_calls:
            call_info = f"Função: {function_call.name}"
            if function_call.args:
                # Simplificar args para log
                args_str = str(function_call.args)
                if len(args_str) > 100:
                    args_str = args_str[:100] + "..."
                call_info += f" | Args: {args_str}"
            self.gui.log(call_info)
            
        if reasoning:
            self.gui.log(f"Raciocínio: {reasoning}")
                
        # Processar chamadas de função (usar lógica do método original)
        function_responses = []
        for function_call in function_calls:
            extra_fr_fields = {}
            if function_call.args and (
                safety := function_call.args.get("safety_decision")
            ):
                decision = self._get_safety_confirmation(safety)
                if decision == "TERMINATE":
                    self.gui.log("Loop do agente terminado pelo usuário")
                    return "COMPLETE"
                extra_fr_fields["safety_acknowledgement"] = "true"
                
            self.gui.log(f"Executando: {function_call.name}...")
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
        
        # Limpar screenshots antigas (mesma lógica do original)
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
        """Override para usar GUI em vez de input do terminal"""
        import threading
        
        if safety["decision"] != "require_confirmation":
            raise ValueError(f"Decisão de segurança desconhecida: {safety['decision']}")
            
        self.gui.log("Serviço de segurança requer confirmação explícita!", "WARNING")
        self.gui.log(safety["explanation"], "WARNING")
        
        # Usar threading.Event para sincronizar
        result_event = threading.Event()
        result_value = [None]
        
        def show_dialog():
            try:
                result_value[0] = messagebox.askyesno(
                    "Confirmação de Segurança",
                    f"{safety['explanation']}\n\nDeseja prosseguir?"
                )
            except Exception as e:
                self.gui.log(f"Erro no diálogo: {e}", "ERROR")
                result_value[0] = False
            finally:
                result_event.set()
        
        # Executar dialog na thread principal
        self.gui.root.after(0, show_dialog)
        
        # Aguardar resposta (com timeout de 5 minutos)
        if result_event.wait(timeout=300):
            if result_value[0] is None:
                self.gui.log("Erro na confirmação de segurança", "ERROR")
                return "TERMINATE"
            if not result_value[0]:
                return "TERMINATE"
            return "CONTINUE"
        else:
            self.gui.log("Timeout na confirmação de segurança", "ERROR")
            return "TERMINATE"


def main():
    try:
        # Configurações específicas para macOS
        if platform.system() == "Darwin":
            # Configurar o estilo nativo do macOS
            root = tk.Tk()
            root.tk.call('tk', 'scaling', 1.0)
        else:
            root = tk.Tk()
        
        # Configurar a janela
        root.withdraw()  # Esconder temporariamente para evitar flash
        
        app = BrowserAgentGUI(root)
        
        # Mostrar a janela
        root.deiconify()
        
        # Focar na janela
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar a interface gráfica: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

