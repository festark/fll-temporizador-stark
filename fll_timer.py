import tkinter as tk
from tkinter import messagebox, font
import time
import threading
import urllib.request
import os
import sys
from PIL import Image, ImageTk
import winsound

# === FUNÇÃO PARA RECURSOS EMBUTIDOS ===
def resource_path(relative_path):
    """
    Retorna o caminho absoluto para recursos, funciona tanto no dev quanto no executável.
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# === CORES OFICIAIS FLL ===
CORES = {
    "fundo": "#f5f5f5",
    "azul_fll": "#005eb8",
    "amarelo_fll": "#ffb81c",
    "cinza": "#e0e0e0",
    "verde": "#4caf50",
    "laranja": "#ff9800",
    "vermelho": "#d32f2f",
    "texto": "#212121"
}

# === CHAVES DAS FASES (textos vão depender do idioma) ===
FASES_CHAVES = [
    ("fase1", 2 * 60),
    ("fase2", 5 * 60),
    ("fase3", 5 * 60),
    ("fase4", 5 * 60),
    ("fase5", 5 * 60),
    ("fase6", 8 * 60),
]

# Fases que precisam de avisos (1 min e 30 seg – apresentações)
FASES_COM_AVISOS_CHAVES = ["fase2", "fase4"]

# === TEXTOS POR IDIOMA ===
TEXTOS = {
    "pt": {
        "app_title": "FLL - Temporizador de Avaliação",
        "header_title": "FIRST® LEGO® LEAGUE",
        "subtitle": "Temporizador de Avaliação",
        "team_label": "Nome da Equipe:",
        "start_eval": "INICIAR AVALIAÇÃO",
        "team_warning_title": "Atenção",
        "team_warning_msg": "Digite o nome da equipe!",
        "total_time_label": "TEMPO TOTAL DA AVALIAÇÃO:",
        "btn_start": "INICIAR",
        "btn_pause": "PAUSAR",
        "btn_resume": "CONTINUAR",
        "btn_prev": "ANTERIOR",
        "btn_next": "PRÓXIMA",
        "phase_indicator": "Fase {atual} de {total}",
        "prev_phase_title": "Fase Anterior",
        "prev_phase_msg": "Voltando para:\n{fase}",
        "next_phase_title": "Avançar",
        "next_phase_msg": "Avançando para:\n{fase}",
        "general_time_over_title": "TEMPO TOTAL ESGOTADO",
        "general_time_over_msg": "Os 30 minutos gerais da avaliação terminaram!",
        "eval_done_title": "AVALIAÇÃO CONCLUÍDA",
        "eval_done_msg": "Equipe {equipe}\n\nTodas as fases foram concluídas!",
        "warning_title": "AVISO",
        "warning_1min": "{fase}\n\nFALTA 1 MINUTO!",
        "warning_30s": "{fase}\n\nFALTAM 30 SEGUNDOS!",
        "language_button": "PT / EN",

        # Fases (nomes exibidos)
        "fase1": "1 - SET UP E APRESENTAÇÕES",
        "fase2": "2 - APRESENTAÇÃO DO PROJETO DE INOVAÇÃO",
        "fase3": "3 - PERGUNTAS E RESPOSTAS DO PROJETO DE INOVAÇÃO",
        "fase4": "4 - APRESENTAÇÃO DO DESIGN DO ROBÔ",
        "fase5": "5 - PERGUNTAS E RESPOSTAS DO DESIGN DO ROBÔ",
        "fase6": "6 - FEEDBACK E CONSIDERAÇÕES FINAIS",
    },
    "en": {
        "app_title": "FLL - Evaluation Timer",
        "header_title": "FIRST® LEGO® LEAGUE",
        "subtitle": "Evaluation Timer",
        "team_label": "Team Name:",
        "start_eval": "START EVALUATION",
        "team_warning_title": "Warning",
        "team_warning_msg": "Please enter the team name!",
        "total_time_label": "TOTAL EVALUATION TIME:",
        "btn_start": "START",
        "btn_pause": "PAUSE",
        "btn_resume": "RESUME",
        "btn_prev": "PREVIOUS",
        "btn_next": "NEXT",
        "phase_indicator": "Phase {atual} of {total}",
        "prev_phase_title": "Previous Phase",
        "prev_phase_msg": "Going back to:\n{fase}",
        "next_phase_title": "Next Phase",
        "next_phase_msg": "Advancing to:\n{fase}",
        "general_time_over_title": "TOTAL TIME OVER",
        "general_time_over_msg": "The 30 minutes of the evaluation have ended!",
        "eval_done_title": "EVALUATION COMPLETED",
        "eval_done_msg": "Team {equipe}\n\nAll phases have been completed!",
        "warning_title": "WARNING",
        "warning_1min": "{fase}\n\n1 MINUTE REMAINING!",
        "warning_30s": "{fase}\n\n30 SECONDS REMAINING!",
        "language_button": "PT / EN",

        # Fases (nomes exibidos)
        "fase1": "1 - SETUP AND INTRODUCTIONS",
        "fase2": "2 - INNOVATION PROJECT PRESENTATION",
        "fase3": "3 - INNOVATION PROJECT Q&A",
        "fase4": "4 - ROBOT DESIGN PRESENTATION",
        "fase5": "5 - ROBOT DESIGN Q&A",
        "fase6": "6 - FEEDBACK AND FINAL REMARKS",
    }
}


class TemporizadorFLL:
    def __init__(self, root):
        self.root = root

        # Idioma padrão: português
        self.idioma = "pt"

        self.root.title(TEXTOS[self.idioma]["app_title"])
        self.root.geometry("900x700")
        self.root.configure(bg=CORES["fundo"])
        self.root.resizable(True, True)

        self.equipe = ""
        self.fase_atual = 0
        self.tempo_restante = 0
        self.duracao_total = 0
        self.executando = False
        self.thread = None

        self.tempo_geral = 30 * 60
        self.thread_geral = None
        self.cronometro_geral_iniciado = False

        self.aviso_1min_dado = False
        self.aviso_30seg_dado = False

        self.logo_img = self.carregar_logo()
        self.fonte_titulo = font.Font(family="Arial", size=24, weight="bold")
        self.fonte_fase = font.Font(family="Arial", size=20, weight="bold")
        self.fonte_tempo = font.Font(family="Arial", size=72, weight="bold")
        self.fonte_botoes = font.Font(family="Arial", size=12, weight="bold")
        self.fonte_geral = font.Font(family="Arial", size=18, weight="bold")

        # Referências a widgets para atualização de idioma
        self.lbl_header_title = None
        self.lbl_subtitle = None
        self.lbl_team_label = None
        self.btn_iniciar_tela_inicial = None

        self.lbl_total_time_label = None
        self.lbl_tempo_geral = None
        self.lbl_fase = None
        self.lbl_indicador = None
        self.btn_iniciar = None
        self.btn_pausar = None
        self.btn_continuar = None
        self.btn_voltar = None
        self.btn_proxima = None
        self.btn_idioma = None

        self.mostrar_tela_inicial()

    # ==========================
    # ÁUDIO (WAV com winsound)
    # ==========================
    def tocar_som_arquivo(self, nome_arquivo):
        def _play():
            try:
                caminho = resource_path(nome_arquivo)
                winsound.PlaySound(caminho, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Erro ao tocar som '{nome_arquivo}': {e}")

        threading.Thread(target=_play, daemon=True).start()

    # ==========================
    # LOGO / INTERFACE INICIAL
    # ==========================
    def carregar_logo(self):
        logo_path = resource_path("fll_logo.png")
        if not os.path.exists(logo_path):
            try:
                logo_path = "fll_logo.png"
                urllib.request.urlretrieve(
                    "https://www.firstinspires.org/hs-fs/hubfs/logo-library/fll/FLL-RGB_Challenge-horiz-stacked-full-color.png?width=2000&name=FLL-RGB_Challenge-horiz-stacked-full-color.png",
                    logo_path
                )
            except:
                return None

        if os.path.exists(logo_path):
            img = Image.open(logo_path).resize((180, 80), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    def mostrar_tela_inicial(self):
        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root, bg=CORES["fundo"])
        frame.pack(expand=True, fill="both")

        if self.logo_img:
            tk.Label(frame, image=self.logo_img, bg=CORES["fundo"]).pack(pady=20)

        self.lbl_header_title = tk.Label(
            frame,
            text=TEXTOS[self.idioma]["header_title"],
            font=self.fonte_titulo,
            bg=CORES["fundo"],
            fg=CORES["azul_fll"]
        )
        self.lbl_header_title.pack(pady=5)

        self.lbl_subtitle = tk.Label(
            frame,
            text=TEXTOS[self.idioma]["subtitle"],
            font=("Arial", 14),
            bg=CORES["fundo"],
            fg=CORES["texto"]
        )
        self.lbl_subtitle.pack(pady=5)

        self.lbl_team_label = tk.Label(
            frame,
            text=TEXTOS[self.idioma]["team_label"],
            font=("Arial", 16, "bold"),
            bg=CORES["fundo"],
            fg=CORES["texto"]
        )
        self.lbl_team_label.pack(pady=20)

        self.entry_equipe = tk.Entry(
            frame,
            font=("Arial", 18),
            width=30,
            justify="center",
            relief="flat",
            highlightthickness=2,
            highlightcolor=CORES["azul_fll"]
        )
        self.entry_equipe.pack(pady=10)
        self.entry_equipe.focus()

        self.btn_iniciar_tela_inicial = tk.Button(
            frame,
            text=TEXTOS[self.idioma]["start_eval"],
            font=self.fonte_botoes,
            bg=CORES["azul_fll"],
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.iniciar_avaliacao,
            cursor="hand2"
        )
        self.btn_iniciar_tela_inicial.pack(pady=25)
        self.animar_botao(self.btn_iniciar_tela_inicial)

        # Botão para alternar idioma também na tela inicial
        self.btn_idioma = tk.Button(
            frame,
            text=TEXTOS[self.idioma]["language_button"],
            font=("Arial", 10, "bold"),
            bg="#dddddd",
            fg="#000000",
            relief="flat",
            padx=10,
            pady=5,
            command=self.alternar_idioma,
            cursor="hand2"
        )
        self.btn_idioma.pack(pady=10)
        
        # NOVO TEXTO ADICIONADO AQUI
        tk.Label(
            frame,
            text="Desenvolvido por F. Stark e F. Escalise - Versão 2.0",
            font=("Arial", 9),
            bg=CORES["fundo"],
            fg="#616161"
        ).pack(pady=(5, 0))


        self.root.bind('<Return>', lambda e: self.iniciar_avaliacao())

    def animar_botao(self, btn):
        def hover(e): btn.config(bg=CORES["amarelo_fll"])
        def leave(e): btn.config(bg=btn.default_bg)
        btn.default_bg = btn['bg']
        btn.bind("<Enter>", hover)
        btn.bind("<Leave>", leave)

    # ==========================
    # FLUXO PRINCIPAL
    # ==========================
    def iniciar_avaliacao(self):
        nome = self.entry_equipe.get().strip()
        if not nome:
            messagebox.showwarning(
                TEXTOS[self.idioma]["team_warning_title"],
                TEXTOS[self.idioma]["team_warning_msg"]
            )
            return

        self.equipe = nome
        for widget in self.root.winfo_children():
            widget.destroy()

        self.criar_interface_principal()
        self.proxima_fase()

        if not self.cronometro_geral_iniciado:
            self.cronometro_geral_iniciado = True
            self.iniciar_contagem_geral()

        self.forcar_inicio()
        self.tocar_som_arquivo("charge.wav")

    def criar_interface_principal(self):
        self.root.title(TEXTOS[self.idioma]["app_title"])

        container = tk.Frame(self.root, bg=CORES["fundo"])
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg=CORES["azul_fll"], height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        if self.logo_img:
            tk.Label(header, image=self.logo_img, bg=CORES["azul_fll"]).pack(side="left", padx=20, pady=10)

        self.lbl_header_title = tk.Label(
            header,
            text=f"EQUIPE: {self.equipe}" if self.idioma == "pt" else f"TEAM: {self.equipe}",
            font=("Arial", 18, "bold"),
            bg=CORES["azul_fll"],
            fg="white"
        )
        self.lbl_header_title.pack(side="left", padx=10, pady=10)

        # Botão idioma no cabeçalho
        self.btn_idioma = tk.Button(
            header,
            text=TEXTOS[self.idioma]["language_button"],
            font=("Arial", 10, "bold"),
            bg="#dddddd",
            fg="#000000",
            relief="flat",
            padx=10,
            pady=5,
            command=self.alternar_idioma,
            cursor="hand2"
        )
        self.btn_idioma.pack(side="right", padx=20)

        # Cronômetro geral
        frame_geral = tk.Frame(container, bg=CORES["amarelo_fll"], height=70)
        frame_geral.pack(fill="x")
        frame_geral.pack_propagate(False)

        self.lbl_total_time_label = tk.Label(
            frame_geral,
            text=TEXTOS[self.idioma]["total_time_label"],
            font=("Arial", 14, "bold"),
            bg=CORES["amarelo_fll"],
            fg=CORES["texto"]
        )
        self.lbl_total_time_label.pack(side="left", padx=20)

        self.lbl_tempo_geral = tk.Label(
            frame_geral,
            text="30:00",
            font=self.fonte_geral,
            bg=CORES["amarelo_fll"],
            fg=CORES["azul_fll"]
        )
        self.lbl_tempo_geral.pack(side="right", padx=30)

        main = tk.Frame(container, bg=CORES["fundo"])
        main.pack(expand=True, fill="both", pady=20, padx=20)

        self.lbl_fase = tk.Label(
            main,
            text="",
            font=self.fonte_fase,
            bg=CORES["fundo"],
            fg=CORES["azul_fll"],
            wraplength=800,
            justify="center"
        )
        self.lbl_fase.pack(pady=10)

        self.lbl_tempo = tk.Label(
            main,
            text="00:00",
            font=self.fonte_tempo,
            bg=CORES["fundo"],
            fg=CORES["verde"]
        )
        self.lbl_tempo.pack(pady=20)

        self.canvas = tk.Canvas(main, height=40, bg=CORES["cinza"], highlightthickness=0)
        self.canvas.pack(pady=15, fill="x", expand=False)
        self.barra = self.canvas.create_rectangle(10, 10, 10, 30, fill=CORES["verde"], outline="", width=0)
        self.canvas.tag_bind(self.barra, "<Button-1>", self.clique_barra)
        self.canvas.tag_bind(self.barra, "<B1-Motion>", self.arrastar_barra)
        self.canvas.bind("<Configure>", lambda e: self.atualizar_barra())

        self.lbl_indicador = tk.Label(
            main,
            text="",
            font=("Arial", 14),
            bg=CORES["fundo"],
            fg="#555"
        )
        self.lbl_indicador.pack(pady=5)

        frame_botoes = tk.Frame(main, bg=CORES["fundo"])
        frame_botoes.pack(pady=20)

        self.btn_iniciar = self.criar_botao(
            frame_botoes,
            TEXTOS[self.idioma]["btn_start"],
            CORES["verde"],
            self.forcar_inicio
        )
        self.btn_iniciar.grid(row=0, column=0, padx=10)

        self.btn_pausar = self.criar_botao(
            frame_botoes,
            TEXTOS[self.idioma]["btn_pause"],
            CORES["laranja"],
            self.pausar
        )
        self.btn_pausar.grid(row=0, column=1, padx=10)
        self.btn_pausar.grid_remove()

        self.btn_continuar = self.criar_botao(
            frame_botoes,
            TEXTOS[self.idioma]["btn_resume"],
            CORES["verde"],
            self.continuar
        )
        self.btn_continuar.grid(row=0, column=2, padx=10)
        self.btn_continuar.grid_remove()

        self.btn_voltar = self.criar_botao(
            frame_botoes,
            TEXTOS[self.idioma]["btn_prev"],
            "#757575",
            self.fase_anterior
        )
        self.btn_voltar.grid(row=0, column=3, padx=10)

        self.btn_proxima = self.criar_botao(
            frame_botoes,
            TEXTOS[self.idioma]["btn_next"],
            CORES["azul_fll"],
            self.forcar_proxima_fase
        )
        self.btn_proxima.grid(row=0, column=4, padx=10)

        self.atualizar_indicador_fase()

    def criar_botao(self, parent, texto, cor, comando):
        btn = tk.Button(
            parent,
            text=texto,
            font=self.fonte_botoes,
            bg=cor,
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            command=comando,
            cursor="hand2"
        )
        self.animar_botao(btn)
        return btn

    # ==========================
    # SUPORTE A IDIOMA
    # ==========================
    def alternar_idioma(self):
        # alterna entre 'pt' e 'en'
        self.idioma = "en" if self.idioma == "pt" else "pt"
        self.atualizar_idioma()

    def atualizar_idioma(self):
        self.root.title(TEXTOS[self.idioma]["app_title"])

        # Tela inicial
        if self.lbl_header_title and isinstance(self.lbl_header_title.master, tk.Frame):
            if "EQUIPE:" in self.lbl_header_title.cget("text") or "TEAM:" in self.lbl_header_title.cget("text"):
                # estamos na tela principal, não sobrescreve aqui
                pass
            else:
                self.lbl_header_title.config(text=TEXTOS[self.idioma]["header_title"])
        if self.lbl_subtitle:
            self.lbl_subtitle.config(text=TEXTOS[self.idioma]["subtitle"])
        if self.lbl_team_label:
            self.lbl_team_label.config(text=TEXTOS[self.idioma]["team_label"])
        if self.btn_iniciar_tela_inicial:
            self.btn_iniciar_tela_inicial.config(text=TEXTOS[self.idioma]["start_eval"])

        # Botão de idioma (tela inicial ou principal)
        if self.btn_idioma:
            self.btn_idioma.config(text=TEXTOS[self.idioma]["language_button"])

        # Tela principal (se já existir)
        if self.lbl_total_time_label:
            self.lbl_total_time_label.config(text=TEXTOS[self.idioma]["total_time_label"])

        if self.lbl_header_title and (f"EQUIPE: " in self.lbl_header_title.cget("text")
                                      or f"TEAM: " in self.lbl_header_title.cget("text")):
            # Cabeçalho da tela principal
            if self.idioma == "pt":
                self.lbl_header_title.config(text=f"EQUIPE: {self.equipe}")
            else:
                self.lbl_header_title.config(text=f"TEAM: {self.equipe}")

        if self.btn_iniciar:
            self.btn_iniciar.config(text=TEXTOS[self.idioma]["btn_start"])
        if self.btn_pausar:
            self.btn_pausar.config(text=TEXTOS[self.idioma]["btn_pause"])
        if self.btn_continuar:
            self.btn_continuar.config(text=TEXTOS[self.idioma]["btn_resume"])
        if self.btn_voltar:
            self.btn_voltar.config(text=TEXTOS[self.idioma]["btn_prev"])
        if self.btn_proxima:
            self.btn_proxima.config(text=TEXTOS[self.idioma]["btn_next"])

        self.atualizar_indicador_fase()
        self.atualizar_nome_fase()

    # ==========================
    # FASES
    # ==========================
    def obter_nome_fase_atual(self):
        chave, _ = FASES_CHAVES[self.fase_atual]
        return TEXTOS[self.idioma][chave]

    def atualizar_nome_fase(self):
        if self.lbl_fase:
            self.lbl_fase.config(text=self.obter_nome_fase_atual())

    def atualizar_indicador_fase(self):
        if self.lbl_indicador:
            texto = TEXTOS[self.idioma]["phase_indicator"].format(
                atual=self.fase_atual + 1,
                total=len(FASES_CHAVES)
            )
            self.lbl_indicador.config(text=texto)

    def proxima_fase(self):
        if self.fase_atual >= len(FASES_CHAVES):
            self.finalizar_avaliacao()
            return

        chave, duracao = FASES_CHAVES[self.fase_atual]
        self.tempo_restante = duracao
        self.duracao_total = duracao

        self.aviso_1min_dado = False
        self.aviso_30seg_dado = False

        self.atualizar_nome_fase()
        self.atualizar_tempo()
        self.atualizar_barra()
        self.atualizar_indicador_fase()
        self.mostrar_botao_iniciar()

    def mostrar_botao_iniciar(self):
        if self.btn_pausar:
            self.btn_pausar.grid_remove()
        if self.btn_continuar:
            self.btn_continuar.grid_remove()
        if self.btn_iniciar:
            self.btn_iniciar.grid()

    def forcar_inicio(self):
        if not self.executando:
            self.executando = True
            if self.btn_iniciar:
                self.btn_iniciar.grid_remove()
            if self.btn_pausar:
                self.btn_pausar.grid()
            self.iniciar_contagem()

    def pausar(self):
        self.executando = False
        if self.btn_pausar:
            self.btn_pausar.grid_remove()
        if self.btn_continuar:
            self.btn_continuar.grid()

    def continuar(self):
        self.executando = True
        if self.btn_continuar:
            self.btn_continuar.grid_remove()
        if self.btn_pausar:
            self.btn_pausar.grid()
        self.iniciar_contagem()

    # ==========================
    # CONTAGENS
    # ==========================
    def iniciar_contagem(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.contagem_regressiva, daemon=True)
            self.thread.start()

    def iniciar_contagem_geral(self):
        if self.thread_geral is None or not self.thread_geral.is_alive():
            self.thread_geral = threading.Thread(target=self.contagem_regressiva_geral, daemon=True)
            self.thread_geral.start()

    def contagem_regressiva(self):
        while self.tempo_restante > 0 and self.executando:
            time.sleep(1)
            if self.executando:
                self.tempo_restante -= 1
                self.root.after(0, self.atualizar_tempo)
                self.root.after(0, self.atualizar_barra)
                self.root.after(0, self.verificar_avisos)

        if self.executando and self.tempo_restante <= 0:
            self.tocar_som_arquivo("buzzer.wav")
            self.root.after(0, self.finalizar_fase_atual)

    def contagem_regressiva_geral(self):
        while self.tempo_geral > 0:
            time.sleep(1)
            self.tempo_geral -= 1
            self.root.after(0, self.atualizar_tempo_geral)

        if self.tempo_geral <= 0:
            self.root.after(0, self.alerta_tempo_geral_esgotado)

    # ==========================
    # AVISOS ESPECIAIS
    # ==========================
    def verificar_avisos(self):
        chave, _ = FASES_CHAVES[self.fase_atual]
        nome_fase = TEXTOS[self.idioma][chave]

        if chave in FASES_COM_AVISOS_CHAVES:
            if self.tempo_restante == 60 and not self.aviso_1min_dado:
                self.aviso_1min_dado = True
                self.tocar_som_arquivo("dingding.wav")
                messagebox.showwarning(
                    TEXTOS[self.idioma]["warning_title"],
                    TEXTOS[self.idioma]["warning_1min"].format(fase=nome_fase),
                    parent=self.root
                )
            elif self.tempo_restante == 30 and not self.aviso_30seg_dado:
                self.aviso_30seg_dado = True
                self.tocar_som_arquivo("laser.wav")
                messagebox.showwarning(
                    TEXTOS[self.idioma]["warning_title"],
                    TEXTOS[self.idioma]["warning_30s"].format(fase=nome_fase),
                    parent=self.root
                )

    def alerta_tempo_geral_esgotado(self):
        self.tocar_som_arquivo("buzzer.wav")
        messagebox.showerror(
            TEXTOS[self.idioma]["general_time_over_title"],
            TEXTOS[self.idioma]["general_time_over_msg"],
            parent=self.root
        )

    # ==========================
    # ATUALIZAÇÃO VISUAL
    # ==========================
    def atualizar_tempo_geral(self):
        mins = self.tempo_geral // 60
        secs = self.tempo_geral % 60
        if self.lbl_tempo_geral:
            self.lbl_tempo_geral.config(text=f"{mins:02d}:{secs:02d}")

            if self.tempo_geral <= 60:
                self.lbl_tempo_geral.config(fg=CORES["vermelho"])
            elif self.tempo_geral <= 5 * 60:
                self.lbl_tempo_geral.config(fg=CORES["laranja"])
            else:
                self.lbl_tempo_geral.config(fg=CORES["azul_fll"])

    def finalizar_fase_atual(self):
        self.executando = False
        self.fase_atual += 1
        self.root.after(1500, self.proxima_fase)

    def fase_anterior(self):
        if self.fase_atual > 0:
            self.executando = False
            self.fase_atual -= 1
            self.proxima_fase()
            chave, _ = FASES_CHAVES[self.fase_atual]
            nome_fase = TEXTOS[self.idioma][chave]
            messagebox.showinfo(
                TEXTOS[self.idioma]["prev_phase_title"],
                TEXTOS[self.idioma]["prev_phase_msg"].format(fase=nome_fase)
            )

    def forcar_proxima_fase(self):
        self.executando = False
        self.fase_atual += 1
        self.proxima_fase()
        if self.fase_atual < len(FASES_CHAVES):
            chave, _ = FASES_CHAVES[self.fase_atual]
            nome_fase = TEXTOS[self.idioma][chave]
            messagebox.showinfo(
                TEXTOS[self.idioma]["next_phase_title"],
                TEXTOS[self.idioma]["next_phase_msg"].format(fase=nome_fase)
            )

    def clique_barra(self, event):
        self.ajustar_tempo(event.x)

    def arrastar_barra(self, event):
        self.ajustar_tempo(event.x)

    def ajustar_tempo(self, x):
        largura_total = max(self.canvas.winfo_width() - 20, 10)
        offset = 10
        x = max(offset, min(x, offset + largura_total))
        percentual = (x - offset) / largura_total
        self.tempo_restante = int(self.duracao_total * percentual)
        self.atualizar_tempo()
        self.atualizar_barra()

    def atualizar_tempo(self):
        mins = self.tempo_restante // 60
        secs = self.tempo_restante % 60
        if self.lbl_tempo:
            self.lbl_tempo.config(text=f"{mins:02d}:{secs:02d}")
            if self.tempo_restante <= 30:
                self.lbl_tempo.config(fg=CORES["vermelho"])
            elif self.tempo_restante <= 60:
                self.lbl_tempo.config(fg=CORES["laranja"])
            else:
                self.lbl_tempo.config(fg=CORES["verde"])

    def atualizar_barra(self):
        largura_total = max(self.canvas.winfo_width() - 20, 10)
        offset = 10
        percentual = self.tempo_restante / self.duracao_total if self.duracao_total > 0 else 0
        percentual = max(0, min(1, percentual))
        nova_largura = largura_total * percentual
        self.canvas.coords(self.barra, offset, 10, offset + nova_largura, 30)

        cor = CORES["verde"] if percentual > 0.5 else CORES["laranja"] if percentual > 0.2 else CORES["vermelho"]
        self.canvas.itemconfig(self.barra, fill=cor)

    def finalizar_avaliacao(self):
        self.executando = False
        messagebox.showinfo(
            TEXTOS[self.idioma]["eval_done_title"],
            TEXTOS[self.idioma]["eval_done_msg"].format(equipe=self.equipe),
            icon="info"
        )
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = TemporizadorFLL(root)
    root.mainloop()
