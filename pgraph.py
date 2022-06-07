import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import *
import re
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
        self.fitter = Fit()
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
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)

    def create_config(self):
        self.frame_config = tk.LabelFrame(master=self.master, text='Load Data')
        self.frame_config.grid(row=1, rowspan=2, column=0)

        self.frame_graph = tk.LabelFrame(master=self.master, text='Graph Setting')
        self.frame_graph.grid(row=2, column=1)

        self.frame_fitting = tk.LabelFrame(master=self.master, text='Fitting')
        self.frame_fitting.grid(row=2, column=2)

        self.label_msg = tk.Label(master=self.master, textvariable=self.msg)
        self.label_msg.grid(row=1, column=1, columnspan=2)

        self.listbox_asc = tk.Listbox(master=self.frame_config, width=50, height=6, selectmode='extended')
        self.xbar = tk.Scrollbar(self.frame_config, orient=tk.HORIZONTAL)
        self.ybar = tk.Scrollbar(self.frame_config, orient=tk.VERTICAL)
        self.xbar.config(command=self.listbox_asc.xview)
        self.ybar.config(command=self.listbox_asc.yview)
        self.listbox_asc.config(xscrollcommand=self.xbar.set)
        self.listbox_asc.config(yscrollcommand=self.ybar.set)
        self.button_update = tk.Button(master=self.frame_config, text='グラフ\n更新', width=10, height=4, command=self.draw)
        self.button_delete = tk.Button(master=self.frame_config, text='削除', width=10, height=1, command=self.delete)
        self.button_quit = tk.Button(master=self.frame_config, text='終了', fg='red',  width=10, height=1, command=self.quit)
        self.listbox_asc.grid(row=0, column=0)
        self.xbar.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.ybar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.button_update.grid(row=0, column=2)
        self.button_delete.grid(row=2, column=0)
        self.button_quit.grid(row=2, column=2)

        self.label_color = tk.Label(master=self.frame_graph, text='色')
        self.label_y_shift = tk.Label(master=self.frame_graph, text='y方向シフト')
        self.entry_color = ttk.Combobox(master=self.frame_graph, values=('black', 'red', 'blue', 'green', 'purple', 'gray', 'gold'), width=10)
        self.entry_color.insert(0, 'black')
        self.entry_y_shift = tk.Entry(master=self.frame_graph, textvariable=tk.StringVar(value='0'), width=13, justify=tk.CENTER)
        self.button_apply = tk.Button(master=self.frame_graph, text='適用', width=10, command=self.update_graph)
        self.label_color.grid(row=0, column=0)
        self.label_y_shift.grid(row=1, column=0)
        self.entry_color.grid(row=0, column=1)
        self.entry_y_shift.grid(row=1, column=1)
        self.button_apply.grid(row=2, column=0, columnspan=2)

        self.label_description_1 = tk.Label(master=self.frame_fitting, text='位置 強度 幅 (BG)')
        self.label_description_2 = tk.Label(master=self.frame_fitting, text='位置 強度 幅 (BG)')
        self.text_params = tk.Text(master=self.frame_fitting, width=20, height=5)
        self.text_params.insert(1.0, '1.7 20000 0.2\n1.8 3000 0.2\n2.4 8000 0.4\n0')
        self.text_params_fit = tk.Text(master=self.frame_fitting, width=20, height=5)
        self.button_fit = tk.Button(master=self.frame_fitting, text='Fit', width=10, command=self.fit)
        self.if_show = tk.BooleanVar(value=False)
        self.check_fit = tk.Checkbutton(master=self.frame_fitting, variable=self.if_show, text='結果を描画')
        self.button_load = tk.Button(master=self.frame_fitting, text='LOAD', width=10, command=self.load_params)
        self.button_save = tk.Button(master=self.frame_fitting, text='SAVE', width=10, command=self.save_params)
        self.label_description_1.grid(row=0, column=0, columnspan=2)
        self.label_description_2.grid(row=0, column=2, columnspan=2)
        self.text_params.grid(row=1, column=0, columnspan=2)
        self.text_params_fit.grid(row=1, column=2, columnspan=2)
        self.button_fit.grid(row=2, column=0)
        self.check_fit.grid(row=2, column=1)
        self.button_load.grid(row=2, column=2)
        self.button_save.grid(row=2, column=3)

    def clear(self):
        for obj in self.ax.lines + self.ax.collections:
            obj.remove()

    def draw(self):
        self.clear()
        ylims = {'min': [1e10], 'max': [0]}
        for item in self.dl.get_dict().values():
            df = item['data']
            color = item['color']
            y_shift = item['y_shift']

            x = (1240 / df.x).values
            y = df.y.values

            ln, = self.ax.plot(x, y + y_shift, color=color)
            self.lines.append(ln)

            ylims['min'].append(min(y + y_shift))
            ylims['max'].append(max(y + y_shift))
        ylim = [min(ylims['min']) * 0.9, max(ylims['max']) * 1.1]
        self.ax.set_ylim(ylim)

        if self.if_show.get():
            self.fitter.draw(self.ax)

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

    def fit(self):
        df_fit = None
        for df in self.dl.get_dfs():
            if df_fit is None:
                df_fit = df
            else:
                df_fit = pd.concat([df_fit, df], axis=0)
        if df_fit is None:
            self.msg.set('データが見つかりません．')
            return False

        df_fit = df_fit.sort_values('x', ascending=False)
        x = 1240 / df_fit.x.values
        y = df_fit.y.values

        self.fitter.load_data(x, y)

        params = self.text_params.get(1.0, tk.END)
        params = re.split('[\n ]', params)
        params = [float(p) for p in params if p != '']

        self.fitter.set_params(params)
        if self.fitter.fit():
            self.msg.set('フィッティングに成功しました．')
        else:
            self.msg.set('フィッティングに失敗しました．パラメータを変えてください．')

        self.show_params_fit()

        self.draw()

    def show_params_fit(self):
        params_fit = self.fitter.params_fit
        text = ''
        for i, param in enumerate(params_fit):
            if i % 3 in [0, 1]:
                text += str(round(param, 2)) + ' '
            else:
                text += str(round(param, 2)) + '\n'
        self.text_params_fit.delete(1.0, tk.END)
        self.text_params_fit.insert(1.0, text)

    def load_params(self):
        filename = list(self.dl.get_names())[0]
        filename = filename.split('/')[:-1]
        filename = '/'.join(filename)
        filename += '/params.asc'
        self.fitter.load_params(filename)
        self.show_params_fit()

    def save_params(self):
        filename = list(self.dl.get_names())[0]
        filename = filename.split('/')[:-1]
        filename = '/'.join(filename)
        filename += '/params.asc'
        self.fitter.save_params(filename)

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
