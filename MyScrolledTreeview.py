from tkinter import Frame, Pack, Grid, Place
from tkinter.ttk import Treeview, Scrollbar
from tkinter.constants import HORIZONTAL, NSEW, END


class MyTreeview(Treeview):
    def __init__(self, master=None, **kw):
        Treeview.__init__(
            self,
            master,
            columns=['path', 'calibration', 'path_raw', 'path_ref', 'fitting'],
            height=9,
            selectmode='extended',
            **kw)
        # 列定義
        self.column("#0", width=40)
        self.column("path", width=600)
        self.column("calibration", width=100)
        self.column("path_raw", width=100)
        self.column("path_ref", width=100)
        self.column("fitting", width=100)
        # 見出し定義
        self.heading("#0", text="")
        self.heading("path", text="path")
        self.heading("calibration", text="calibration")
        self.heading("path_raw", text="path_raw")
        self.heading("path_ref", text="path_ref")
        self.heading("fitting", text="fitting")

    def load(self, spec_dict: dict, sort: bool = False, descending: bool = False):
        self.delete_all()
        # アイテム挿入
        if sort:
            spec_dict = sorted(spec_dict.items(), key=lambda x: x[0], reverse=descending)
        else:
            spec_dict = spec_dict.items()
        for i, (filename, value) in enumerate(spec_dict):
            calibration = value.calibration[0] if value.calibration is not None else ""
            abs_path_raw = value.abs_path_raw if value.abs_path_raw is not None else ""
            abs_path_ref = value.abs_path_ref if value.abs_path_ref is not None else ""
            fitting = f'{value.fitting_function} {value.fitting_range}' if value.fitting_function is not None else ""
            values = [filename, calibration, abs_path_raw, abs_path_ref, fitting]
            self.insert(
                '',
                END,
                iid=str(i),
                text=str(i),
                values=values,
                open=True,
                )

    def delete_all(self):
        # アイテム削除
        for i in self.get_children():
            self.delete(i)

    def get_filename(self, iid: str = None):
        if len(self.get_children()) == 0:
            return None
        if iid is None or iid == '':
            iid = self.get_children()[0]
            self.selection_add(self.get_children())  # 全選択
        return self.item(iid)['values'][0]
