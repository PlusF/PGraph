import tkinter as tk
from tkinterdnd2 import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 15

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['axes.labelsize'] = 18         # 軸ラベルのフォントサイズ
plt.rcParams['axes.linewidth'] = 1.0        # グラフ囲う線の太さ

plt.rcParams['legend.loc'] = 'best'        # 凡例の位置、"best"でいい感じのところ
plt.rcParams['legend.frameon'] = True       # 凡例を囲うかどうか、Trueで囲う、Falseで囲わない
plt.rcParams['legend.framealpha'] = 1.0     # 透過度、0.0から1.0の値を入れる
plt.rcParams['legend.facecolor'] = 'white'  # 背景色
plt.rcParams['legend.edgecolor'] = 'black'  # 囲いの色
plt.rcParams['legend.fancybox'] = False     # Trueにすると囲いの四隅が丸くなる

plt.rcParams['lines.linewidth'] = 1.0
plt.rcParams['image.cmap'] = 'jet'
plt.rcParams['figure.subplot.bottom'] = 0.2
plt.rcParams['figure.subplot.left'] = 0.2


class PGraph(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.dfs = []
        self.lines = []
        self.msg = tk.StringVar(value='ファイルをドロップしてください')

        self.create_graph()
        self.create_config()

        self.update()

    def create_graph(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.ax.set_xlim(1.4, 2.9)
        self.ax.set_ylim(0, 10000)
        self.ax.set_yticks([])
        self.ax.set_xlabel('Energy [eV]')  # TODO: 波長と可換に
        self.ax.set_ylabel('Intensity [arb. units]')  # TODO: Countsと可換に

        self.canvas = FigureCanvasTkAgg(self.fig)
        self.canvas.get_tk_widget().pack()

    def create_config(self):
        self.frame_config = tk.LabelFrame(master=self.master)
        self.frame_config.pack()

        self.label_msg = tk.Label(master=self.frame_config, textvariable=self.msg)
        self.listbox_asc = tk.Listbox(master=self.frame_config, width=50, height=6)
        self.button_quit = tk.Button(master=self.frame_config, text='終了', fg='red',  width=20, height=10, command=self.quit)
        self.label_msg.pack()
        self.listbox_asc.pack()
        self.button_quit.pack()

    def update(self):
        self.draw()
        self.after(100, self.update)

    def quit(self):
        self.master.destroy()
        print('終了しました')

    def draw(self):
        xlim = [0, 0]
        ylim = [0, 0]
        for df in self.dfs:
            df_tmp = df.astype(float)
            x = (1240 / df_tmp.x).values
            y = df_tmp.y.values
            ln, = self.ax.plot(x, y, color='k')
            self.lines.append(ln)
            tmp_max = max(y)
        self.ax.set_xlim()
        self.ax.set_ylim()

        self.canvas.draw()

    def get_asc(self, event=None):
        filename = event.data.strip('{').strip('}')
        if filename.endswith('.asc'):
            self.msg = 'ascファイルが読み込まれました'
            self.listbox_asc.insert(tk.END, filename)
            df_tmp = pd.read_csv(filename, sep='[:\t]', header=None, engine='python')
            df_tmp = df_tmp.loc[26:, 0:1]
            df_tmp = df_tmp.reset_index(drop=True)
            df_tmp.columns = ['x', 'y']
            self.dfs.append(df_tmp)
        else:
            self.msg = 'ascファイルを選択してください'


def main():
    # Drug & Drop が可能なTkオブジェクトを生成
    root = TkinterDnD.Tk()
    root.title('PGraph')
    root.geometry('1000x600')

    app = PGraph(master=root)
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', app.get_asc)
    app.mainloop()


if __name__ == '__main__':
    main()
