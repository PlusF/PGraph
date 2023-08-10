import os
import tkinter as tk
from tkinter import ttk, font
from tkinterdnd2 import Tk, DND_FILES, TkinterDnD
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from MyToolbar import MyToolbar
from dataloader import DataLoader
from fitting import Fit


def set_rcParams() -> None:
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 25

    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.major.width'] = 1.0
    plt.rcParams['ytick.major.width'] = 1.0
    plt.rcParams['xtick.labelsize'] = 25
    plt.rcParams['ytick.labelsize'] = 25

    plt.rcParams['axes.linewidth'] = 1.0
    plt.rcParams['axes.labelsize'] = 35         # 軸ラベルのフォントサイズ
    plt.rcParams['axes.linewidth'] = 1.0        # グラフ囲う線の太さ

    plt.rcParams['legend.loc'] = 'best'        # 凡例の位置、"best"でいい感じのところ
    plt.rcParams['legend.frameon'] = True       # 凡例を囲うかどうか、Trueで囲う、Falseで囲わない
    plt.rcParams['legend.framealpha'] = 1.0     # 透過度、0.0から1.0の値を入れる
    plt.rcParams['legend.facecolor'] = 'white'  # 背景色
    plt.rcParams['legend.edgecolor'] = 'black'  # 囲いの色
    plt.rcParams['legend.fancybox'] = False     # Trueにすると囲いの四隅が丸くなる

    plt.rcParams['lines.linewidth'] = 1.0
    plt.rcParams['image.cmap'] = 'jet'
    plt.rcParams['figure.subplot.top'] = 0.95
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.left'] = 0.1
    plt.rcParams['figure.subplot.right'] = 0.95


