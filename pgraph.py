import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_loader import DataLoader
from fitting import Fit

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


def quit_me(root_window):
    root_window.quit()
    root_window.destroy()


class PGraph(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.dl = DataLoader()
        self.fit = Fit()
        self.lines = []
        self.msg = tk.StringVar(value='ファイルをドロップしてください')

        self.create_graph()
        self.create_config()

    def create_graph(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.ax.set_xlim(1.4, 2.9)
        self.ax.set_ylim(0, 10000)
        self.ax.set_yticks([])
        self.ax.set_xlabel('Energy [eV]')  # TODO: 波長と可換に
        self.ax.set_ylabel('Intensity [arb. units]')  # TODO: Countsと可換に

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=2)

    def create_config(self):
        self.frame_config = tk.LabelFrame(master=self.master, text='Load Data')
        self.frame_config.grid(row=1, column=0)

        self.frame_graph = tk.LabelFrame(master=self.master, text='Graph Setting')
        self.frame_graph.grid(row=1, column=1)

        self.label_msg = tk.Label(master=self.frame_config, textvariable=self.msg)
        self.listbox_asc = tk.Listbox(master=self.frame_config, width=50, height=6, selectmode='extended')
        xbar = tk.Scrollbar(self.frame_config, orient=tk.HORIZONTAL)
        ybar = tk.Scrollbar(self.frame_config, orient=tk.VERTICAL)
        xbar.grid(row=2, column=0, sticky=tk.W + tk.E)
        ybar.grid(row=1, column=1, sticky=tk.N + tk.S)
        xbar.config(command=self.listbox_asc.xview)
        ybar.config(command=self.listbox_asc.yview)
        self.listbox_asc.config(xscrollcommand=xbar.set)
        self.listbox_asc.config(yscrollcommand=ybar.set)
        self.button_delete = tk.Button(master=self.frame_config, text='削除', width=10, height=1, command=self.delete)
        self.button_quit = tk.Button(master=self.frame_config, text='終了', fg='red',  width=10, height=1, command=self.quit)
        self.label_msg.grid(row=0, column=0)
        self.listbox_asc.grid(row=1, column=0)
        self.button_delete.grid(row=3, column=0)
        self.button_quit.grid(row=3, column=2)

        self.label_color = tk.Label(master=self.frame_graph, text='色')
        self.label_y_shift = tk.Label(master=self.frame_graph, text='y方向シフト')
        self.entry_color = ttk.Combobox(master=self.frame_graph, values=('black', 'red', 'blue', 'green', 'purple', 'gray', 'gold'), width=10)
        self.entry_y_shift = tk.Entry(master=self.frame_graph, textvariable=tk.StringVar(value='0'), width=13, justify=tk.CENTER)
        self.button_apply = tk.Button(master=self.frame_graph, text='適用', width=10, command=self.update_graph)
        self.label_color.grid(row=0, column=0)
        self.label_y_shift.grid(row=1, column=0)
        self.entry_color.grid(row=0, column=1)
        self.entry_y_shift.grid(row=1, column=1)
        self.button_apply.grid(row=2, column=0, columnspan=2)

    def draw(self):
        for _ in self.lines:
            self.ax.lines.pop(0)
            self.lines.pop(0)
        ylims = {'min': [1e10], 'max': [0]}
        for item in self.dl.get_dict().values():
            df = item['data']
            color = item['color']
            y_shift = item['y_shift']

            df_tmp = df.astype(float)
            x = (1240 / df_tmp.x).values
            y = df_tmp.y.values

            ln, = self.ax.plot(x, y + y_shift, color=color)
            self.lines.append(ln)

            ylims['min'].append(min(y + y_shift))
            ylims['max'].append(max(y + y_shift))
        ylim = [min(ylims['min']) * 0.9, max(ylims['max']) * 1.1]
        self.ax.set_ylim(ylim)

        self.canvas.draw()

    def update_graph(self):
        selected_index = self.listbox_asc.curselection()
        for index in selected_index:
            filename = self.listbox_asc.get(index)
            color = self.entry_color.get()
            y_shift = self.entry_y_shift.get()
            self.dl.change_color(filename, color)
            self.dl.change_y_shift(filename, y_shift)

        self.draw()

    def load(self, event=None):
        filenames = [f.replace('{', '').replace('}', '') for f in event.data.split('} {')]
        ret = self.dl.load_files(filenames)
        if ret:
            self.msg.set('全てのファイルが正常に読み込まれました．')
        else:
            self.msg.set('一部のファイルが正常に読み込まれませんでした．')
        self.update_listbox()
        self.draw()

    def update_listbox(self):
        self.listbox_asc.delete(0, tk.END)
        loaded_filenames = self.dl.get_names()
        for filename in loaded_filenames:
            self.listbox_asc.insert(0, filename)

    def delete(self):
        selected_index = self.listbox_asc.curselection()
        for index in selected_index:
            filename = self.listbox_asc.get(index)
            self.dl.delete_file(filename)
        for index in reversed(selected_index):
            self.listbox_asc.delete(index)
        self.draw()

    def quit(self):
        quit_me(self.master)


def main():
    # Drug & Drop が可能なTkオブジェクトを生成
    root = TkinterDnD.Tk()
    root.title('PGraph')
    # root.geometry('1000x800')

    app = PGraph(master=root)
    root.drop_target_register(DND_FILES)
    root.protocol('WM_DELETE_WINDOW', lambda: quit_me(root))
    root.dnd_bind('<<Drop>>', app.load)
    app.mainloop()


if __name__ == '__main__':
    main()
