import pandas as pd


class DataLoader:
    def __init__(self):
        self.dict_df_ = {}

    def load_file(self, filename: str):
        if filename.split('.')[-1] != 'asc':
            print(f'ascファイルを選択してください．：{filename}')
            return False

        if filename in self.dict_df_:
            print(f'このファイルは既に読み込まれています．：{filename}')
            return False

        df = self.load_asc(filename)
        self.dict_df_[filename] = {'data': df, 'color': 'k', 'y_shift': 0, 'fit_params': []}
        return True

    def load_files(self, filenames: list):
        ret = True
        for filename in filenames:
            if not self.load_file(filename):
                ret = False
        return ret

    def load_asc(self, filename: str):
        df = pd.read_csv(filename, sep='[:\t]', header=None, engine='python')
        if df.shape[0] > 1024:  # sifからbatch conversionで変換したascファイルのとき
            print('Solisから出力されたファイルを読み込みました．')
            df = df.loc[26:, 0:1]
            df = df.reset_index(drop=True)
        elif df.shape[0] == 1024:  # AutoRayleighで出力したascファイルのとき
            print('AutoRayleighから出力されたファイルを読み込みました．\n\tキャリブレーションが必要です．')
        else:
            print('未確認のファイル形式です．')
        df.columns = ['x', 'y']

        return df

    def get_dict(self):
        return self.dict_df_

    def get_names(self):
        return self.dict_df_.keys()

    def get_df(self, key: str):
        return self.dict_df_[key]['data']

    def get_dfs(self):
        dfs = [item['data'] for item in self.dict_df_.values()]
        return dfs

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

    def change_y_shift(self, filename: str, y_shift: str):
        y_shift = float(y_shift)
        self.dict_df_[filename]['y_shift'] = y_shift
        return True


def test():
    dl = DataLoader()
    ret = dl.load_file(r"G:\共有ドライブ\Laboratory\Individuals\kaneda\Data_B4\卒論_slit_gas-flow_02\Rayleigh\220113atmND50\2-1_01_s0.1-45\raw\2-1_01_s0.1-45_500.asc")
    print(ret)
    ret = dl.load_files(
        [
            r"G:\共有ドライブ\Laboratory\Individuals\kaneda\Data_M1\220603\AutoRayleighbackground.asc",
            r"G:\共有ドライブ\Laboratory\Individuals\kaneda\Data_B4\卒論_slit_gas-flow_02\Rayleigh\220112Water384ND50\2-1_01_s0.1-300\raw\2-1_01_s0.1-300_500.asc",
            r"G:\共有ドライブ\Laboratory\Individuals\kaneda\Data_B4\卒論_slit_gas-flow_02\Rayleigh\220112Water384ND50\2-1_01_s0.1-300\raw\2-1_01_s0.1-300_630.asc",
            r"G:\共有ドライブ\Laboratory\Individuals\kaneda\Data_B4\卒論_slit_gas-flow_02\Rayleigh\220112Water384ND50\2-1_01_s0.1-300\raw\2-1_01_s0.1-300_500.asc"
        ]
    )
    print(ret)
    dict_df = dl.get_dict()
    for name, df in dict_df.items():
        print(name)
        print(df)


if __name__ == '__main__':
    test()
