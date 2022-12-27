import os
import pandas as pd


class DataLoader:
    def __init__(self):
        self.dict_df_ = {}

    def load_file(self, filename: str):
        if filename.split('.')[-1] not in ['asc', 'txt']:
            print(f'ascまたはtxtファイルを選択してください．：{filename}')
            return False

        if filename in self.dict_df_:
            print(f'このファイルは既に読み込まれています．：{filename}')
            return False

        df = self.load_asc(filename)
        self.dict_df_[filename] = {'data': df, 'color': 'black', 'linestyle': 'solid', 'y_shift': 0, 'y_times': 1, 'highlight': False}
        return True

    def load_files(self, filenames: list):
        ret = True
        for filename in filenames:
            if not self.load_file(filename):
                ret = False
        return ret

    def load_asc(self, filename: str):
        df = pd.read_csv(filename, sep='[:\t]', header=None, engine='python')
        if df.shape[0] == 1057:  # 最近のファイルは情報量が増えた
            print('Solisから出力されたファイルを読み込みました．')
            df = df.loc[30:, 0:1]
            df = df.reset_index(drop=True)
        if df.shape[0] > 1024:  # sifからbatch conversionで変換したascファイルのとき
            print('Solisから出力されたファイルを読み込みました．')
            df = df.loc[26:, 0:1]
            df = df.reset_index(drop=True)
        elif df.shape[0] == 1024:  # AutoRayleighで出力したascファイルのとき
            print('AutoRayleighから出力されたファイルを読み込みました．')
        elif df.shape[0] == 1015:
            print('Renishaw Ramanから出力されたファイルを読み込みました．')
        else:
            print('未確認のファイル形式です．')
        df.columns = ['x', 'y']
        df = df.astype(float)

        return df

    def get_dict(self):
        return self.dict_df_

    def get_len_dict(self):
        return len(self.dict_df_)

    def get_names(self):
        return list(self.dict_df_.keys())

    def get_df(self, key: str):
        return self.dict_df_[key]['data']

    def get_color(self, key: str):
        return self.dict_df_[key]['color']

    def get_linestyle(self, key: str):
        return self.dict_df_[key]['linestyle']

    def get_y_shift(self, key: str):
        return self.dict_df_[key]['y_shift']

    def get_y_times(self, key: str):
        return self.dict_df_[key]['y_times']

    def get_dfs(self):
        dfs = [item['data'] for item in self.dict_df_.values()]
        return dfs

    def get_first_file_directory(self):
        return os.path.dirname(self.get_names()[0])

    def reset_option(self):
        for name, item in self.dict_df_.items():
            self.dict_df_[name] = {'data': item['data'], 'color': 'black', 'linestyle': 'solid', 'y_shift': 0, 'y_times': 1, 'highlight': False}

    def delete_file(self, key: str):
        if key not in self.dict_df_:
            print(f'削除するファイルが見つかりません．：{key}')
            return False
        self.dict_df_.pop(key)
        print(f'{key} を削除しました．')
        return True

    def delete_files(self, filenames: list):
        ret = True
        for filename in filenames:
            if not self.delete_file(filename):
                ret = False
        return ret

    def change_color(self, filename: str, color: str):
        self.dict_df_[filename]['color'] = color
        return True

    def change_linestyle(self, filename: str, linestyle: str):
        self.dict_df_[filename]['linestyle'] = linestyle
        return True

    def change_y_shift(self, filename: str, y_shift: float):
        self.dict_df_[filename]['y_shift'] = y_shift
        return True

    def change_y_times(self, filename: str, y_times: float):
        self.dict_df_[filename]['y_times'] = y_times
        return True

    def set_highlight(self, filename: str):
        self.dict_df_[filename]['highlight'] = True
        return True

    def reset_highlight(self):
        for filename, item in self.dict_df_.items():
            self.dict_df_[filename]['highlight'] = False
        return True
