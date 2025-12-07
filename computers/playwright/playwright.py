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
import logging
import termcolor
import time
import os
import sys
from ..computer import (
    Computer,
    EnvState,
)
import playwright.sync_api
from playwright.sync_api import sync_playwright
from typing import Literal

# Importar logger configurado
try:
    from logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback se logger_config não estiver disponível
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

# Define a mapping from the user-friendly key names to Playwright's expected key names.
# Playwright is generally good with case-insensitivity for these, but it's best to be canonical.
# See: https://playwright.dev/docs/api/class-keyboard#keyboard-press
# Keys like 'a', 'b', '1', '$' are passed directly.
PLAYWRIGHT_KEY_MAP = {
    "backspace": "Backspace",
    "tab": "Tab",
    "return": "Enter",  # Playwright uses 'Enter'
    "enter": "Enter",
    "shift": "Shift",
    "control": "ControlOrMeta",
    "alt": "Alt",
    "escape": "Escape",
    "space": "Space",  # Can also just be " "
    "pageup": "PageUp",
    "pagedown": "PageDown",
    "end": "End",
    "home": "Home",
    "left": "ArrowLeft",
    "up": "ArrowUp",
    "right": "ArrowRight",
    "down": "ArrowDown",
    "insert": "Insert",
    "delete": "Delete",
    "semicolon": ";",  # For actual character ';'
    "equals": "=",  # For actual character '='
    "multiply": "Multiply",  # NumpadMultiply
    "add": "Add",  # NumpadAdd
    "separator": "Separator",  # Numpad specific
    "subtract": "Subtract",  # NumpadSubtract, or just '-' for character
    "decimal": "Decimal",  # NumpadDecimal, or just '.' for character
    "divide": "Divide",  # NumpadDivide, or just '/' for character
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
    "command": "Meta",  # 'Meta' is Command on macOS, Windows key on Windows
}


