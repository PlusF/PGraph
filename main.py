import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
from tkinterdnd2 import Tk, DND_FILES, TkinterDnD
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from MyToolbar import MyToolbar
from MyTreeview import MyTreeview
from dataloader import DataLoader
from fitting import Fit

font_lg = ('Arial', 24)
font_md = ('Arial', 16)
font_sm = ('Arial', 12)

linestyles = ('solid', 'dashed', 'dashdot', 'dotted')

functions = ('Lorentzian', 'Gaussian', "Voigt")

plt.rcParams['font.family'] = 'Arial'

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


def create_line_config_widget(parent):
    # 線の設定ウィジェットと更新用の関数を生成する

    linecolor = ['black']  # mutableなオブジェクトを渡す

    def change_linecolor(event) -> None:
        rgb, code = colorchooser.askcolor(title='色を選択')
        set_linecolor(code)

    def set_linecolor(code) -> None:
        label_show_linecolor.config(background=code)
        linecolor[0] = code

    label_color = ttk.Label(master=parent, text='色')
    label_linestyle = ttk.Label(master=parent, text='線種')
    label_show_linecolor = ttk.Label(master=parent, style='Color.TLabel')
    label_show_linecolor.bind('<Button-1>', change_linecolor)
    linestyle = tk.StringVar(value='solid')
    optionmenu_linestyle = ttk.OptionMenu(parent, linestyle, linestyles[0], *linestyles)
    optionmenu_linestyle.config(width=5)
    optionmenu_linestyle['menu'].config(font=font_sm)
    label_color.grid(row=0, column=0, padx=5, pady=5)
    label_show_linecolor.grid(row=0, column=1, padx=5, pady=5)
    label_linestyle.grid(row=1, column=0, padx=5, pady=5)
    optionmenu_linestyle.grid(row=1, column=1, padx=5, pady=5)

    return label_show_linecolor, linecolor, change_linecolor, set_linecolor, linestyle


