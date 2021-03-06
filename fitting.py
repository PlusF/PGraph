from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd


def lorentzian_func(x, x0, a, w):
    y = w ** 2 / (4 * (x - x0) ** 2 + w ** 2)
    return a * y


class Fit:
    def __init__(self):
        self.x = None
        self.y = None
        self.params = None
        self.num_func = 0
        self.func = lorentzian_func

        self.y_sum = None
        self.y_list = []

        self.params_fit = None
        self.pcov = None

    def load_data(self, x, y):
        self.x = x
        self.y = y

    def set_params(self, params):
        self.params = params
        self.num_func = int(len(self.params) / 3)

    def superposition(self, x, *params):
        # 全てのyを足し合わせ
        self.y_sum = np.zeros_like(x)
        for i in range(self.num_func):
            x0 = params[i * 3 + 0]
            a = params[i * 3 + 1]
            w = params[i * 3 + 2]
            self.y_sum += self.func(x, x0, a, w)

        # バックグラウンドを追加
        self.y_sum = self.y_sum + params[-1]

        return self.y_sum

    def fit(self):
        if self.params is None:
            print('パラメータをセットしてください．')
            return False
        try:
            self.params_fit, self.pcov = curve_fit(self.superposition, self.x, self.y, p0=self.params)
        except RuntimeError:
            print('パラメータを変えて実行しなおしてください．')
            return False

        print('フィッティングに成功しました．')
        return True

    def make_y_list(self):
        if self.x is None or self.y is None or self.params_fit is None:
            print('フィッティング後でなければ描画はできません．')
            return False

        self.y_list = []
        self.y_list.append(self.superposition(self.x, *self.params_fit))
        for i in range(self.num_func):
            x0 = self.params_fit[i * 3 + 0]
            a = self.params_fit[i * 3 + 1]
            w = self.params_fit[i * 3 + 2]
            y = self.func(self.x, x0, a, w)
            self.y_list.append(y)

        # バックグラウンドを追加
        self.y_list.append(np.ones_like(self.x) * self.params_fit[-1])

    def get_y_list(self):
        return self.y_list

    def draw(self, ax):
        self.make_y_list()

        for i, y in enumerate(self.y_list):
            if i == 0 or i == len(self.y_list) - 1:
                ax.plot(self.x, y, color='r')
            else:
                ax.fill_between(self.x, y, self.y_list[-1], facecolor=cm.rainbow(i / len(self.y_list)), alpha=0.6)

    def save_params(self, filename):
        if self.params_fit is None:
            print('フィッティングを行ってからセーブしてください．')
            return False
        params_str = [str(p) + '\n' for p in self.params_fit]
        with open(filename, 'w') as f:
            f.writelines(params_str)
        print('パラメータを保存しました．')
        return True

    def load_params(self, filename):
        with open(filename, 'r') as f:
            params_str = f.readlines()
        print('パラメータを読み込みました．')
        self.set_params([float(p) for p in params_str])
        self.params_fit = [float(p) for p in params_str]


def test():
    f = Fit()
    # x = np.linspace(0, 10, 10000)
    # y = lorentzian_func(x, 5, 10, 1) + lorentzian_func(x, 3, 5, 1)
    df = pd.read_csv(r"C:\Users\root\Downloads\test.txt", sep='\t')
    df.columns = ['x', 'y']
    x = df.x
    y = df.y
    # print(df)
    plt.plot(x, y)
    plt.show()

    f.load_data(x, y)
    f.set_params([1600, 300, 1,
                  2500, 100, 2,
                  2700, 800, 1,
                  0])
    f.fit()
    fig, ax = plt.subplots()
    f.draw(ax)
    plt.show()
    f.save_params('./params.asc')
    #
    # f.load_params('./params.asc')
    # f.fit()
    # fig, ax = plt.subplots()
    # f.draw(ax)
    # plt.show()


if __name__ == '__main__':
    test()