class PlaywrightComputer(Computer):
    """Connects to a local Playwright instance."""

    def __init__(
        self,
        screen_size: tuple[int, int],
        initial_url: str = "https://www.google.com",
        search_engine_url: str = "https://www.google.com",
        highlight_mouse: bool = False,
    ):
        logger.info(f"Inicializando PlaywrightComputer")
        logger.debug(f"Screen size: {screen_size}")
        logger.debug(f"URL inicial: {initial_url}")
        logger.debug(f"Highlight mouse: {highlight_mouse}")
        
        self._initial_url = initial_url
        self._screen_size = screen_size
        self._search_engine_url = search_engine_url
        self._highlight_mouse = highlight_mouse

    def _handle_new_page(self, new_page: playwright.sync_api.Page):
        """The Computer Use model only supports a single tab at the moment.

        Some websites, however, try to open links in a new tab.
        For those situations, we intercept the page-opening behavior, and instead overwrite the current page.
        """
        new_url = new_page.url
        new_page.close()
        self._page.goto(new_url)

    def __enter__(self):
        logger.info("Criando sessão do Playwright...")
        start_time = time.time()
        
        logger.debug("Iniciando Playwright...")
        self._playwright = sync_playwright().start()
        logger.debug("Playwright iniciado")
        
        headless = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() in ("true", "1", "yes")
        logger.info(f"Lançando navegador Chromium (headless={headless})...")
        
        self._browser = self._playwright.chromium.launch(
            args=[
                "--disable-extensions",
                "--disable-file-system",
                "--disable-plugins",
                "--disable-dev-shm-usage",
                "--disable-background-networking",
                "--disable-default-apps",
                "--disable-sync",
                # No '--no-sandbox' arg means the sandbox is on.
            ],
            headless=headless,
        )
        logger.info("Navegador Chromium lançado com sucesso")
        
        logger.debug(f"Criando contexto do navegador com viewport: {self._screen_size}")
        self._context = self._browser.new_context(
            viewport={
                "width": self._screen_size[0],
                "height": self._screen_size[1],
            }
        )
        logger.debug("Contexto criado")
        
        logger.debug("Criando nova página...")
        self._page = self._context.new_page()
        logger.debug("Página criada")
        
        logger.info(f"Navegando para URL inicial: {self._initial_url}")
        self._page.goto(self._initial_url)
        logger.info(f"Página carregada: {self._page.url}")

        self._context.on("page", self._handle_new_page)
        logger.debug("Handler de novas páginas configurado")

        elapsed = time.time() - start_time
        logger.info(f"Sessão do Playwright criada em {elapsed:.2f}s")
        
        termcolor.cprint(
            f"Started local playwright.",
            color="green",
            attrs=["bold"],
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Encerrando sessão do Playwright...")
        
        if exc_type:
            logger.warning(f"Exceção detectada no contexto: {exc_type.__name__}: {exc_val}")
        
        if self._context:
            logger.debug("Fechando contexto do navegador...")
            self._context.close()
            logger.debug("Contexto fechado")
            
        try:
            logger.debug("Fechando navegador...")
            self._browser.close()
            logger.debug("Navegador fechado")
        except Exception as e:
            # Browser was already shut down because of SIGINT or such.
            if "Browser.close: Connection closed while reading from the driver" in str(e):
                logger.debug("Navegador já estava fechado")
                pass
            else:
                logger.error(f"Erro ao fechar navegador: {e}")
                raise

        logger.debug("Parando Playwright...")
        self._playwright.stop()
        logger.info("Sessão do Playwright encerrada")

    def open_web_browser(self) -> EnvState:
        return self.current_state()

    def click_at(self, x: int, y: int):
        logger.debug(f"Clique em coordenadas: ({x}, {y})")
        self.highlight_mouse(x, y)
        self._page.mouse.click(x, y)
        logger.debug("Aguardando estado de carregamento...")
        self._page.wait_for_load_state()
        logger.debug("Estado de carregamento alcançado")
        return self.current_state()

    def hover_at(self, x: int, y: int):
        self.highlight_mouse(x, y)
        self._page.mouse.move(x, y)
        self._page.wait_for_load_state()
        return self.current_state()

    def type_text_at(
        self,
        x: int,
        y: int,
        text: str,
        press_enter: bool = False,
        clear_before_typing: bool = True,
    ) -> EnvState:
        self.highlight_mouse(x, y)
        self._page.mouse.click(x, y)
        self._page.wait_for_load_state()

        if clear_before_typing:
            if sys.platform == "darwin":
                self.key_combination(["Command", "A"])
            else:
                self.key_combination(["Control", "A"])
            self.key_combination(["Delete"])

        self._page.keyboard.type(text)
        self._page.wait_for_load_state()

        if press_enter:
            self.key_combination(["Enter"])
        self._page.wait_for_load_state()
        return self.current_state()

    def _horizontal_document_scroll(
        self, direction: Literal["left", "right"]
    ) -> EnvState:
        # Scroll by 50% of the viewport size.
        horizontal_scroll_amount = self.screen_size()[0] // 2
        if direction == "left":
            sign = "-"
        else:
            sign = ""
        scroll_argument = f"{sign}{horizontal_scroll_amount}"
        # Scroll using JS.
        self._page.evaluate(f"window.scrollBy({scroll_argument}, 0); ")
        self._page.wait_for_load_state()
        return self.current_state()

    def scroll_document(
        self, direction: Literal["up", "down", "left", "right"]
    ) -> EnvState:
        if direction == "down":
            return self.key_combination(["PageDown"])
        elif direction == "up":
            return self.key_combination(["PageUp"])
        elif direction in ("left", "right"):
            return self._horizontal_document_scroll(direction)
        else:
            raise ValueError("Unsupported direction: ", direction)

    def scroll_at(
        self,
        x: int,
        y: int,
        direction: Literal["up", "down", "left", "right"],
        magnitude: int = 800,
    ) -> EnvState:
        self.highlight_mouse(x, y)

        self._page.mouse.move(x, y)
        self._page.wait_for_load_state()

        dx = 0
        dy = 0
        if direction == "up":
            dy = -magnitude
        elif direction == "down":
            dy = magnitude
        elif direction == "left":
            dx = -magnitude
        elif direction == "right":
            dx = magnitude
        else:
            raise ValueError("Unsupported direction: ", direction)

        self._page.mouse.wheel(dx, dy)
        self._page.wait_for_load_state()
        return self.current_state()

    def wait_5_seconds(self) -> EnvState:
        time.sleep(5)
        return self.current_state()

    def go_back(self) -> EnvState:
        self._page.go_back()
        self._page.wait_for_load_state()
        return self.current_state()

    def go_forward(self) -> EnvState:
        self._page.go_forward()
        self._page.wait_for_load_state()
        return self.current_state()

    def search(self) -> EnvState:
        return self.navigate(self._search_engine_url)

    def navigate(self, url: str) -> EnvState:
        logger.info(f"Navegando para URL: {url}")
        normalized_url = url
        if not normalized_url.startswith(("http://", "https://")):
            normalized_url = "https://" + normalized_url
            logger.debug(f"URL normalizada: {normalized_url}")
        
        start_time = time.time()
        self._page.goto(normalized_url)
        elapsed = time.time() - start_time
        logger.info(f"Navegação concluída em {elapsed:.2f}s")
        
        logger.debug("Aguardando estado de carregamento...")
        self._page.wait_for_load_state()
        logger.debug(f"URL atual após navegação: {self._page.url}")
        return self.current_state()

    def key_combination(self, keys: list[str]) -> EnvState:
        # Normalize all keys to the Playwright compatible version.
        keys = [PLAYWRIGHT_KEY_MAP.get(k.lower(), k) for k in keys]

        for key in keys[:-1]:
            self._page.keyboard.down(key)

        self._page.keyboard.press(keys[-1])

        for key in reversed(keys[:-1]):
            self._page.keyboard.up(key)

        return self.current_state()

    def drag_and_drop(
        self, x: int, y: int, destination_x: int, destination_y: int
    ) -> EnvState:
        self.highlight_mouse(x, y)
        self._page.mouse.move(x, y)
        self._page.wait_for_load_state()
        self._page.mouse.down()
        self._page.wait_for_load_state()

        self.highlight_mouse(destination_x, destination_y)
        self._page.mouse.move(destination_x, destination_y)
        self._page.wait_for_load_state()
        self._page.mouse.up()
        return self.current_state()

    def current_state(self) -> EnvState:
        logger.debug("Obtendo estado atual da página...")
        self._page.wait_for_load_state()
        # Even if Playwright reports the page as loaded, it may not be so.
        # Add a manual sleep to make sure the page has finished rendering.
        time.sleep(0.5)
        
        screenshot_start = time.time()
        screenshot_bytes = self._page.screenshot(type="png", full_page=False)
        screenshot_time = time.time() - screenshot_start
        
        current_url = self._page.url
        logger.debug(f"Screenshot capturada em {screenshot_time:.2f}s ({len(screenshot_bytes)} bytes)")
        logger.debug(f"URL atual: {current_url}")
        
        return EnvState(screenshot=screenshot_bytes, url=current_url)

    def screen_size(self) -> tuple[int, int]:
        viewport_size = self._page.viewport_size
        # If available, try to take the local playwright viewport size.
        if viewport_size:
            return viewport_size["width"], viewport_size["height"]
        # If unavailable, fall back to the original provided size.
        return self._screen_size

    def highlight_mouse(self, x: int, y: int):
        if not self._highlight_mouse:
            return
        self._page.evaluate(
            f"""
        () => {{
            const element_id = "playwright-feedback-circle";
            const div = document.createElement('div');
            div.id = element_id;
            div.style.pointerEvents = 'none';
            div.style.border = '4px solid red';
            div.style.borderRadius = '50%';
            div.style.width = '20px';
            div.style.height = '20px';
            div.style.position = 'fixed';
            div.style.zIndex = '9999';
            document.body.appendChild(div);

            div.hidden = false;
            div.style.left = {x} - 10 + 'px';
            div.style.top = {y} - 10 + 'px';

            setTimeout(() => {{
                div.hidden = true;
            }}, 2000);
        }}
    """
        )
        # Wait a bit for the user to see the cursor.
        time.sleep(1)