class PGraph(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.dl = DataLoader()
        self.fitter = Fit()
        self.msg = tk.StringVar(value='ファイルをドロップしてください')

        self.spec_lines = {}
        self.vlines = []
        self.fitting_result = []

        self.create_graph()
        self.create_config()

        self.master.bind("<Return>", self.update_option)

        # TODO: 縦ライン・横ラインを入れられるように
        # TODO: legend機能つける？

    def create_graph(self) -> None:
        width = 900
        height = 600
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
        # スタイル設定
        font_md = ('Arial', 16)
        font_sm = ('Arial', 12)
        style = ttk.Style()
        style.theme_use('winnative')
        style.configure('TButton', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')
        style.configure('R.TButton', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='red')
        style.configure('TLabel', font=font_sm, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TEntry', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TCombobox', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TCheckbutton', font=font_md, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TMenubutton', font=font_md, width=10, padding=[0, 4, 0, 4], foreground='black', justify='center')
        # style.configure('TTreeview', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')

        # all parent frames
        self.frame_graph = tk.LabelFrame(master=self.master, text='Graph Area')
        self.frame_data = tk.LabelFrame(master=self.master, text='Loaded Data')
        self.frame_fitting = tk.LabelFrame(master=self.master, text='Fitting')
        self.label_msg = ttk.Label(master=self.master, textvariable=self.msg, style='TLabel')
        self.frame_graph.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.N)
        self.frame_data.grid(row=1, rowspan=2, column=0, padx=10, sticky=tk.N)
        self.frame_fitting.grid(row=2, column=1, padx=10, sticky=tk.N)
        self.label_msg.grid(row=3, column=0, columnspan=2, padx=10, sticky=tk.N)

        # graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.frame_graph_setting = tk.LabelFrame(master=self.frame_graph, text='Graph Setting')
        self.toolbar = MyToolbar(self.canvas, self.frame_graph, pack_toolbar=False)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.toolbar.grid(row=1, column=0)
        self.frame_graph_setting.grid(row=0, column=1, rowspan=2, sticky=tk.N)

        # data
        # TODO: Listbox => Treeview
        self.listbox_file = tk.Listbox(master=self.frame_data, width=100, height=10, selectmode='extended', font=font_sm)
        self.listbox_file.bind('<Double-1>', self.select)
        self.xbar = tk.Scrollbar(self.frame_data, orient=tk.HORIZONTAL)
        self.ybar = tk.Scrollbar(self.frame_data, orient=tk.VERTICAL)
        self.xbar.config(command=self.listbox_file.xview)
        self.ybar.config(command=self.listbox_file.yview)
        self.listbox_file.config(xscrollcommand=self.xbar.set)
        self.listbox_file.config(yscrollcommand=self.ybar.set)
        self.button_delete = ttk.Button(master=self.frame_data, text='削除', command=self.delete)
        self.button_sort_ascending = ttk.Button(master=self.frame_data, text='ソート（昇順）', command=self.sort_file_ascending)
        self.button_sort_descending = ttk.Button(master=self.frame_data, text='ソート（降順）', command=self.sort_file_descending)
        self.button_reset_selection = ttk.Button(master=self.frame_data, text='ハイライト解除', command=self.reset_selection)
        self.button_quit = ttk.Button(master=self.frame_data, text='終了', style='R.TButton', command=self.quit)
        self.listbox_file.grid(row=0, column=0, columnspan=5)
        self.xbar.grid(row=1, column=0, columnspan=5, sticky=tk.W + tk.E)
        self.ybar.grid(row=0, column=5, sticky=tk.N + tk.S)
        self.button_delete.grid(row=2, column=0, padx=5, pady=5)
        self.button_sort_ascending.grid(row=2, column=1, padx=5, pady=5)
        self.button_sort_descending.grid(row=2, column=2, padx=5, pady=5)
        self.button_reset_selection.grid(row=2, column=3, padx=5, pady=5)
        self.button_quit.grid(row=2, column=4, padx=5, pady=5)

        # fitting
        self.functions = ('Lorentzian', 'Gaussian', "Voigt")
        self.function_fitting = tk.StringVar(value=self.functions[0])
        optionmenu_fitting = ttk.OptionMenu(self.frame_fitting, self.function_fitting, self.functions[0], *self.functions, style='TMenubutton', command=self.function_changed)
        optionmenu_fitting['menu'].config(font=font_sm)
        self.description_fitting = tk.StringVar(value='位置 強度 幅 (BG)')
        self.description_fitting_fitted = tk.StringVar(value='(fitted) 位置 強度 幅 (BG)')
        self.label_description_1 = ttk.Label(master=self.frame_fitting,  textvariable=self.description_fitting)
        self.label_description_2 = ttk.Label(master=self.frame_fitting, textvariable=self.description_fitting_fitted)
        self.text_params = tk.Text(master=self.frame_fitting, width=30, height=5, font=font_md)
        self.text_params.insert(1.0, '1.7 20000 1\n1.8 3000 1\n0 0')
        self.text_params_fit = tk.Text(master=self.frame_fitting, width=30, height=5, font=font_md)
        self.button_fit = ttk.Button(master=self.frame_fitting, text='Fit', command=self.fit)
        self.if_show = tk.BooleanVar(value=False)
        self.check_fit = ttk.Checkbutton(master=self.frame_fitting, variable=self.if_show, text='結果を描画', style='TCheckbutton', command=self.refresh)
        self.button_load = ttk.Button(master=self.frame_fitting, text='LOAD', command=self.load_params)
        self.button_save = ttk.Button(master=self.frame_fitting, text='SAVE', command=self.save_params)
        optionmenu_fitting.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        self.label_description_1.grid(row=1, column=0, columnspan=2)
        self.label_description_2.grid(row=1, column=2, columnspan=2)
        self.text_params.grid(row=2, column=0, columnspan=2)
        self.text_params_fit.grid(row=2, column=2, columnspan=2)
        self.button_fit.grid(row=3, column=0, padx=5, pady=5)
        self.check_fit.grid(row=3, column=1, padx=5, pady=5)
        self.button_load.grid(row=3, column=2, padx=5, pady=5)
        self.button_save.grid(row=3, column=3, padx=5, pady=5)

        # labelframes in graph_setting
        self.frame_graph_setting_1 = ttk.Frame(master=self.frame_graph_setting)
        self.frame_graph_setting_2 = ttk.Frame(master=self.frame_graph_setting)
        self.frame_graph_setting_3 = ttk.Frame(master=self.frame_graph_setting)
        self.frame_graph_setting_1.grid(row=0, column=0, padx=5, sticky=tk.N + tk.W)
        self.frame_graph_setting_2.grid(row=0, column=1, padx=5, sticky=tk.N + tk.W)
        self.frame_graph_setting_3.grid(row=0, column=2, padx=5, sticky=tk.N + tk.W)
        self.labelframe_label = ttk.LabelFrame(master=self.frame_graph_setting_1, text='軸ラベル')
        self.labelframe_range = ttk.LabelFrame(master=self.frame_graph_setting_1, text='グラフ範囲')
        self.labelframe_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_range.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_individual = ttk.LabelFrame(master=self.frame_graph_setting_2, text='個別設定')
        self.labelframe_advanced = ttk.LabelFrame(master=self.frame_graph_setting_2, text='一括設定')
        self.button_reset = ttk.Button(master=self.frame_graph_setting_2, text='リセット', width=10, command=self.reset)
        self.labelframe_individual.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_advanced.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.button_reset.grid(row=3, column=0)
        self.labelframe_vline = ttk.LabelFrame(master=self.frame_graph_setting_3, text='縦線追加')
        self.labelframe_vline.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # xaxis, yaxis
        self.x_labels = ('Wavelength [nm]', 'Energy [eV]', 'Raman Shift [cm-1]')
        self.y_labels = ('Intensity [arb. units]', 'Counts', 'Absorbance', 'Transmittance')
        self.x_label = tk.StringVar()
        optionmenu_x_label = ttk.OptionMenu(self.labelframe_label, self.x_label, self.x_labels[0], *self.x_labels, command=self.update_option)
        optionmenu_x_label.config(width=16)
        optionmenu_x_label['menu'].config(font=font_sm)
        self.y_label = tk.StringVar()
        optionmenu_y_label = ttk.OptionMenu(self.labelframe_label, self.y_label, self.y_labels[0], *self.y_labels, command=self.update_option)
        optionmenu_y_label.config(width=16)
        optionmenu_y_label['menu'].config(font=font_sm)
        optionmenu_x_label.grid(row=0, column=0, padx=5, pady=5)
        optionmenu_y_label.grid(row=1, column=0, padx=5, pady=5)

        # range
        self.label_min = ttk.Label(master=self.labelframe_range, text='min')
        self.label_max = ttk.Label(master=self.labelframe_range, text='max')
        self.label_ticks = ttk.Label(master=self.labelframe_range, text='分割数')
        self.label_xrange = ttk.Label(master=self.labelframe_range, text='x')
        self.label_yrange = ttk.Label(master=self.labelframe_range, text='y')
        self.entry_xmin = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.entry_xmax = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.xticks = tk.StringVar(value='auto')
        self.entry_xticks = ttk.Entry(master=self.labelframe_range, textvariable=self.xticks, width=5, font=font_md, justify=tk.CENTER)
        self.entry_ymin = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.entry_ymax = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.yticks = tk.StringVar(value='auto')
        self.entry_yticks = ttk.Entry(master=self.labelframe_range, textvariable=self.yticks, width=5, font=font_md, justify=tk.CENTER)
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

        # individual
        self.label_color = ttk.Label(master=self.labelframe_individual, text='色')
        self.label_linestyle = ttk.Label(master=self.labelframe_individual, text='線種')
        self.label_y_shift = ttk.Label(master=self.labelframe_individual, text='y方向シフト')
        self.label_y_times = ttk.Label(master=self.labelframe_individual, text='y方向倍率')
        linecolors = ('black', 'red', 'blue', 'green', 'purple', 'gray', 'gold')
        linestyles = ('solid', 'dashed', 'dashdot', 'dotted')
        self.linecolor = tk.StringVar(value='black')
        self.linestyle = tk.StringVar(value='solid')
        optionmenu_linecolor = ttk.OptionMenu(self.labelframe_individual, self.linecolor, linecolors[0], *linecolors)
        optionmenu_linestyle = ttk.OptionMenu(self.labelframe_individual, self.linestyle, linestyles[0], *linestyles)
        optionmenu_linecolor.config(width=8)
        optionmenu_linestyle.config(width=8)
        self.y_shift_value = tk.DoubleVar(value=0)
        self.y_times_value = tk.DoubleVar(value=1)
        self.entry_y_shift = ttk.Entry(master=self.labelframe_individual, textvariable=self.y_shift_value, width=7, font=font_md, justify=tk.CENTER)
        self.entry_y_times = ttk.Entry(master=self.labelframe_individual, textvariable=self.y_times_value, width=7, font=font_md, justify=tk.CENTER)
        self.button_apply = ttk.Button(master=self.labelframe_individual, text='適用', width=10, command=self.update_option)
        self.label_color.grid(row=0, column=0, padx=5, pady=5)
        self.label_linestyle.grid(row=1, column=0, padx=5, pady=5)
        self.label_y_shift.grid(row=2, column=0, padx=5, pady=5)
        self.label_y_times.grid(row=3, column=0, padx=5, pady=5)
        optionmenu_linecolor.grid(row=0, column=1, padx=5, pady=5)
        optionmenu_linestyle.grid(row=1, column=1, padx=5, pady=5)
        self.entry_y_shift.grid(row=2, column=1, padx=5, pady=5)
        self.entry_y_times.grid(row=3, column=1, padx=5, pady=5)
        self.button_apply.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # advanced
        self.y_shift_each_value = tk.DoubleVar(value=0)
        self.entry_y_shift_each = ttk.Entry(master=self.labelframe_advanced, textvariable=self.y_shift_each_value, width=7, font=font_md, justify=tk.CENTER)
        self.label_y_shift_each = ttk.Label(master=self.labelframe_advanced, text='ずつy方向にずらす')
        self.button_apply_advanced = ttk.Button(master=self.labelframe_advanced, text='適用', width=10, command=self.apply_advanced)
        self.entry_y_shift_each.grid(row=0, column=0, padx=5, pady=5)
        self.label_y_shift_each.grid(row=0, column=1, padx=5, pady=5)
        self.button_apply_advanced.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # vertical line
        self.label_vline_x = ttk.Label(master=self.labelframe_vline, text='x座標')
        self.label_vline_color = ttk.Label(master=self.labelframe_vline, text='色')
        self.label_vline_linestyle = ttk.Label(master=self.labelframe_vline, text='線種')
        self.vline_x_value = tk.DoubleVar(value=0)
        self.vlinecolor = tk.StringVar(value='black')
        self.vlinestyle = tk.StringVar(value='solid')
        optionmenu_vlinecolor = ttk.OptionMenu(self.labelframe_vline, self.vlinecolor, linecolors[0], *linecolors)
        optionmenu_vlinestyle = ttk.OptionMenu(self.labelframe_vline, self.vlinestyle, linestyles[0], *linestyles)
        optionmenu_linecolor.config(width=8)
        optionmenu_linestyle.config(width=8)
        self.entry_vline_x = ttk.Entry(master=self.labelframe_vline, textvariable=self.vline_x_value, width=7, font=font_md, justify=tk.CENTER)
        self.button_vline_apply = ttk.Button(master=self.labelframe_vline, text='適用', width=10, command=self.apply_vline)
        self.label_vline_x.grid(row=0, column=0, padx=5, pady=5)
        self.label_vline_color.grid(row=1, column=0, padx=5, pady=5)
        self.label_vline_linestyle.grid(row=2, column=0, padx=5, pady=5)
        self.entry_vline_x.grid(row=0, column=1, padx=5, pady=5)
        optionmenu_vlinecolor.grid(row=1, column=1, padx=5, pady=5)
        optionmenu_vlinestyle.grid(row=2, column=1, padx=5, pady=5)
        self.button_vline_apply.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def remove_spec_lines(self) -> None:
        for line in self.spec_lines.values():
            line.remove()
        self.spec_lines = {}

    def remove_vlines(self) -> None:
        for line in self.vlines:
            line.remove()
        self.vlines = []

    def remove_fitting_result(self) -> None:
        for obj in self.fitting_result:
            obj.remove()

    def refresh(self) -> None:
        self.remove_spec_lines()
        self.remove_vlines()
        self.remove_fitting_result()

        xlims = {'min': [1e10], 'max': [0]}
        ylims = {'min': [1e10], 'max': [0]}
        for filename, spec in self.dl.spec_dict.items():
            linewidth = 2 if spec.highlight else 1

            x = spec.xdata
            if self.x_label.get() == self.x_labels[1]:  # エネルギー
                x = 1240 / x
            y = spec.ydata * spec.y_times

            line = self.ax.plot(x, y + spec.y_shift, color=spec.color, linestyle=spec.linestyle, linewidth=linewidth)
            self.spec_lines[filename] = line[0]

            xlims['min'].append(min(x))
            xlims['max'].append(max(x))
            ylims['min'].append(min(y + spec.y_shift))
            ylims['max'].append(max(y + spec.y_shift))

        xlim = [min(xlims['min']), max(xlims['max'])]
        ylim = [min(ylims['min']) * 0.9, max(ylims['max']) * 1.1]

        self.ax.set(xlim=xlim, ylim=ylim)

        self.ax.set_xlabel(self.x_label.get())
        self.ax.set_ylabel(self.y_label.get())

        if self.if_show.get():
            self.fitting_result = self.fitter.draw(self.ax)

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
        if self.xticks.get() != 'auto':
            self.ax_x.set_ticks(np.linspace(*xlim, int(self.entry_xticks.get()) + 1))
        if self.yticks.get() != 'auto':
            self.ax_y.set_ticks(np.linspace(*ylim, int(self.entry_yticks.get()) + 1))

    def update_option(self, event=None) -> None:
        selected_index = self.listbox_file.curselection()
        for index in selected_index:
            filename = self.listbox_file.get(index)
            color = self.linecolor.get()
            linestyle = self.linestyle.get()
            y_shift = self.y_shift_value.get()
            y_times = self.y_times_value.get()
            self.dl.spec_dict[filename].color = color
            self.dl.spec_dict[filename].linestyle = linestyle
            self.dl.spec_dict[filename].y_shift = y_shift
            self.dl.spec_dict[filename].y_times = y_times

        self.refresh()  # TODO: 既存のグラフを消さないようにする

    def apply_advanced(self, event=None) -> None:
        for i in range(len(self.dl.spec_dict)):
            filename = self.listbox_file.get(i)
            self.dl.spec_dict[filename].y_shift = i * self.y_shift_each_value.get()
        self.refresh()

    def apply_vline(self, event=None) -> None:
        x = float(self.entry_vline_x.get())
        color = self.vlinecolor.get()
        linestyle = self.vlinestyle.get()
        line = self.ax.axvline(x=x, color=color, linestyle=linestyle)
        self.vlines.append(line)
        self.canvas.draw()

    def load(self, event: TkinterDnD.DnDEvent=None) -> None:
        if event.data[0] == '{':
            filenames = list(map(lambda x: x.strip('{').strip('}'), event.data.split('} {')))
        else:
            filenames = event.data.split()
        self.dl.load_files(filenames)
        self.check_device(filenames[0])
        self.update_listbox()
        self.refresh()  # TODO: 既存のグラフを消さないようにする

    def select(self, event=None) -> None:
        self.dl.reset_highlight()
        selected_index = self.listbox_file.curselection()
        for index in selected_index:
            filename = self.listbox_file.get(index)
            self.dl.spec_dict[filename].highlight = True
            self.linecolor.set(self.dl.spec_dict[filename].color)
            self.y_shift_value.set(self.dl.spec_dict[filename].y_shift)
            self.y_times_value.set(self.dl.spec_dict[filename].y_times)
        self.refresh()  # TODO: 既存のグラフを消さないようにする

    def reset_selection(self) -> None:
        self.listbox_file.select_clear(0, tk.END)
        self.dl.reset_highlight()
        self.refresh()

    def update_listbox(self) -> None:
        self.listbox_file.delete(0, tk.END)
        loaded_filenames = self.dl.spec_dict.keys()
        for filename in loaded_filenames:
            self.listbox_file.insert(tk.END, filename)

    def check_device(self, filename: str) -> None:
        device = self.dl.spec_dict[filename].device
        if device == 'Renishaw':
            self.x_label.set(self.x_labels[2])
            self.y_label.set(self.y_labels[0])
        elif device == 'Andor':
            self.x_label.set(self.x_labels[0])
            self.y_label.set(self.y_labels[0])
        elif device == 'CCS':
            self.x_label.set(self.x_labels[0])
            self.y_label.set(self.y_labels[0])

    def reset(self) -> None:
        self.dl.reset_option()
        self.refresh()

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
        self.description_fitting_fitted.set('(fitted) ' + description)
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
        self.fitter.set_data(x, y, xlim)

        params = self.get_params_from_text()
        try:
            params = [float(value.replace(r'\x7f308', '')) for sublist in params for value in sublist]
        except ValueError:
            self.msg.set('パラメータが無効です．')
            return

        self.fitter.set_params(params)
        if self.fitter.fit():
            self.msg.set('フィッティングに成功しました．')
        else:
            self.msg.set('フィッティングに失敗しました．パラメータを変えてください．')
            return

        self.show_params(self.text_params_fit, self.fitter.params_fit)

        self.refresh()

    def show_params(self, textbox: tk.Text, params: list[float]) -> None:
        text = ''
        for i in range(self.fitter.num_func):
            for j in range(self.fitter.num_params_per_func):
                text += str(round(params[i * self.fitter.num_params_per_func + j], 3)) + ' '
            text += '\n'
        text += str(round(params[-2], 3)) + ' ' + str(round(params[-1], 3)) + '\n'
        textbox.delete(1.0, tk.END)
        textbox.insert(1.0, text)

    def load_params(self) -> None:
        filename = self.listbox_file.get(0)
        func = self.dl.spec_dict[filename].fitting_function
        fitting_range = self.dl.spec_dict[filename].fitting_range
        params = self.dl.spec_dict[filename].fitting_values
        if len(params) == 0:
            self.msg.set('No params to load.')
            return
        # set range
        self.entry_xmin.insert(0, fitting_range[0])
        self.entry_xmax.insert(0, fitting_range[1])
        self.check_and_fix_range()
        self.canvas.draw()
        # set function
        self.function_fitting.set(func)
        self.function_changed()
        # set parameters
        self.fitter.set_params(params)

        self.show_params(self.text_params, self.fitter.params)

    def save_params(self) -> None:
        for i in range(len(self.dl.spec_dict)):
            filename = self.listbox_file.get(i)
            self.dl.spec_dict[filename].fitting_function = self.function_fitting.get()
            self.dl.spec_dict[filename].fitting_range = self.fitter.xlim
            self.dl.spec_dict[filename].fitting_values = self.fitter.params_fit.tolist()
            self.dl.save(filename)

    def delete(self) -> None:
        selected_index = self.listbox_file.curselection()
        for index in selected_index:
            filename = self.listbox_file.get(index)
            self.dl.delete_file(filename)
            self.spec_lines[filename].remove()
            del self.spec_lines[filename]
        for index in reversed(selected_index):
            self.listbox_file.delete(index)

        self.canvas.draw()

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

    root = Tk()
    root.title('PGraph')

    app = PGraph(master=root)
    root.drop_target_register(DND_FILES)
    root.protocol('WM_DELETE_WINDOW', app.quit)
    root.dnd_bind('<<Drop>>', app.load)

    app.mainloop()


if __name__ == '__main__':
    main()
