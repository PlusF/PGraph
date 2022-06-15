import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import *
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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

        self.master.bind("<Return>", self.update_graph)

    def create_graph(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.ax_x = self.ax.get_xaxis()
        self.ax_y = self.ax.get_yaxis()
        self.ax.set_xlim(1.4, 2.9)
        self.ax.set_ylim(0, 10000)
        self.ax.set_yticks([])
        self.ax.set_xlabel('Energy [eV]')
        self.ax.set_ylabel('Intensity [arb. units]')

    def create_config(self):
        self.frame_graph = tk.LabelFrame(master=self.master, text='Graph Area')
        self.frame_graph.grid(row=0, column=0, columnspan=3)

        self.frame_config = tk.LabelFrame(master=self.master, text='Load Data')
        self.frame_config.grid(row=1, rowspan=2, column=0)

        self.frame_fitting = tk.LabelFrame(master=self.master, text='Fitting')
        self.frame_fitting.grid(row=2, column=1)

        self.label_msg = tk.Label(master=self.master, textvariable=self.msg)
        self.label_msg.grid(row=1, column=1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.frame_graph_setting = tk.LabelFrame(master=self.frame_graph, text='Graph Setting')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_graph, pack_toolbar=False)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.toolbar.grid(row=1, column=0)
        self.frame_graph_setting.grid(row=0, column=1)

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

        self.labelframe_xaxis = tk.LabelFrame(master=self.frame_graph_setting, text='x軸ラベル')
        self.x_label = tk.IntVar(value=2)
        self.radio_x_1 = tk.Radiobutton(master=self.labelframe_xaxis, text='波長 [nm]', value=1, variable=self.x_label)
        self.radio_x_2 = tk.Radiobutton(master=self.labelframe_xaxis, text='エネルギー [eV]', value=2, variable=self.x_label)
        self.y_label = tk.IntVar(value=1)
        self.labelframe_yaxis = tk.LabelFrame(master=self.frame_graph_setting, text='y軸ラベル')
        self.radio_y_1 = tk.Radiobutton(master=self.labelframe_yaxis, text='Intensity [arb. units]', value=1, variable=self.y_label)
        self.radio_y_2 = tk.Radiobutton(master=self.labelframe_yaxis, text='Counts', value=2, variable=self.y_label)

        self.labelframe_range = tk.LabelFrame(master=self.frame_graph_setting, text='グラフ範囲')
        self.label_min = tk.Label(master=self.labelframe_range, text='min')
        self.label_max = tk.Label(master=self.labelframe_range, text='max')
        self.label_ticks = tk.Label(master=self.labelframe_range, text='分割数')
        self.label_xrange = tk.Label(master=self.labelframe_range, text='x')
        self.label_yrange = tk.Label(master=self.labelframe_range, text='y')
        self.entry_xmin = tk.Entry(master=self.labelframe_range, width=5, justify=tk.CENTER)
        self.entry_xmax = tk.Entry(master=self.labelframe_range, width=5, justify=tk.CENTER)
        self.entry_xticks = tk.Entry(master=self.labelframe_range, textvariable=tk.StringVar(value='auto'), width=5, justify=tk.CENTER)
        self.entry_ymin = tk.Entry(master=self.labelframe_range, width=5, justify=tk.CENTER)
        self.entry_ymax = tk.Entry(master=self.labelframe_range, width=5, justify=tk.CENTER)
        self.entry_yticks = tk.Entry(master=self.labelframe_range, textvariable=tk.StringVar(value='auto'), width=5, justify=tk.CENTER)
        self.label_min.grid(row=0, column=1)
        self.label_max.grid(row=0, column=2)
        self.label_ticks.grid(row=0, column=3)
        self.label_xrange.grid(row=1, column=0)
        self.entry_xmin.grid(row=1, column=1)
        self.entry_xmax.grid(row=1, column=2)
        self.entry_xticks.grid(row=1, column=3)
        self.label_yrange.grid(row=2, column=0)
        self.entry_ymin.grid(row=2, column=1)
        self.entry_ymax.grid(row=2, column=2)
        self.entry_yticks.grid(row=2, column=3)

        self.label_color = tk.Label(master=self.frame_graph_setting, text='色')
        self.label_y_shift = tk.Label(master=self.frame_graph_setting, text='y方向シフト')
        self.entry_color = ttk.Combobox(master=self.frame_graph_setting, values=('black', 'red', 'blue', 'green', 'purple', 'gray', 'gold'), width=5)
        self.entry_color.insert(0, 'black')
        self.entry_y_shift = tk.Entry(master=self.frame_graph_setting, textvariable=tk.StringVar(value='0'), width=5, justify=tk.CENTER)
        self.button_apply = tk.Button(master=self.frame_graph_setting, text='適用', width=10, command=self.update_graph)
        self.labelframe_xaxis.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.labelframe_yaxis.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.labelframe_range.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.label_color.grid(row=3, column=0)
        self.label_y_shift.grid(row=4, column=0)
        self.entry_color.grid(row=3, column=1)
        self.entry_y_shift.grid(row=4, column=1)
        self.button_apply.grid(row=5, column=0, columnspan=2)
        self.radio_x_1.grid(row=0, column=0, sticky=tk.W)
        self.radio_x_2.grid(row=1, column=0, sticky=tk.W)
        self.radio_y_1.grid(row=0, column=0, sticky=tk.W)
        self.radio_y_2.grid(row=1, column=0, sticky=tk.W)

    def clear(self):
        for obj in self.ax.lines + self.ax.collections:
            obj.remove()

    def draw(self):
        self.clear()

        xlims = {'min': [1e10], 'max': [0]}
        ylims = {'min': [1e10], 'max': [0]}
        for item in self.dl.get_dict().values():
            df = item['data']
            color = item['color']
            y_shift = item['y_shift']

            x = df.x.values
            if self.x_label.get() == 2:  # エネルギー
                x = 1240 / x

            y = df.y.values

            ln, = self.ax.plot(x, y + y_shift, color=color)
            self.lines.append(ln)

            xlims['min'].append(min(x))
            xlims['max'].append(max(x))
            ylims['min'].append(min(y + y_shift))
            ylims['max'].append(max(y + y_shift))

        xlim = [min(xlims['min']), max(xlims['max'])]
        ylim = [min(ylims['min']) * 0.9, max(ylims['max']) * 1.1]
        self.ax.set(xlim=xlim, ylim=ylim)

        if self.x_label.get() == 1:  # 波長
            self.ax.set_xlabel('Wavelength [nm]')
        elif self.x_label.get() == 2:  # エネルギー
            self.ax.set_xlabel('Energy [eV]')

        if self.y_label.get() == 1:
            self.ax.set_yticks([])
            self.ax.set_ylabel('Intensity [arb. units]')
        elif self.y_label.get() == 2:
            self.ax.set_yticks(np.linspace(0, round(self.ax.get_ylim()[1], -2), 5))
            self.ax.set_ylabel('Counts')

        if self.if_show.get():
            self.fitter.draw(self.ax)

        self.canvas.draw()

    def check_range(self):
        xmin = self.entry_xmin.get()
        xmax = self.entry_xmax.get()
        ymin = self.entry_ymin.get()
        ymax = self.entry_ymax.get()
        if xmin == '':
            xmin = self.ax.get_xlim()[0]
        else:
            xmin = float(xmin)
        if xmax == '':
            xmax = self.ax.get_xlim()[1]
        else:
            xmax = float(xmax)
        if ymin == '':
            ymin = self.ax.get_ylim()[0]
        else:
            ymin = float(ymin)
        if ymax == '':
            ymax = self.ax.get_ylim()[1]
        else:
            ymax = float(ymax)
        self.ax.set(xlim=[xmin, xmax], ylim=[ymin, ymax])

        self.ax_x.reset_ticks()
        self.ax_y.reset_ticks()
        if self.entry_xticks.get() != 'auto':
            self.ax_x.set_ticks(np.linspace(xmin, xmax, int(self.entry_xticks.get()) + 1))
        if self.entry_yticks.get() != 'auto':
            self.ax_y.set_ticks(np.linspace(ymin, ymax, int(self.entry_yticks.get()) + 1))

        self.canvas.draw()

    def update_graph(self, event=None):
        selected_index = self.listbox_asc.curselection()
        for index in selected_index:
            filename = self.listbox_asc.get(index)
            color = self.entry_color.get()
            y_shift = self.entry_y_shift.get()
            self.dl.change_color(filename, color)
            self.dl.change_y_shift(filename, y_shift)

        self.draw()

        self.check_range()

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
        x = df_fit.x.values
        if self.x_label.get() == 2:  # エネルギー
            x = 1240 / x
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
