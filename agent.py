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
import os
import logging
from typing import Literal, Optional, Union, Any
from google import genai
from google.genai import types
import termcolor
from google.genai.types import (
    Part,
    GenerateContentConfig,
    Content,
    Candidate,
    FunctionResponse,
    FinishReason,
)
import time
from rich.console import Console
from rich.table import Table

from computers import EnvState, Computer
from logger_config import get_logger

logger = get_logger(__name__)

MAX_RECENT_TURN_WITH_SCREENSHOTS = 3
PREDEFINED_COMPUTER_USE_FUNCTIONS = [
    "open_web_browser",
    "click_at",
    "hover_at",
    "type_text_at",
    "scroll_document",
    "scroll_at",
    "wait_5_seconds",
    "go_back",
    "go_forward",
    "search",
    "navigate",
    "key_combination",
    "drag_and_drop",
]


console = Console()

# Built-in Computer Use tools will return "EnvState".
# Custom provided functions will return "dict".
FunctionResponseT = Union[EnvState, dict]


def multiply_numbers(x: float, y: float) -> dict:
    """Multiplies two numbers."""
    return {"result": x * y}


class BrowserAgent:
    def __init__(
        self,
        browser_computer: Computer,
        query: str,
        model_name: str,
        verbose: bool = True,
    ):
        logger.info(f"Inicializando BrowserAgent com modelo: {model_name}")
        logger.debug(f"Query: {query[:100]}..." if len(query) > 100 else f"Query: {query}")
        logger.debug(f"Verbose: {verbose}")
        
        self._browser_computer = browser_computer
        self._query = query
        self._model_name = model_name
        self._verbose = verbose
        self.final_reasoning = None
        use_vertexai = os.environ.get("USE_VERTEXAI", "0").lower() in ["true", "1"]
        
        logger.info(f"Configurando cliente Gemini - VertexAI: {use_vertexai}")
        
        if use_vertexai:
            # Usar Vertex AI
            project = os.environ.get("VERTEXAI_PROJECT")
            location = os.environ.get("VERTEXAI_LOCATION")
            logger.info(f"Usando Vertex AI - Project: {project}, Location: {location}")
            self._client = genai.Client(
                vertexai=True,
                project=project,
                location=location,
            )
        else:
            # Usar API Key
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                logger.info("Usando API Key do Gemini")
                logger.debug(f"API Key (primeiros 10 chars): {api_key[:10]}...")
            else:
                logger.warning("GEMINI_API_KEY não encontrada!")
            self._client = genai.Client(
                api_key=api_key,
            )
        self._contents: list[Content] = [
            Content(
                role="user",
                parts=[
                    Part(text=self._query),
                ],
            )
        ]

        # Exclude any predefined functions here.
        excluded_predefined_functions = []

        # Add your own custom functions here.
        custom_functions = [
            # For example:
            types.FunctionDeclaration.from_callable(
                client=self._client, callable=multiply_numbers
            )
        ]

        # Computer Use está SEMPRE ativo - é obrigatório para este agente
        computer_use_tool = types.Tool(
            computer_use=types.ComputerUse(
                environment=types.Environment.ENVIRONMENT_BROWSER,
                excluded_predefined_functions=excluded_predefined_functions,
            ),
        )
        
        logger.info("=" * 60)
        logger.info("🖥️  COMPUTER USE CONFIGURADO E ATIVO")
        logger.info("=" * 60)
        logger.info(f"Ambiente: ENVIRONMENT_BROWSER")
        logger.info(f"Funções excluídas: {len(excluded_predefined_functions)}")
        logger.info(f"Funções disponíveis: {len(PREDEFINED_COMPUTER_USE_FUNCTIONS)}")
        logger.info(f"Funções customizadas: {len(custom_functions)}")
        logger.info("=" * 60)
        
        self._generate_content_config = GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            tools=[
                computer_use_tool,  # Computer Use sempre presente
                types.Tool(function_declarations=custom_functions),
            ],
        )

    def handle_action(self, action: types.FunctionCall) -> FunctionResponseT:
        """Handles the action and returns the environment state."""
        logger.info(f"Executando ação: {action.name}")
        logger.debug(f"Argumentos da ação {action.name}: {action.args}")
        
        start_time = time.time()
        result = None
        
        try:
            if action.name == "open_web_browser":
                logger.debug("Abrindo navegador web")
                result = self._browser_computer.open_web_browser()
                
            elif action.name == "click_at":
                x = self.denormalize_x(action.args["x"])
                y = self.denormalize_y(action.args["y"])
                logger.debug(f"Clique em coordenadas: ({x}, {y})")
                result = self._browser_computer.click_at(x=x, y=y)
                
            elif action.name == "hover_at":
                x = self.denormalize_x(action.args["x"])
                y = self.denormalize_y(action.args["y"])
                logger.debug(f"Hover em coordenadas: ({x}, {y})")
                result = self._browser_computer.hover_at(x=x, y=y)
                
            elif action.name == "type_text_at":
                x = self.denormalize_x(action.args["x"])
                y = self.denormalize_y(action.args["y"])
                text = action.args["text"]
                press_enter = action.args.get("press_enter", False)
                clear_before_typing = action.args.get("clear_before_typing", True)
                logger.debug(f"Digitando texto em ({x}, {y}): '{text[:50]}...' (press_enter={press_enter}, clear={clear_before_typing})")
                result = self._browser_computer.type_text_at(
                    x=x, y=y, text=text, press_enter=press_enter, clear_before_typing=clear_before_typing
                )
                
            elif action.name == "scroll_document":
                direction = action.args["direction"]
                logger.debug(f"Rolando documento: {direction}")
                result = self._browser_computer.scroll_document(direction)
                
            elif action.name == "scroll_at":
                x = self.denormalize_x(action.args["x"])
                y = self.denormalize_y(action.args["y"])
                magnitude = action.args.get("magnitude", 800)
                direction = action.args["direction"]
                logger.debug(f"Rolando em ({x}, {y}) direção {direction}, magnitude {magnitude}")

                if direction in ("up", "down"):
                    magnitude = self.denormalize_y(magnitude)
                elif direction in ("left", "right"):
                    magnitude = self.denormalize_x(magnitude)
                else:
                    raise ValueError("Unknown direction: ", direction)
                result = self._browser_computer.scroll_at(x=x, y=y, direction=direction, magnitude=magnitude)
                
            elif action.name == "wait_5_seconds":
                logger.debug("Aguardando 5 segundos")
                result = self._browser_computer.wait_5_seconds()
                
            elif action.name == "go_back":
                logger.debug("Navegando para página anterior")
                result = self._browser_computer.go_back()
                
            elif action.name == "go_forward":
                logger.debug("Navegando para próxima página")
                result = self._browser_computer.go_forward()
                
            elif action.name == "search":
                logger.debug("Navegando para página de busca")
                result = self._browser_computer.search()
                
            elif action.name == "navigate":
                url = action.args["url"]
                logger.info(f"Navegando para URL: {url}")
                result = self._browser_computer.navigate(url)
                
            elif action.name == "key_combination":
                keys = action.args["keys"].split("+")
                logger.debug(f"Pressionando combinação de teclas: {keys}")
                result = self._browser_computer.key_combination(keys)
                
            elif action.name == "drag_and_drop":
                x = self.denormalize_x(action.args["x"])
                y = self.denormalize_y(action.args["y"])
                destination_x = self.denormalize_x(action.args["destination_x"])
                destination_y = self.denormalize_y(action.args["destination_y"])
                logger.debug(f"Drag and drop de ({x}, {y}) para ({destination_x}, {destination_y})")
                result = self._browser_computer.drag_and_drop(
                    x=x, y=y, destination_x=destination_x, destination_y=destination_y
                )
                
            # Handle the custom function declarations here.
            elif action.name == multiply_numbers.__name__:
                x = action.args["x"]
                y = action.args["y"]
                logger.debug(f"Multiplicando números: {x} * {y}")
                result = multiply_numbers(x=x, y=y)
                
            else:
                error_msg = f"Função não suportada: {action.name}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Ação {action.name} concluída em {elapsed_time:.2f}s")
            
            if isinstance(result, EnvState):
                logger.debug(f"Estado do ambiente - URL: {result.url}, Screenshot size: {len(result.screenshot)} bytes")
            elif isinstance(result, dict):
                logger.debug(f"Resultado customizado: {result}")
            
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Erro ao executar ação {action.name} após {elapsed_time:.2f}s: {str(e)}", exc_info=True)
            raise

    def get_model_response(
        self, max_retries=5, base_delay_s=1
    ) -> types.GenerateContentResponse:
        logger.info(f"Solicitando resposta do modelo {self._model_name}")
        logger.debug(f"Tamanho do histórico de conteúdo: {len(self._contents)} mensagens")
        
        # Log detalhado do conteúdo sendo enviado
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Conteúdo sendo enviado:")
            for idx, content in enumerate(self._contents[-3:], 1):  # Últimas 3 mensagens
                logger.debug(f"  Mensagem {idx}: role={content.role}, parts={len(content.parts) if content.parts else 0}")
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Tentativa {attempt + 1}/{max_retries} de gerar conteúdo")
                logger.debug("🖥️  Computer Use está ativo na configuração")
                start_time = time.time()
                
                # Computer Use está sempre incluído no config através de self._generate_content_config
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=self._contents,
                    config=self._generate_content_config,  # Computer Use sempre presente aqui
                )
                
                elapsed_time = time.time() - start_time
                logger.info(f"Resposta recebida do modelo em {elapsed_time:.2f}s")
                
                # Verificar resposta detalhadamente
                if response.candidates:
                    logger.debug(f"Número de candidatos na resposta: {len(response.candidates)}")
                    candidate = response.candidates[0]
                    logger.debug(f"Finish reason: {candidate.finish_reason}")
                    
                    # Log de feedback se disponível
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        feedback = response.prompt_feedback
                        logger.debug(f"Prompt feedback: {feedback}")
                        if hasattr(feedback, 'block_reason') and feedback.block_reason:
                            logger.warning(f"⚠️  Bloqueio detectado: {feedback.block_reason}")
                    
                    # Log de uso
                    if hasattr(response, 'usage_metadata') and response.usage_metadata:
                        usage = response.usage_metadata
                        logger.debug(f"Usage metadata: {usage}")
                        if hasattr(usage, 'prompt_token_count'):
                            logger.debug(f"Tokens usados - Prompt: {usage.prompt_token_count}, "
                                       f"Candidates: {getattr(usage, 'candidates_token_count', 'N/A')}")
                else:
                    logger.warning("⚠️  Resposta recebida mas sem candidatos!")
                    # Tentar obter informações sobre o erro
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        feedback = response.prompt_feedback
                        logger.error(f"Prompt feedback: {feedback}")
                        if hasattr(feedback, 'block_reason') and feedback.block_reason:
                            logger.error(f"🚫 BLOQUEIO: {feedback.block_reason}")
                    if hasattr(response, 'usage_metadata') and response.usage_metadata:
                        logger.error(f"Usage metadata: {response.usage_metadata}")
                
                return response  # Return response on success
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                logger.warning(f"Erro ao gerar conteúdo (tentativa {attempt + 1}/{max_retries}): {error_type}: {error_msg}")
                
                # Log detalhado do erro
                if logger.isEnabledFor(logging.DEBUG):
                    import traceback
                    logger.debug(f"Traceback completo:\n{traceback.format_exc()}")
                
                # Verificar se é erro de API key
                if "API key" in error_msg or "authentication" in error_msg.lower():
                    logger.error("ERRO DE AUTENTICAÇÃO: Verifique sua API key!")
                    raise
                
                # Verificar se é rate limit
                if "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                    logger.error("RATE LIMIT ou QUOTA: Aguarde antes de tentar novamente")
                
                if attempt < max_retries - 1:
                    delay = base_delay_s * (2**attempt)
                    logger.info(f"Tentando novamente em {delay} segundos...")
                    termcolor.cprint(
                        f"Generating content failed on attempt {attempt + 1}. "
                        f"Retrying in {delay} seconds...\n",
                        color="yellow",
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"Falha ao gerar conteúdo após {max_retries} tentativas")
                    logger.error(f"Último erro: {error_type}: {error_msg}")
                    termcolor.cprint(
                        f"Generating content failed after {max_retries} attempts.\n",
                        color="red",
                    )
                    raise

    def get_text(self, candidate: Candidate) -> Optional[str]:
        """Extracts the text from the candidate."""
        if not candidate.content or not candidate.content.parts:
            return None
        text = []
        for part in candidate.content.parts:
            if part.text:
                text.append(part.text)
        return " ".join(text) or None

    def extract_function_calls(self, candidate: Candidate) -> list[types.FunctionCall]:
        """Extracts the function call from the candidate."""
        if not candidate.content or not candidate.content.parts:
            return []
        ret = []
        for part in candidate.content.parts:
            if part.function_call:
                ret.append(part.function_call)
        return ret

    def run_one_iteration(self) -> Literal["COMPLETE", "CONTINUE"]:
        logger.info("=" * 60)
        logger.info("Iniciando nova iteração do agente")
        logger.info("=" * 60)
        
        iteration_start = time.time()
        
        # Generate a response from the model.
        if self._verbose:
            with console.status(
                "Generating response from Gemini Computer Use...", spinner_style=None
            ):
                try:
                    response = self.get_model_response()
                except Exception as e:
                    logger.error(f"Erro ao obter resposta do modelo: {e}", exc_info=True)
                    return "COMPLETE"
        else:
            try:
                response = self.get_model_response()
            except Exception as e:
                logger.error(f"Erro ao obter resposta do modelo: {e}", exc_info=True)
                return "COMPLETE"

        if not response.candidates:
            logger.error("=" * 60)
            logger.error("ERRO: Resposta sem candidatos da API do Gemini!")
            logger.error("=" * 60)
            
            # Tentar obter mais informações sobre a resposta
            error_details = []
            is_safety_block = False
            block_reason = None
            block_message = None
            
            try:
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    feedback = response.prompt_feedback
                    logger.error(f"Prompt feedback: {feedback}")
                    error_details.append(f"Prompt feedback: {feedback}")
                    
                    # Verificar se há bloqueio de segurança
                    if hasattr(feedback, 'block_reason') and feedback.block_reason:
                        is_safety_block = True
                        block_reason = feedback.block_reason
                        block_message = getattr(feedback, 'block_reason_message', None)
                        
                        logger.error("=" * 60)
                        logger.error("🚫 BLOQUEIO DE SEGURANÇA DETECTADO")
                        logger.error("=" * 60)
                        logger.error(f"Razão do bloqueio: {block_reason}")
                        if block_message:
                            logger.error(f"Mensagem: {block_message}")
                        
                        # Verificar safety ratings se disponível
                        if hasattr(feedback, 'safety_ratings') and feedback.safety_ratings:
                            logger.error("Safety ratings:")
                            for rating in feedback.safety_ratings:
                                logger.error(f"  - {rating.category}: {rating.probability}")
                        
                        logger.error("\n💡 Soluções:")
                        logger.error("  1. Reformule a query de forma mais clara e específica")
                        logger.error("  2. Evite termos que possam ser interpretados como maliciosos")
                        logger.error("  3. Divida a tarefa em etapas menores")
                        logger.error("  4. Tente uma abordagem diferente para a mesma tarefa")
                        logger.error("=" * 60)
                
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    usage = response.usage_metadata
                    logger.error(f"Usage metadata: {usage}")
                    if hasattr(usage, 'prompt_token_count'):
                        logger.error(f"Tokens usados no prompt: {usage.prompt_token_count}")
                    error_details.append(f"Usage: {usage}")
                
                # Tentar obter informações de erro da resposta
                if hasattr(response, 'error'):
                    logger.error(f"Erro na resposta: {response.error}")
                    error_details.append(f"Erro: {response.error}")
                    
            except Exception as e:
                logger.error(f"Erro ao obter detalhes da resposta: {e}")
            
            if not is_safety_block:
                logger.error("\nPossíveis causas:")
                logger.error("  1. API Key inválida ou expirada")
                logger.error("  2. Rate limiting da API")
                logger.error("  3. Filtros de segurança bloqueando a resposta")
                logger.error("  4. Problemas com o modelo especificado")
                logger.error("  5. Quota excedida")
                logger.error("  6. Conteúdo bloqueado por políticas de segurança")
            
            logger.error("=" * 60)
            
            # Se for bloqueio de segurança, parar imediatamente
            if is_safety_block:
                logger.error("Bloqueio de segurança detectado - parando agente")
                logger.error("Por favor, reformule a query e tente novamente")
                return "COMPLETE"
            
            raise ValueError("Empty response - API retornou resposta sem candidatos")

        # Extract the text and function call from the response.
        candidate = response.candidates[0]
        logger.debug(f"Finish reason do candidato: {candidate.finish_reason}")
        
        # Append the model turn to conversation history.
        if candidate.content:
            self._contents.append(candidate.content)
            logger.debug("Conteúdo do candidato adicionado ao histórico")

        reasoning = self.get_text(candidate)
        function_calls = self.extract_function_calls(candidate)
        
        logger.info(f"Raciocínio extraído: {reasoning[:200]}..." if reasoning and len(reasoning) > 200 else f"Raciocínio: {reasoning}")
        logger.info(f"Chamadas de função encontradas: {len(function_calls)}")

        # Retry the request in case of malformed FCs.
        if (
            not function_calls
            and not reasoning
            and candidate.finish_reason == FinishReason.MALFORMED_FUNCTION_CALL
        ):
            return "CONTINUE"

        if not function_calls:
            logger.info("Nenhuma chamada de função - loop do agente concluído")
            logger.info(f"Raciocínio final: {reasoning}")
            print(f"Agent Loop Complete: {reasoning}")
            self.final_reasoning = reasoning
            iteration_time = time.time() - iteration_start
            logger.info(f"Iteração concluída em {iteration_time:.2f}s")
            return "COMPLETE"

        function_call_strs = []
        for idx, function_call in enumerate(function_calls, 1):
            logger.info(f"Função {idx}/{len(function_calls)}: {function_call.name}")
            # Print the function call and any reasoning.
            function_call_str = f"Name: {function_call.name}"
            if function_call.args:
                function_call_str += f"\nArgs:"
                for key, value in function_call.args.items():
                    function_call_str += f"\n  {key}: {value}"
                    # Log detalhado dos argumentos
                    if key in ['x', 'y', 'destination_x', 'destination_y']:
                        logger.debug(f"  {key}: {value} (normalizado)")
                    elif key == 'text':
                        logger.debug(f"  {key}: '{value[:50]}...' (truncado)" if len(str(value)) > 50 else f"  {key}: '{value}'")
                    else:
                        logger.debug(f"  {key}: {value}")
            function_call_strs.append(function_call_str)

        table = Table(expand=True)
        table.add_column(
            "Gemini Computer Use Reasoning", header_style="magenta", ratio=1
        )
        table.add_column("Function Call(s)", header_style="cyan", ratio=1)
        table.add_row(reasoning, "\n".join(function_call_strs))
        if self._verbose:
            console.print(table)
            print()

        function_responses = []
        for idx, function_call in enumerate(function_calls, 1):
            logger.info(f"Processando função {idx}/{len(function_calls)}: {function_call.name}")
            extra_fr_fields = {}
            
            if function_call.args and (
                safety := function_call.args.get("safety_decision")
            ):
                logger.warning("Decisão de segurança requerida!")
                logger.debug(f"Detalhes de segurança: {safety}")
                decision = self._get_safety_confirmation(safety)
                if decision == "TERMINATE":
                    logger.warning("Loop do agente terminado pelo usuário (decisão de segurança)")
                    print("Terminating agent loop")
                    return "COMPLETE"
                # Explicitly mark the safety check as acknowledged.
                extra_fr_fields["safety_acknowledgement"] = "true"
                logger.info("Decisão de segurança confirmada - continuando")
                
            if self._verbose:
                with console.status(
                    "Sending command to Computer...", spinner_style=None
                ):
                    fc_result = self.handle_action(function_call)
            else:
                fc_result = self.handle_action(function_call)
            if isinstance(fc_result, EnvState):
                logger.debug(f"Resposta da função {function_call.name}: EnvState com URL {fc_result.url}")
                logger.debug(f"Tamanho da screenshot: {len(fc_result.screenshot)} bytes")
                function_responses.append(
                    FunctionResponse(
                        name=function_call.name,
                        response={
                            "url": fc_result.url,
                            **extra_fr_fields,
                        },
                        parts=[
                            types.FunctionResponsePart(
                                inline_data=types.FunctionResponseBlob(
                                    mime_type="image/png", data=fc_result.screenshot
                                )
                            )
                        ],
                    )
                )
            elif isinstance(fc_result, dict):
                logger.debug(f"Resposta da função {function_call.name}: {fc_result}")
                function_responses.append(
                    FunctionResponse(name=function_call.name, response=fc_result)
                )

        self._contents.append(
            Content(
                role="user",
                parts=[Part(function_response=fr) for fr in function_responses],
            )
        )

        # only keep screenshots in the few most recent turns, remove the screenshot images from the old turns.
        turn_with_screenshots_found = 0
        for content in reversed(self._contents):
            if content.role == "user" and content.parts:
                # check if content has screenshot of the predefined computer use functions.
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
                    # remove the screenshot image if the number of screenshots exceed the limit.
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

    def _get_safety_confirmation(
        self, safety: dict[str, Any]
    ) -> Literal["CONTINUE", "TERMINATE"]:
        if safety["decision"] != "require_confirmation":
            raise ValueError(f"Unknown safety decision: safety['decision']")
        termcolor.cprint(
            "Safety service requires explicit confirmation!",
            color="yellow",
            attrs=["bold"],
        )
        print(safety["explanation"])
        decision = ""
        while decision.lower() not in ("y", "n", "ye", "yes", "no"):
            decision = input("Do you wish to proceed? [Yes]/[No]\n")
        if decision.lower() in ("n", "no"):
            return "TERMINATE"
        return "CONTINUE"

    def agent_loop(self):
        logger.info("=" * 60)
        logger.info("Iniciando loop do agente")
        logger.info(f"Query: {self._query}")
        logger.info(f"Modelo: {self._model_name}")
        logger.info("=" * 60)
        
        iteration_count = 0
        status = "CONTINUE"
        max_iterations = 50  # Limite de segurança para evitar loops infinitos
        
        while status == "CONTINUE":
            iteration_count += 1
            
            if iteration_count > max_iterations:
                logger.warning(f"Limite de {max_iterations} iterações atingido - finalizando loop")
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteração #{iteration_count}")
            logger.info(f"{'='*60}\n")
            
            status = self.run_one_iteration()
            
            if status == "CONTINUE":
                logger.info(f"Iteração #{iteration_count} concluída - continuando...")
            else:
                logger.info(f"Iteração #{iteration_count} concluída - finalizando loop")
        
        logger.info("=" * 60)
        logger.info(f"Loop do agente finalizado após {iteration_count} iterações")
        if self.final_reasoning:
            logger.info(f"Raciocínio final: {self.final_reasoning}")
        if hasattr(self, '_safety_block_count') and self._safety_block_count > 0:
            logger.warning(f"Total de bloqueios de segurança: {self._safety_block_count}")
        logger.info("=" * 60)

    def denormalize_x(self, x: int) -> int:
        return int(x / 1000 * self._browser_computer.screen_size()[0])

    def denormalize_y(self, y: int) -> int:
        return int(y / 1000 * self._browser_computer.screen_size()[1])
