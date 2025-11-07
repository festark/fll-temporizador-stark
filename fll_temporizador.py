import tkinter as tk
from tkinter import messagebox, font
import time
import threading
import winsound
import urllib.request
import os
from PIL import Image, ImageTk

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

FASES = [
    ("Projeto de Inovação", 5 * 60),
    ("Feedback Inovação", 5 * 60),
    ("Design do Robô", 5 * 60),
    ("Feedback Robô", 5 * 60),
    ("Perguntas e Respostas", 8 * 60),
    ("Deliberação dos Juízes", 10 * 60)
]

class TemporizadorFLL:
    def __init__(self, root):
        self.root = root
        self.root.title("FLL - Temporizador de Avaliação")
        self.root.geometry("800x600")
        self.root.configure(bg=CORES["fundo"])
        self.root.resizable(False, False)

        self.equipe = ""
        self.fase_atual = 0
        self.tempo_restante = 0
        self.duracao_total = 0
        self.executando = False
        self.thread = None

        self.logo_img = self.carregar_logo()
        self.fonte_titulo = font.Font(family="Arial", size=24, weight="bold")
        self.fonte_fase = font.Font(family="Arial", size=20, weight="bold")
        self.fonte_tempo = font.Font(family="Arial", size=72, weight="bold")
        self.fonte_botoes = font.Font(family="Arial", size=12, weight="bold")

        self.mostrar_tela_inicial()

    def carregar_logo(self):
        logo_path = "fll_logo.png"
        if not os.path.exists(logo_path):
            try:
                urllib.request.urlretrieve(
                    "https://www.firstinspires.org/hs-fs/hubfs/logo-library/fll/FLL-RGB_Challenge-horiz-stacked-full-color.png?width=2000&name=FLL-RGB_Challenge-horiz-stacked-full-color.png",
                    logo_path
                )
            except:
                pass
        if os.path.exists(logo_path):
            img = Image.open(logo_path).resize((180, 80), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    def mostrar_tela_inicial(self):
        frame = tk.Frame(self.root, bg=CORES["fundo"])
        frame.pack(expand=True)

        if self.logo_img:
            tk.Label(frame, image=self.logo_img, bg=CORES["fundo"]).pack(pady=20)

        tk.Label(frame, text="FIRST® LEGO® LEAGUE", font=self.fonte_titulo,
                 bg=CORES["fundo"], fg=CORES["azul_fll"]).pack(pady=5)
        tk.Label(frame, text="Temporizador de Avaliação", font=("Arial", 14),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(pady=5)

        tk.Label(frame, text="Nome da Equipe:", font=("Arial", 16, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(pady=20)

        self.entry_equipe = tk.Entry(frame, font=("Arial", 18), width=30, justify="center",
                                     relief="flat", highlightthickness=2, highlightcolor=CORES["azul_fll"])
        self.entry_equipe.pack(pady=10)
        self.entry_equipe.focus()

        btn_iniciar = tk.Button(frame, text="INICIAR AVALIAÇÃO", font=self.fonte_botoes,
                                bg=CORES["azul_fll"], fg="white", relief="flat", padx=20, pady=10,
                                command=self.iniciar_avaliacao, cursor="hand2")
        btn_iniciar.pack(pady=25)
        self.animar_botao(btn_iniciar)

        self.root.bind('<Return>', lambda e: self.iniciar_avaliacao())

    def animar_botao(self, btn):
        def hover(e): btn.config(bg=CORES["amarelo_fll"])
        def leave(e): btn.config(bg=btn.default_bg)
        btn.default_bg = btn['bg']
        btn.bind("<Enter>", hover)
        btn.bind("<Leave>", leave)

    def iniciar_avaliacao(self):
        nome = self.entry_equipe.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome da equipe!")
            return
        self.equipe = nome
        for widget in self.root.winfo_children():
            widget.destroy()

        self.criar_interface_principal()
        self.proxima_fase()

    def criar_interface_principal(self):
        header = tk.Frame(self.root, bg=CORES["azul_fll"], height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        if self.logo_img:
            tk.Label(header, image=self.logo_img, bg=CORES["azul_fll"]).pack(side="left", padx=20, pady=10)
        tk.Label(header, text=f"EQUIPE: {self.equipe}", font=("Arial", 18, "bold"),
                 bg=CORES["azul_fll"], fg="white").pack(side="right", padx=30, pady=10)

        main = tk.Frame(self.root, bg=CORES["fundo"])
        main.pack(expand=True, fill="both", pady=20)

        self.lbl_fase = tk.Label(main, text="", font=self.fonte_fase,
                                 bg=CORES["fundo"], fg=CORES["azul_fll"])
        self.lbl_fase.pack(pady=10)

        self.lbl_tempo = tk.Label(main, text="00:00", font=self.fonte_tempo,
                                  bg=CORES["fundo"], fg=CORES["verde"])
        self.lbl_tempo.pack(pady=20)

        self.canvas = tk.Canvas(main, width=700, height=40, bg=CORES["cinza"], highlightthickness=0)
        self.canvas.pack(pady=15)
        self.barra = self.canvas.create_rectangle(10, 10, 10, 30, fill=CORES["verde"], outline="", width=0)
        self.canvas.tag_bind(self.barra, "<Button-1>", self.clique_barra)
        self.canvas.tag_bind(self.barra, "<B1-Motion>", self.arrastar_barra)

        self.lbl_indicador = tk.Label(main, text="", font=("Arial", 14), bg=CORES["fundo"], fg="#555")
        self.lbl_indicador.pack(pady=5)

        # === BOTÕES DE CONTROLE (SEPARADOS) ===
        frame_botoes = tk.Frame(main, bg=CORES["fundo"])
        frame_botoes.pack(pady=20)

        # Botão INICIAR (só aparece se não começou)
        self.btn_iniciar = self.criar_botao(frame_botoes, "INICIAR", CORES["verde"], self.forcar_inicio)
        self.btn_iniciar.grid(row=0, column=0, padx=10)

        # Botão PAUSAR
        self.btn_pausar = self.criar_botao(frame_botoes, "PAUSAR", CORES["laranja"], self.pausar)
        self.btn_pausar.grid(row=0, column=1, padx=10)
        self.btn_pausar.grid_remove()  # Esconde inicialmente

        # Botão CONTINUAR
        self.btn_continuar = self.criar_botao(frame_botoes, "CONTINUAR", CORES["verde"], self.continuar)
        self.btn_continuar.grid(row=0, column=2, padx=10)
        self.btn_continuar.grid_remove()  # Esconde inicialmente

        # Botões de fase
        self.btn_voltar = self.criar_botao(frame_botoes, "ANTERIOR", "#757575", self.fase_anterior)
        self.btn_voltar.grid(row=0, column=3, padx=10)

        self.btn_proxima = self.criar_botao(frame_botoes, "PRÓXIMA", CORES["azul_fll"], self.forcar_proxima_fase)
        self.btn_proxima.grid(row=0, column=4, padx=10)

        self.atualizar_indicador_fase()

    def criar_botao(self, parent, texto, cor, comando):
        btn = tk.Button(parent, text=texto, font=self.fonte_botoes,
                        bg=cor, fg="white", relief="flat", padx=15, pady=8,
                        command=comando, cursor="hand2")
        self.animar_botao(btn)
        return btn

    def atualizar_indicador_fase(self):
        self.lbl_indicador.config(text=f"Fase {self.fase_atual + 1} de {len(FASES)}")

    def proxima_fase(self):
        if self.fase_atual >= len(FASES):
            self.finalizar_avaliacao()
            return

        nome, duracao = FASES[self.fase_atual]
        self.tempo_restante = duracao
        self.duracao_total = duracao

        self.lbl_fase.config(text=nome)
        self.atualizar_tempo()
        self.atualizar_barra()
        self.atualizar_indicador_fase()

        # Mostra INICIAR e esconde outros
        self.mostrar_botao_iniciar()

    def mostrar_botao_iniciar(self):
        self.btn_pausar.grid_remove()
        self.btn_continuar.grid_remove()
        self.btn_iniciar.grid()

    def forcar_inicio(self):
        if not self.executando:
            self.executando = True
            self.btn_iniciar.grid_remove()
            self.btn_pausar.grid()
            self.iniciar_contagem()

    def pausar(self):
        self.executando = False
        self.btn_pausar.grid_remove()
        self.btn_continuar.grid()

    def continuar(self):
        self.executando = True
        self.btn_continuar.grid_remove()
        self.btn_pausar.grid()
        self.iniciar_contagem()

    def iniciar_contagem(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.contagem_regressiva, daemon=True)
            self.thread.start()

    def contagem_regressiva(self):
        while self.tempo_restante > 0 and self.executando:
            time.sleep(1)
            if self.executando:
                self.tempo_restante -= 1
                self.root.after(0, self.atualizar_tempo)
                self.root.after(0, self.atualizar_barra)

        if self.executando:
            self.root.after(0, self.tocar_alerta)
            self.root.after(0, self.finalizar_fase_atual)

    def finalizar_fase_atual(self):
        self.executando = False
        self.fase_atual += 1
        self.root.after(1500, self.proxima_fase)

    def fase_anterior(self):
        if self.fase_atual > 0:
            self.executando = False
            self.fase_atual -= 1
            self.proxima_fase()
            messagebox.showinfo("Fase Anterior", f"Voltando para:\n{FASES[self.fase_atual][0]}")

    def forcar_proxima_fase(self):
        self.executando = False
        self.fase_atual += 1
        self.proxima_fase()
        if self.fase_atual < len(FASES):
            messagebox.showinfo("Avançar", f"Avançando para:\n{FASES[self.fase_atual][0]}")

    def clique_barra(self, event): self.ajustar_tempo(event.x)
    def arrastar_barra(self, event): self.ajustar_tempo(event.x)

    def ajustar_tempo(self, x):
        largura = 680
        offset = 10
        x = max(offset, min(x, offset + largura))
        percentual = (x - offset) / largura
        self.tempo_restante = int(self.duracao_total * percentual)
        self.atualizar_tempo()
        self.atualizar_barra()

    def atualizar_tempo(self):
        mins = self.tempo_restante // 60
        secs = self.tempo_restante % 60
        self.lbl_tempo.config(text=f"{mins:02d}:{secs:02d}")
        if self.tempo_restante <= 30:
            self.lbl_tempo.config(fg=CORES["vermelho"])
        elif self.tempo_restante <= 60:
            self.lbl_tempo.config(fg=CORES["laranja"])
        else:
            self.lbl_tempo.config(fg=CORES["verde"])

    def atualizar_barra(self):
        largura_total = 680
        offset = 10
        percentual = self.tempo_restante / self.duracao_total if self.duracao_total > 0 else 0
        nova_largura = largura_total * percentual
        self.canvas.coords(self.barra, offset, 10, offset + nova_largura, 30)

        cor = CORES["verde"] if percentual > 0.5 else CORES["laranja"] if percentual > 0.2 else CORES["vermelho"]
        self.canvas.itemconfig(self.barra, fill=cor)

    def tocar_alerta(self):
        try:
            for freq in [800, 1000, 1200]:
                winsound.Beep(freq, 400)
                time.sleep(0.3)
        except:
            pass

    def finalizar_avaliacao(self):
        self.executando = False
        messagebox.showinfo("AVALIAÇÃO CONCLUÍDA",
                            f"Equipe {self.equipe}\n\nTodas as fases foram concluídas!",
                            icon="info")
        self.root.quit()


# === EXECUTAR ===
if __name__ == "__main__":
    root = tk.Tk()
    app = TemporizadorFLL(root)
    root.mainloop()
