import os
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from MyToolbar import MyToolbar
from dataloader import DataLoader
from fitting import Fit


def set_rcParams() -> None:
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 15

    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.major.width'] = 1.0
    plt.rcParams['ytick.major.width'] = 1.0
    plt.rcParams['xtick.labelsize'] = 15
    plt.rcParams['ytick.labelsize'] = 15

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

        self.dl = DataLoader()
        self.fitter = Fit()
        self.msg = tk.StringVar(value='ファイルをドロップしてください')

        self.create_graph()
        self.create_config()

        self.master.bind("<Return>", self.update_option)

        # TODO: 縦ライン・横ラインを入れられるように
        # TODO: legend機能つける？

    def create_graph(self) -> None:
        width = 800
        height = 500
        dpi = 100
        if os.name == 'posix':
            width /= 2
            height /= 2
            dpi /= 2
        self.fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        self.ax = self.fig.add_subplot()
        self.ax_x = self.ax.get_xaxis()
        self.ax_y = self.ax.get_yaxis()
        self.ax.set_xlim(1.4, 2.9)
        self.ax.set_ylim(0, 10000)
        self.ax.set_yticks([])
        self.ax.set_xlabel('Energy [eV]')
        self.ax.set_ylabel('Intensity [arb. units]')

    def create_config(self) -> None:
        # all parent frames
        self.frame_graph = tk.LabelFrame(master=self.master, text='Graph Area')
        self.frame_config = tk.LabelFrame(master=self.master, text='Loaded Data')
        self.frame_fitting = tk.LabelFrame(master=self.master, text='Fitting')
        self.label_msg = tk.Label(master=self.master, textvariable=self.msg)
        self.frame_graph.grid(row=0, column=0, columnspan=3)
        self.frame_config.grid(row=1, rowspan=2, column=0)
        self.frame_fitting.grid(row=2, column=1)
        self.label_msg.grid(row=1, column=1)

        # graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.frame_graph_setting = tk.LabelFrame(master=self.frame_graph, text='Graph Setting')
        self.toolbar = MyToolbar(self.canvas, self.frame_graph, pack_toolbar=False)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.toolbar.grid(row=1, column=0)
        self.frame_graph_setting.grid(row=0, column=1, rowspan=2)

        # config
        self.listbox_file = tk.Listbox(master=self.frame_config, width=70, height=8, selectmode='extended')
        self.listbox_file.bind('<Double-1>', self.select)
        self.xbar = tk.Scrollbar(self.frame_config, orient=tk.HORIZONTAL)
        self.ybar = tk.Scrollbar(self.frame_config, orient=tk.VERTICAL)
        self.xbar.config(command=self.listbox_file.xview)
        self.ybar.config(command=self.listbox_file.yview)
        self.listbox_file.config(xscrollcommand=self.xbar.set)
        self.listbox_file.config(yscrollcommand=self.ybar.set)
        self.button_delete = tk.Button(master=self.frame_config, text='削除', width=12, height=1, command=self.delete)
        self.button_sort_ascending = tk.Button(master=self.frame_config, text='ソート（昇順）', width=12, height=1, command=self.sort_file_ascending)
        self.button_sort_descending = tk.Button(master=self.frame_config, text='ソート（降順）', width=12, height=1, command=self.sort_file_descending)
        self.button_reset_selection = tk.Button(master=self.frame_config, text='ハイライト解除', width=12, height=1, command=self.reset_selection)
        self.button_quit = tk.Button(master=self.frame_config, text='終了', fg='red',  width=12, height=1, command=self.quit)
        self.listbox_file.grid(row=0, column=0, columnspan=5)
        self.xbar.grid(row=1, column=0, columnspan=5, sticky=tk.W + tk.E)
        self.ybar.grid(row=0, column=5, sticky=tk.N + tk.S)
        self.button_delete.grid(row=2, column=0)
        self.button_sort_ascending.grid(row=2, column=1)
        self.button_sort_descending.grid(row=2, column=2)
        self.button_reset_selection.grid(row=2, column=3)
        self.button_quit.grid(row=2, column=4)

        # fitting
        self.functions = ('Lorentzian', 'Gaussian', "Voigt")
        self.function_fitting = tk.StringVar(value=self.functions[0])
        self.optionmenu_fitting = tk.OptionMenu(self.frame_fitting, self.function_fitting, self.functions[0], *self.functions[1:], command=self.function_changed)
        self.description_fitting = tk.StringVar(value='位置 強度 幅 (BG)')
        self.label_description_1 = tk.Label(master=self.frame_fitting, textvariable=self.description_fitting)
        self.label_description_2 = tk.Label(master=self.frame_fitting, textvariable=self.description_fitting)
        self.text_params = tk.Text(master=self.frame_fitting, width=30, height=5)
        self.text_params.insert(1.0, '1.7 20000 1\n1.8 3000 1\n0 0')
        self.text_params_fit = tk.Text(master=self.frame_fitting, width=30, height=5)
        self.button_fit = tk.Button(master=self.frame_fitting, text='Fit', width=10, command=self.fit)
        self.if_show = tk.BooleanVar(value=False)
        self.check_fit = tk.Checkbutton(master=self.frame_fitting, variable=self.if_show, text='結果を描画', command=self.draw)
        self.button_load = tk.Button(master=self.frame_fitting, text='LOAD', width=10, command=self.load_params)
        self.button_save = tk.Button(master=self.frame_fitting, text='SAVE', width=10, command=self.save_params)
        self.optionmenu_fitting.grid(row=0, column=0, columnspan=4)
        self.label_description_1.grid(row=1, column=0, columnspan=2)
        self.label_description_2.grid(row=1, column=2, columnspan=2)
        self.text_params.grid(row=2, column=0, columnspan=2)
        self.text_params_fit.grid(row=2, column=2, columnspan=2)
        self.button_fit.grid(row=3, column=0)
        self.check_fit.grid(row=3, column=1)
        self.button_load.grid(row=3, column=2)
        self.button_save.grid(row=3, column=3)

        # labelframes in graph_setting
        self.labelframe_xaxis = tk.LabelFrame(master=self.frame_graph_setting, text='x軸ラベル')
        self.labelframe_yaxis = tk.LabelFrame(master=self.frame_graph_setting, text='y軸ラベル')
        self.labelframe_range = tk.LabelFrame(master=self.frame_graph_setting, text='グラフ範囲')
        self.labelframe_individual = tk.LabelFrame(master=self.frame_graph_setting, text='個別設定')
        self.labelframe_advanced = tk.LabelFrame(master=self.frame_graph_setting, text='一括設定')
        self.labelframe_xaxis.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.labelframe_yaxis.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.labelframe_range.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.labelframe_individual.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.labelframe_advanced.grid(row=4, column=0, columnspan=2, sticky=tk.W)

        # xaxis, yaxis
        self.x_labels = ('Wavelength [nm]', 'Energy [eV]', 'Raman Shift [cm-1]')
        self.y_labels = ('Intensity [arb. units]', 'Counts', 'Absorbance')
        self.x_label = tk.IntVar(value=1)
        for i, label in enumerate(self.x_labels):
            radio_x = tk.Radiobutton(master=self.labelframe_xaxis, text=label, value=i+1, variable=self.x_label, command=self.update_option)
            radio_x.grid(row=i, column=0, sticky=tk.W)
        self.y_label = tk.IntVar(value=2)
        for i, label in enumerate(self.y_labels):
            radio_y = tk.Radiobutton(master=self.labelframe_yaxis, text=label, value=i+1, variable=self.y_label, command=self.update_option)
            radio_y.grid(row=i, column=0, sticky=tk.W)

        # range
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
        # self.if_legend = tk.BooleanVar(value=False)
        # self.check_legend = tk.Checkbutton(master=self.labelframe_range, variable=self.if_legend, text='Legend', command=self.draw)
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
        # self.check_legend.grid(row=3, column=0, columnspan=4)

        # individual
        self.label_color = tk.Label(master=self.labelframe_individual, text='色')
        self.label_linestyle = tk.Label(master=self.labelframe_individual, text='線種')
        self.label_y_shift = tk.Label(master=self.labelframe_individual, text='y方向シフト')
        self.label_y_times = tk.Label(master=self.labelframe_individual, text='y方向倍率')
        self.combobox_color = ttk.Combobox(master=self.labelframe_individual, values=('black', 'red', 'blue', 'green', 'purple', 'gray', 'gold'), width=5)
        self.combobox_color.insert(0, 'black')
        self.combobox_linestyle = ttk.Combobox(master=self.labelframe_individual, values=('solid', 'dashed', 'dashdot', 'dotted'), width=5)
        self.combobox_linestyle.insert(0, 'solid')
        self.y_shift_value = tk.DoubleVar(value=0)
        self.y_times_value = tk.DoubleVar(value=1)
        self.entry_y_shift = tk.Entry(master=self.labelframe_individual, textvariable=self.y_shift_value, width=5, justify=tk.CENTER)
        self.entry_y_times = tk.Entry(master=self.labelframe_individual, textvariable=self.y_times_value, width=5, justify=tk.CENTER)
        self.button_apply = tk.Button(master=self.labelframe_individual, text='適用', width=10, command=self.update_option)
        self.button_reset = tk.Button(master=self.labelframe_individual, text='リセット', width=10, command=self.reset)
        self.label_color.grid(row=0, column=0)
        self.label_linestyle.grid(row=1, column=0)
        self.label_y_shift.grid(row=2, column=0)
        self.label_y_times.grid(row=3, column=0)
        self.combobox_color.grid(row=0, column=1)
        self.combobox_linestyle.grid(row=1, column=1)
        self.entry_y_shift.grid(row=2, column=1)
        self.entry_y_times.grid(row=3, column=1)
        self.button_apply.grid(row=4, column=0)
        self.button_reset.grid(row=4, column=1)

        # advanced
        self.y_shift_each_value = tk.DoubleVar(value=0)
        self.entry_y_shift_each = tk.Entry(master=self.labelframe_advanced, textvariable=self.y_shift_each_value, width=5, justify=tk.CENTER)
        self.label_y_shift_each = tk.Label(master=self.labelframe_advanced, text='ずつy方向にずらす')
        self.button_apply_advanced = tk.Button(master=self.labelframe_advanced, text='適用', width=10, command=self.apply_advanced)
        self.entry_y_shift_each.grid(row=0, column=0)
        self.label_y_shift_each.grid(row=0, column=1)
        self.button_apply_advanced.grid(row=1, column=0, columnspan=2)

    def clear(self) -> None:
        for obj in self.ax.lines + self.ax.collections:
            obj.remove()

    def draw(self) -> None:
        self.clear()

        xlims = {'min': [1e10], 'max': [0]}
        ylims = {'min': [1e10], 'max': [0]}
        for spec in self.dl.spec_dict.values():
            linewidth = 2 if spec.highlight else 1

            x = spec.xdata
            if self.x_label.get() == 2:  # エネルギー
                x = 1240 / x
            y = spec.ydata * spec.y_times

            self.ax.plot(x, y + spec.y_shift, color=spec.color, linestyle=spec.linestyle, linewidth=linewidth)

            xlims['min'].append(min(x))
            xlims['max'].append(max(x))
            ylims['min'].append(min(y + spec.y_shift))
            ylims['max'].append(max(y + spec.y_shift))

        xlim = [min(xlims['min']), max(xlims['max'])]
        ylim = [min(ylims['min']) * 0.9, max(ylims['max']) * 1.1]

        self.ax.set(xlim=xlim, ylim=ylim)

        self.ax.set_xlabel(self.x_labels[self.x_label.get() - 1])
        self.ax.set_ylabel(self.y_labels[self.y_label.get() - 1])

        if self.if_show.get():
            self.fitter.draw(self.ax)

        # if self.if_legend.get():
        #     self.ax.legend()

        self.check_and_fix_range()

        self.canvas.draw()

    def get_graph_range(self) -> [list[float, float], list[float, float]]:
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

        return [xmin, xmax], [ymin, ymax]

    def check_and_fix_range(self) -> None:
        xlim, ylim = self.get_graph_range()
        self.ax.set(xlim=xlim, ylim=ylim)

        self.ax_x.reset_ticks()
        self.ax_y.reset_ticks()
        if self.entry_xticks.get() != 'auto':
            self.ax_x.set_ticks(np.linspace(*xlim, int(self.entry_xticks.get()) + 1))
        if self.entry_yticks.get() != 'auto':
            self.ax_y.set_ticks(np.linspace(*ylim, int(self.entry_yticks.get()) + 1))

    def update_option(self, event=None) -> None:
        selected_index = self.listbox_file.curselection()
        for index in selected_index:
            filename = self.listbox_file.get(index)
            color = self.combobox_color.get()
            linestyle = self.combobox_linestyle.get()
            y_shift = self.y_shift_value.get()
            y_times = self.y_times_value.get()
            self.dl.spec_dict[filename].color = color
            self.dl.spec_dict[filename].linestyle = linestyle
            self.dl.spec_dict[filename].y_shift = y_shift
            self.dl.spec_dict[filename].y_times = y_times

        self.draw()

    def apply_advanced(self, event=None) -> None:
        for i in range(len(self.dl.spec_dict)):
            filename = self.listbox_file.get(i)
            self.dl.spec_dict[filename].y_shift = i * self.y_shift_each_value.get()
        self.draw()

    def load(self, event: TkinterDnD.DnDEvent=None) -> None:
        if os.name == 'nt':
            filenames = event.data.split('} {')
            filenames = list(map(lambda x: x.strip('{').strip('}'), filenames))
        else:
            filenames = event.data.split()
        self.dl.load_files(filenames)
        self.check_device(filenames[0])
        self.update_listbox()
        self.draw()

    def select(self, event=None) -> None:
        self.dl.reset_highlight()
        selected_index = self.listbox_file.curselection()
        for index in selected_index:
            filename = self.listbox_file.get(index)
            self.dl.spec_dict[filename].highlight = True
            self.combobox_color.set(self.dl.spec_dict[filename].color)
            self.y_shift_value.set(self.dl.spec_dict[filename].y_shift)
            self.y_times_value.set(self.dl.spec_dict[filename].y_times)
        self.draw()

    def reset_selection(self) -> None:
        self.listbox_file.select_clear(0, tk.END)
        self.dl.reset_highlight()
        self.draw()

    def update_listbox(self) -> None:
        self.listbox_file.delete(0, tk.END)
        loaded_filenames = self.dl.spec_dict.keys()
        for filename in loaded_filenames:
            self.listbox_file.insert(tk.END, filename)

    def check_device(self, filename: str) -> None:
        device = self.dl.spec_dict[filename].device
        if device == 'Renishaw':
            self.x_label.set(3)
        elif device == 'Andor':
            self.x_label.set(2)
        elif device == 'CCS':
            self.x_label.set(2)

    def reset(self) -> None:
        self.dl.reset_option()
        self.draw()

    def get_params_from_text(self) -> list[list[str]]:
        params = self.text_params.get(1.0, tk.END)
        params = params.split('\n')
        params = [p.split() for p in params]
        params = list(filter(([]).__ne__, params))

        return params

    def function_changed(self, event=None) -> None:
        pre_num = self.fitter.num_params_per_func
        pre_params = self.get_params_from_text()

        self.fitter.set_function(self.function_fitting.get())

        if self.fitter.num_params_per_func == 3:
            description = '位置 強度 幅 (BG)'
            if pre_num == 4:
                params_default = [' '.join(p[:-1]) for p in pre_params[:-1]] + pre_params[-1]
                params_default = '\n'.join(params_default)
            else:
                params_default = [' '.join(p) for p in pre_params]
                params_default = '\n'.join(params_default)
        elif self.fitter.num_params_per_func == 4:
            description = '位置 強度 幅(Lor) 幅(Gau) (BG)'
            if pre_num == 3:
                params_default = [' '.join(p + ['1']) for p in pre_params[:-1]] + pre_params[-1]
                params_default = '\n'.join(params_default)
            else:
                params_default = [' '.join(p) for p in pre_params]
                params_default = '\n'.join(params_default)
        else:
            print('Unknown function')
            return

        self.description_fitting.set(description)
        self.text_params.delete(1.0, tk.END)
        self.text_params.insert(1.0, params_default)

    def fit(self) -> None:
        df_fit = self.dl.concat_spec()
        df_fit = df_fit.sort_values('x', ascending=False)

        x = df_fit.x.values
        if self.x_label.get() == 2:  # エネルギー
            x = 1240 / x
        y = df_fit.y.values

        # 表示範囲だけにトリミング
        xlim, _ = self.get_graph_range()
        fit_range = (xlim[0] <= x) & (x <= xlim[1])
        x = x[fit_range]
        y = y[fit_range]
        self.fitter.set_data(x, y)

        params = self.get_params_from_text()
        params = [float(value.replace(r'\x7f308', '')) for sublist in params for value in sublist]

        self.fitter.set_params(params)
        if self.fitter.fit():
            self.msg.set('フィッティングに成功しました．')
        else:
            self.msg.set('フィッティングに失敗しました．パラメータを変えてください．')
            return

        self.show_params(self.text_params_fit, self.fitter.params_fit)

        self.draw()

    def show_params(self, textbox: tk.Text, params: list[float]) -> None:
        text = ''
        for i in range(self.fitter.num_func):
            for j in range(self.fitter.num_params_per_func):
                text += str(round(params[i * self.fitter.num_params_per_func + j], 2)) + ' '
            text += '\n'
        text += str(round(params[-2], 3)) + ' ' + str(round(params[-1], 3)) + '\n'
        textbox.delete(1.0, tk.END)
        textbox.insert(1.0, text)

    def load_params(self) -> None:
        filename = self.listbox_file.get(0)
        params = self.dl.spec_dict[filename].fitting
        if len(params) == 0:
            self.msg.set('No params to load.')
            return

        # set function
        func = params[0]
        self.function_fitting.set(func)
        self.function_changed()
        # set parameters
        params = params[1:]
        self.fitter.set_params(params)

        self.show_params(self.text_params, self.fitter.params)

    def save_params(self) -> None:
        for i in range(len(self.dl.spec_dict)):
            filename = self.listbox_file.get(i)
            self.dl.spec_dict[filename].fitting = [self.function_fitting.get()] + self.fitter.params_fit.tolist()
            self.dl.save(filename)

    def delete(self) -> None:
        selected_index = self.listbox_file.curselection()
        for index in selected_index:
            filename = self.listbox_file.get(index)
            self.dl.delete_file(filename)
        for index in reversed(selected_index):
            self.listbox_file.delete(index)

        self.draw()

    def sort_file_ascending(self) -> None:
        self.listbox_file.delete(0, tk.END)
        for filename in sorted(self.dl.spec_dict.keys()):
            self.listbox_file.insert(tk.END, filename)

    def sort_file_descending(self) -> None:
        self.listbox_file.delete(0, tk.END)
        for filename in sorted(self.dl.spec_dict.keys(), reverse=True):
            self.listbox_file.insert(tk.END, filename)

    def quit(self) -> None:
        self.master.quit()
        self.master.destroy()


def main():
    set_rcParams()

    root = TkinterDnD.Tk()
    root.title('PGraph')

    app = PGraph(master=root)
    root.drop_target_register(DND_FILES)
    root.protocol('WM_DELETE_WINDOW', app.quit)
    root.dnd_bind('<<Drop>>', app.load)
    app.mainloop()


if __name__ == '__main__':
    main()