class PGraph(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.dl = DataLoader()
        self.fitter = Fit()

        self.ax: plt.AxesSubplot

        self.spec_lines = {}
        self.vlines = []
        self.hlines = []
        self.fitting_result = []

        self.create_graph()
        self.create_config()

        self.master.bind("<Return>", self.apply_option)

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
        style = ttk.Style()
        style.theme_use('winnative')
        style.configure('TButton', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')
        style.configure('R.TButton', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='red')
        style.configure('TLabel', font=font_sm, padding=[0, 4, 0, 4], foreground='black')
        style.configure('Color.TLabel', font=font_lg, padding=[0, 0, 0, 0], width=4, background='black')
        style.configure('TEntry', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TCheckbutton', font=font_md, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TMenubutton', font=font_md, padding=[20, 4, 0, 4], foreground='black')
        style.configure('TTreeview', font=font_md, foreground='black')

        # all parent frames
        frame_graph = tk.LabelFrame(master=self.master, text='Graph Area')
        frame_data = tk.LabelFrame(master=self.master, text='Loaded Data')
        frame_fitting = tk.LabelFrame(master=self.master, text='Fitting')
        frame_graph.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
        frame_data.grid(row=1, rowspan=2, column=0, padx=10, sticky=tk.NSEW)
        frame_fitting.grid(row=2, column=1, padx=10, sticky=tk.NSEW)

        # graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graph)
        frame_graph_setting = tk.LabelFrame(master=frame_graph, text='Graph Setting')
        toolbar = MyToolbar(self.canvas, frame_graph, pack_toolbar=False)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        toolbar.grid(row=1, column=0)
        frame_graph_setting.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)

        # data
        self.treeview_file = MyTreeview(master=frame_data)
        self.treeview_file.bind('<Button-1>', self.select)
        self.treeview_file.bind('<Delete>', self.delete)
        self.treeview_file.bind('<BackSpace>', self.delete)
        self.treeview_file.bind('<Control-a>', lambda _: self.treeview_file.selection_add(self.treeview_file.get_children()))
        self.treeview_file.bind('Enter', self.apply_option)
        self.treeview_file.grid(row=0, column=0, columnspan=5)
        button_delete = ttk.Button(master=frame_data, text='削除', command=self.delete)
        button_sort_ascending = ttk.Button(master=frame_data, text='ソート（昇順）', command=self.sort_file_ascending)
        button_sort_descending = ttk.Button(master=frame_data, text='ソート（降順）', command=self.sort_file_descending)
        button_reset_selection = ttk.Button(master=frame_data, text='ハイライト解除', command=self.reset_selection)
        button_quit = ttk.Button(master=frame_data, text='終了', style='R.TButton', command=self.quit)
        button_delete.grid(row=2, column=0, padx=5, pady=5)
        button_sort_ascending.grid(row=2, column=1, padx=5, pady=5)
        button_sort_descending.grid(row=2, column=2, padx=5, pady=5)
        button_reset_selection.grid(row=2, column=3, padx=5, pady=5)
        button_quit.grid(row=2, column=4, padx=5, pady=5)

        # fitting
        self.function_fitting = tk.StringVar(value=functions[0])
        optionmenu_fitting = ttk.OptionMenu(frame_fitting, self.function_fitting, functions[0], *functions, command=self.function_changed)
        optionmenu_fitting.config(width=10)
        optionmenu_fitting['menu'].config(font=font_sm)
        self.description_fitting = tk.StringVar(value='位置 強度 幅 (BG)')
        self.description_fitting_fitted = tk.StringVar(value='(fitted) 位置 強度 幅 (BG)')
        label_description_1 = ttk.Label(master=frame_fitting,  textvariable=self.description_fitting)
        label_description_2 = ttk.Label(master=frame_fitting, textvariable=self.description_fitting_fitted)
        self.text_params = tk.Text(master=frame_fitting, width=30, height=5, font=font_md)
        self.text_params.insert(1.0, '1.7 20000 1\n1.8 3000 1\n0 0')
        self.text_params_fit = tk.Text(master=frame_fitting, width=30, height=5, font=font_md)
        self.button_fit = ttk.Button(master=frame_fitting, text='Fit', command=self.fit)
        self.if_show = tk.BooleanVar(value=False)
        self.check_fit = ttk.Checkbutton(master=frame_fitting, variable=self.if_show, text='結果を描画', command=self.refresh)
        button_load = ttk.Button(master=frame_fitting, text='LOAD', command=self.load_params)
        button_save = ttk.Button(master=frame_fitting, text='SAVE', command=self.save_params)
        optionmenu_fitting.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        label_description_1.grid(row=1, column=0, columnspan=2)
        label_description_2.grid(row=1, column=2, columnspan=2)
        self.text_params.grid(row=2, column=0, columnspan=2)
        self.text_params_fit.grid(row=2, column=2, columnspan=2)
        self.button_fit.grid(row=3, column=0, padx=5, pady=5)
        self.check_fit.grid(row=3, column=1, padx=5, pady=5)
        button_load.grid(row=3, column=2, padx=5, pady=5)
        button_save.grid(row=3, column=3, padx=5, pady=5)

        # labelframes in graph_setting
        frame_graph_setting_1 = ttk.Frame(master=frame_graph_setting)
        frame_graph_setting_2 = ttk.Frame(master=frame_graph_setting)
        frame_graph_setting_3 = ttk.Frame(master=frame_graph_setting)
        frame_graph_setting_1.grid(row=0, column=0, padx=5, sticky=tk.NSEW)
        frame_graph_setting_2.grid(row=0, column=1, padx=5, sticky=tk.NSEW)
        frame_graph_setting_3.grid(row=0, column=2, padx=5, sticky=tk.NSEW)
        self.labelframe_label = ttk.LabelFrame(master=frame_graph_setting_1, text='軸ラベル')
        self.labelframe_labelsize = ttk.LabelFrame(master=frame_graph_setting_1, text='ラベルサイズ')
        self.labelframe_range = ttk.LabelFrame(master=frame_graph_setting_1, text='グラフ範囲')
        self.labelframe_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_labelsize.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_range.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_individual = ttk.LabelFrame(master=frame_graph_setting_2, text='個別設定')
        self.labelframe_advanced = ttk.LabelFrame(master=frame_graph_setting_2, text='一括設定')
        self.button_reset_option = ttk.Button(master=frame_graph_setting_2, text='リセット', width=10, command=self.reset_option)
        self.labelframe_individual.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_advanced.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.button_reset_option.grid(row=3, column=0)
        self.labelframe_vline = ttk.LabelFrame(master=frame_graph_setting_3, text='縦線追加')
        self.labelframe_hline = ttk.LabelFrame(master=frame_graph_setting_3, text='横線追加')
        self.button_reset_lines = ttk.Button(master=frame_graph_setting_3, text='リセット', width=10, command=self.reset_lines)
        self.labelframe_vline.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.labelframe_hline.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.button_reset_lines.grid(row=2, column=0, padx=5, pady=5, sticky=tk.S)

        # xaxis, yaxis
        self.x_labels = ('Wavelength [nm]', 'Energy [eV]', 'Raman Shift [cm-1]')
        self.y_labels = ('Intensity [arb. units]', 'Counts', 'Absorbance', 'Transmittance')
        self.x_label = tk.StringVar()
        optionmenu_x_label = ttk.OptionMenu(self.labelframe_label, self.x_label, self.x_labels[0], *self.x_labels, command=self.apply_option)
        optionmenu_x_label.config(width=16)
        optionmenu_x_label['menu'].config(font=font_sm)
        self.y_label = tk.StringVar()
        optionmenu_y_label = ttk.OptionMenu(self.labelframe_label, self.y_label, self.y_labels[0], *self.y_labels, command=self.apply_option)
        optionmenu_y_label.config(width=16)
        optionmenu_y_label['menu'].config(font=font_sm)
        optionmenu_x_label.grid(row=0, column=0, padx=5, pady=5)
        optionmenu_y_label.grid(row=1, column=0, padx=5, pady=5)

        # xaxis, yaxis label size
        label_x_label = ttk.Label(master=self.labelframe_labelsize, text='x軸')
        label_y_label = ttk.Label(master=self.labelframe_labelsize, text='y軸')
        label_xtick_label = ttk.Label(master=self.labelframe_labelsize, text='x軸目盛')
        label_ytick_label = ttk.Label(master=self.labelframe_labelsize, text='y軸目盛')
        self.x_labelsize = tk.StringVar(value='35')
        self.y_labelsize = tk.StringVar(value='35')
        self.xtick_labelsize = tk.StringVar(value='25')
        self.ytick_labelsize = tk.StringVar(value='25')
        entry_x_labelsize = ttk.Entry(master=self.labelframe_labelsize, textvariable=self.x_labelsize, font=font_md, width=6, justify=tk.CENTER)
        entry_y_labelsize = ttk.Entry(master=self.labelframe_labelsize, textvariable=self.y_labelsize, font=font_md, width=6, justify=tk.CENTER)
        entry_xtick_labelsize = ttk.Entry(master=self.labelframe_labelsize, textvariable=self.xtick_labelsize, font=font_md, width=6, justify=tk.CENTER)
        entry_ytick_labelsize = ttk.Entry(master=self.labelframe_labelsize, textvariable=self.ytick_labelsize, font=font_md, width=6, justify=tk.CENTER)
        button_apply = ttk.Button(master=self.labelframe_labelsize, text='適用', width=10, command=self.refresh)
        label_x_label.grid(row=0, column=0, padx=5, pady=5)
        entry_x_labelsize.grid(row=0, column=1, padx=5, pady=5)
        label_y_label.grid(row=1, column=0, padx=5, pady=5)
        entry_y_labelsize.grid(row=1, column=1, padx=5, pady=5)
        label_xtick_label.grid(row=2, column=0, padx=5, pady=5)
        entry_xtick_labelsize.grid(row=2, column=1, padx=5, pady=5)
        label_ytick_label.grid(row=3, column=0, padx=5, pady=5)
        entry_ytick_labelsize.grid(row=3, column=1, padx=5, pady=5)
        button_apply.grid(row=4, column=0, columspan=2)

        # range
        label_min = ttk.Label(master=self.labelframe_range, text='min')
        label_max = ttk.Label(master=self.labelframe_range, text='max')
        label_ticks = ttk.Label(master=self.labelframe_range, text='分割数')
        label_xrange = ttk.Label(master=self.labelframe_range, text='x')
        label_yrange = ttk.Label(master=self.labelframe_range, text='y')
        self.entry_xmin = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.entry_xmax = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.xticks = tk.StringVar(value='auto')
        entry_xticks = ttk.Entry(master=self.labelframe_range, textvariable=self.xticks, width=5, font=font_md, justify=tk.CENTER)
        self.entry_ymin = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.entry_ymax = ttk.Entry(master=self.labelframe_range, width=7, font=font_md, justify=tk.CENTER)
        self.yticks = tk.StringVar(value='auto')
        entry_yticks = ttk.Entry(master=self.labelframe_range, textvariable=self.yticks, width=5, font=font_md, justify=tk.CENTER)
        label_min.grid(row=0, column=1)
        label_max.grid(row=0, column=2)
        label_ticks.grid(row=0, column=3)
        label_xrange.grid(row=1, column=0)
        self.entry_xmin.grid(row=1, column=1)
        self.entry_xmax.grid(row=1, column=2)
        entry_xticks.grid(row=1, column=3)
        label_yrange.grid(row=2, column=0)
        self.entry_ymin.grid(row=2, column=1)
        self.entry_ymax.grid(row=2, column=2)
        entry_yticks.grid(row=2, column=3)

        # individual
        label_y_shift = ttk.Label(master=self.labelframe_individual, text='yシフト')
        label_y_times = ttk.Label(master=self.labelframe_individual, text='y倍率')
        self.y_shift_value = tk.DoubleVar(value=0)
        self.y_times_value = tk.DoubleVar(value=1)
        entry_y_shift = ttk.Entry(master=self.labelframe_individual, textvariable=self.y_shift_value, width=7, font=font_md, justify=tk.CENTER)
        entry_y_times = ttk.Entry(master=self.labelframe_individual, textvariable=self.y_times_value, width=7, font=font_md, justify=tk.CENTER)
        button_apply = ttk.Button(master=self.labelframe_individual, text='適用', width=10, command=self.apply_option)
        self.label_show_linecolor, self.linecolor, self.change_linecolor, self.set_linecolor, self.linestyle = create_line_config_widget(self.labelframe_individual)
        # create_line_config_widgetが2行目まで作成するので、3行目以降を作成する
        label_y_shift.grid(row=2, column=0, padx=5, pady=5)
        entry_y_shift.grid(row=2, column=1, padx=5, pady=5)
        label_y_times.grid(row=3, column=0, padx=5, pady=5)
        entry_y_times.grid(row=3, column=1, padx=5, pady=5)
        button_apply.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # advanced
        self.y_shift_each_value = tk.DoubleVar(value=0)
        entry_y_shift_each = ttk.Entry(master=self.labelframe_advanced, textvariable=self.y_shift_each_value, width=7, font=font_md, justify=tk.CENTER)
        label_y_shift_each = ttk.Label(master=self.labelframe_advanced, text='ずつyシフト')
        button_apply_advanced = ttk.Button(master=self.labelframe_advanced, text='適用', width=10, command=self.apply_option_advanced)
        entry_y_shift_each.grid(row=0, column=0, padx=5, pady=5)
        label_y_shift_each.grid(row=0, column=1, padx=5, pady=5)
        button_apply_advanced.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # vertical line
        label_vline_x = ttk.Label(master=self.labelframe_vline, text='x座標')
        self.vline_x_value = tk.DoubleVar(value=0)
        entry_vline_x = ttk.Entry(master=self.labelframe_vline, textvariable=self.vline_x_value, width=7, font=font_md, justify=tk.CENTER)
        button_vline_apply = ttk.Button(master=self.labelframe_vline, text='適用', width=10, command=self.apply_vline)
        self.label_show_vlinecolor, self.vlinecolor, self.change_vlinecolor, self.set_vlinecolor, self.vlinestyle = create_line_config_widget(self.labelframe_vline)
        # create_line_config_widgetが2行目まで作成するので、3行目以降を作成する
        label_vline_x.grid(row=2, column=0, padx=5, pady=5)
        entry_vline_x.grid(row=2, column=1, padx=5, pady=5)
        button_vline_apply.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # horizontal line
        label_hline_y = ttk.Label(master=self.labelframe_hline, text='y座標')
        self.hline_y_value = tk.DoubleVar(value=0)
        entry_hline_y = ttk.Entry(master=self.labelframe_hline, textvariable=self.hline_y_value, width=7, font=font_md, justify=tk.CENTER)
        button_hline_apply = ttk.Button(master=self.labelframe_hline, text='適用', width=10, command=self.apply_hline)
        self.label_show_hlinecolor, self.hlinecolor, self.change_hlinecolor, self.set_hlinecolor, self.hlinestyle = create_line_config_widget(self.labelframe_hline)
        # create_line_config_widgetが2行目まで作成するので、3行目以降を作成する
        label_hline_y.grid(row=2, column=0, padx=5, pady=5)
        entry_hline_y.grid(row=2, column=1, padx=5, pady=5)
        button_hline_apply.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def remove_spec_lines(self) -> None:
        for line in self.spec_lines.values():
            line.remove()
        self.spec_lines = {}

    def remove_vlines(self) -> None:
        for line in self.vlines:
            line.remove()
        self.vlines = []

    def remove_hlines(self) -> None:
        for line in self.hlines:
            line.remove()
        self.hlines = []

    def remove_fitting_result(self) -> None:
        for obj in self.fitting_result:
            obj.remove()
        self.fitting_result = []

    def refresh(self, *remove_funcs) -> None:
        self.remove_spec_lines()
        for f in remove_funcs:  # 状況によって消したい線・残したい線が変わる
            f()
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

        self.remove_fitting_result()
        if self.if_show.get():
            self.fitting_result = self.fitter.draw(self.ax)

        xlim = [min(xlims['min']), max(xlims['max'])]
        ylim = [min(ylims['min']) * 0.9, max(ylims['max']) * 1.1]
        self.set_range(xlim, ylim)

        self.canvas.draw()

    def set_range(self, xlim, ylim) -> None:
        try:
            xmin = float(self.entry_xmin.get())
        except ValueError:
            xmin = xlim[0]
        try:
            xmax = float(self.entry_xmax.get())
        except ValueError:
            xmax = xlim[1]
        try:
            ymin = float(self.entry_ymin.get())
        except ValueError:
            ymin = ylim[0]
        try:
            ymax = float(self.entry_ymax.get())
        except ValueError:
            ymax = ylim[1]
        self.ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax))

        try:
            num_xticks = int(self.xticks.get()) + 1
        except ValueError:
            num_xticks = 5
        try:
            num_yticks = int(self.yticks.get()) + 1
        except ValueError:
            num_yticks = 5

        xticks = np.linspace(xmin, xmax, num_xticks)
        yticks = np.linspace(ymin, ymax, num_yticks)

        if self.y_label.get() == self.y_labels[0]:  # arbitrary units
            yticks = []

        try:
            self.ax.set_xlabel(self.x_label.get(), fontsize=int(self.x_labelsize.get()))
            self.ax.set_ylabel(self.y_label.get(), fontsize=int(self.y_labelsize.get()))
            self.ax.set_xticks(xticks)
            self.ax.set_yticks(yticks)
            self.ax.tick_params(axis='x', labelsize=int(self.xtick_labelsize.get()))
            self.ax.tick_params(axis='y', labelsize=int(self.ytick_labelsize.get()))
        except ValueError:
            messagebox.showerror('エラー', 'ラベルサイズには整数を入力してください。')

    def get_graph_range(self) -> [list, list]:
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

    def apply_option(self, event=None) -> None:
        selected_iid = self.treeview_file.selection()
        for iid in selected_iid:
            filename = self.treeview_file.get_filename(iid)
            linestyle = self.linestyle.get()
            y_shift = self.y_shift_value.get()
            y_times = self.y_times_value.get()
            self.dl.spec_dict[filename].color = self.linecolor[0]
            self.dl.spec_dict[filename].linestyle = linestyle
            self.dl.spec_dict[filename].y_shift = y_shift
            self.dl.spec_dict[filename].y_times = y_times

        self.refresh()

    def reset_option(self) -> None:
        self.dl.reset_option()
        self.refresh()

    def apply_option_advanced(self, event=None) -> None:
        for i, iid in enumerate(self.treeview_file.get_children()):
            filename = self.treeview_file.get_filename(iid)
            self.dl.spec_dict[filename].y_shift = i * self.y_shift_each_value.get()
        self.refresh()

    def apply_vline(self, event=None) -> None:
        x = float(self.vline_x_value.get())
        color = self.vlinecolor[0]
        linestyle = self.vlinestyle.get()
        line = self.ax.axvline(x=x, color=color, linestyle=linestyle)
        self.vlines.append(line)
        self.canvas.draw()

    def apply_hline(self, event=None) -> None:
        y = float(self.hline_y_value.get())
        color = self.hlinecolor[0]
        linestyle = self.hlinestyle.get()
        line = self.ax.axhline(y=y, color=color, linestyle=linestyle)
        self.hlines.append(line)
        self.canvas.draw()

    def reset_lines(self) -> None:
        self.refresh(self.remove_vlines, self.remove_hlines)

    def load(self, event: TkinterDnD.DnDEvent=None) -> None:
        if event.data[0] == '{':
            filenames = list(map(lambda x: x.strip('{').strip('}'), event.data.split('} {')))
        else:
            filenames = event.data.split()
        self.dl.load_files(filenames)
        self.treeview_file.load(self.dl.spec_dict)
        self.check_device(filenames[0])
        self.refresh()

    def select(self, event=None) -> None:
        self.dl.reset_highlight()
        # focusやselectionでは現在の選択状態を得られない
        iid = self.treeview_file.identify_row(event.y)
        filename = self.treeview_file.get_filename(iid)
        if filename is None:
            return
        self.dl.spec_dict[filename].highlight = True
        self.set_linecolor(self.dl.spec_dict[filename].color)
        self.y_shift_value.set(self.dl.spec_dict[filename].y_shift)
        self.y_times_value.set(self.dl.spec_dict[filename].y_times)
        self.refresh()

    def reset_selection(self) -> None:
        self.treeview_file.selection_remove(self.treeview_file.selection())
        self.dl.reset_highlight()
        self.refresh()

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

    def get_params_from_text(self) -> list:
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
        num_spec = len(self.dl.spec_dict)
        if num_spec == 0:
            messagebox.showerror('Error', 'スペクトルが読み込まれていません．')
            return
        elif num_spec > 2:
            messagebox.showwarning('Warning', '全てのスペクトルを結合してフィッティングを行います．')
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
            messagebox.showerror('Error', 'パラメータが無効です．数値以外の文字が含まれている可能性があります．')
            return

        self.fitter.set_params(params)
        if self.fitter.fit():
            messagebox.showinfo('Info', 'フィッティングに成功しました．')
        else:
            messagebox.showerror('Error', 'フィッティングに失敗しました．パラメータを変えてください．')
            return

        self.show_params(self.text_params_fit, self.fitter.params_fit)

        self.refresh()

    def show_params(self, textbox: tk.Text, params: list) -> None:
        text = ''
        for i in range(self.fitter.num_func):
            for j in range(self.fitter.num_params_per_func):
                text += str(round(params[i * self.fitter.num_params_per_func + j], 3)) + ' '
            text += '\n'
        text += str(round(params[-2], 3)) + ' ' + str(round(params[-1], 3)) + '\n'
        textbox.delete(1.0, tk.END)
        textbox.insert(1.0, text)

    def load_params(self) -> None:
        filename = self.treeview_file.get_filename()
        func = self.dl.spec_dict[filename].fitting_function
        fitting_range = self.dl.spec_dict[filename].fitting_range
        params = self.dl.spec_dict[filename].fitting_values
        if len(params) == 0:
            messagebox.showerror('Error', 'パラメータが見つかりませんでした．')
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
        # 現在ロードされているすべてのファイルにパラメータを保存
        if self.fitter.params_fit is None:
            messagebox.showerror('Error', 'フィッティングを行ってください．')
            return
        filenames_new = []
        for filename, _ in self.dl.spec_dict.items():
            self.dl.spec_dict[filename].fitting_function = self.function_fitting.get()
            self.dl.spec_dict[filename].fitting_range = self.fitter.xlim
            self.dl.spec_dict[filename].fitting_values = self.fitter.params_fit.tolist()
            filename_new = self.dl.save(filename)
            filenames_new.append(filename_new)
        messagebox.showinfo('Info', f'パラメータを追記したファイルを{", ".join(filenames_new)}に保存しました．')

    def delete(self, event=None) -> None:
        for iid in self.treeview_file.selection():
            filename = self.treeview_file.get_filename(iid)
            del self.dl.spec_dict[filename]
            self.treeview_file.delete(iid)

        self.refresh()

    def sort_file_ascending(self) -> None:
        self.treeview_file.load(self.dl.spec_dict, True)

    def sort_file_descending(self) -> None:
        self.treeview_file.load(self.dl.spec_dict, True, True)

    def quit(self) -> None:
        self.master.quit()
        self.master.destroy()


def main():
    root = Tk()
    root.title('PGraph')

    app = PGraph(master=root)
    root.drop_target_register(DND_FILES)
    root.protocol('WM_DELETE_WINDOW', app.quit)
    root.dnd_bind('<<Drop>>', app.load)
    app.grid(sticky=tk.NSEW)
    app.mainloop()


if __name__ == '__main__':
    main()
