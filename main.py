import csv
import json

class DataProcessor:
    def __init__(self):
        self.Quotas = []
        self.players = []
        self.Moon = []
        self.Weather = []
        self.Layout = []
        self.Items = []
        self.Bees = []
        self.Collected = []
        self.BL = []
        self.Sold = []
        self.Deaths = []
        self.tree_Deaths = []
        self.Notes = []

    def read_csv_to_2d_array(self):
        with open(self.file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            data = list(reader)

        if not data:
            return []

        # Transpose the data to get columns as the first dimension
        columns = list(zip(*data))

        # Convert tuples to lists
        columns = [list(column) for column in columns]

        return columns

    def is_number(self, data):
        try:
            float(data)
            return True
        except ValueError:
            return False

    def process_data(self, data_2d_array, idx, Exclude):
        Out = [[] for _ in range((len(data_2d_array[idx]) - 1) // 3 + 2)]
        j = 0
        for i in range(len(data_2d_array[idx])):
            data = data_2d_array[idx][i]
            if data not in Exclude:
                Out[int((j) / 3)].append(data)
                j += 1
        return Out

    def process_numbers(self, data_2d_array, idx):
        Out = [[] for _ in range((len(data_2d_array[idx]) - 1) // 3 + 2)]
        j = 0
        for i in range(len(data_2d_array[idx])):
            data = data_2d_array[idx][i]
            if self.is_number(data):
                Out[int((j) / 3)].append(data)
                j += 1
        return Out

    def process_per_quota(self, data_2d_array, idx, Exclude):
        Out = []
        for data in data_2d_array[idx]:
            if self.is_number(data):
                if data not in Exclude:
                    Out.append(data)
        return Out

    def process_all_data(self, file_path):
        self.file_path = file_path
        self.data_2d_array = self.read_csv_to_2d_array()
        for data in self.data_2d_array[1]:
            if self.is_number(data):
                self.Quotas.append(data)

        self.Moon = self.process_data(self.data_2d_array, 5, ['', 'MOON'])
        self.Weather = self.process_data(self.data_2d_array, 6, ['', 'WEATHER'])
        self.Layout = self.process_data(self.data_2d_array, 7, ['', 'LAYOUT'])
        self.Items = self.process_numbers(self.data_2d_array, 8)
        self.Bees = self.process_numbers(self.data_2d_array, 9)
        self.Collected = self.process_numbers(self.data_2d_array, 10)
        self.BL = self.process_numbers(self.data_2d_array, 11)
        self.Sold = self.process_per_quota(self.data_2d_array, 17, [''])

        for i in range(4):
            self.players.append(self.data_2d_array[21 + i][1])

        self.tree_Deaths = [[[] for _ in range((len(self.data_2d_array[21]) - 1) // 3 + 2)] for _ in range(len(self.players))]
        for j in range(4):
            i = 0
            k = 0
            for death in self.data_2d_array[21 + j]:
                if death in ['', 'M', 'S', 'X']:
                    if i > 0:
                        if death != '':
                            self.tree_Deaths[j][int((k) / 3)].append(True)
                        else:
                            self.tree_Deaths[j][int((k) / 3)].append(False)
                        k += 1
                    i += 1

        self.Notes = [[] for _ in range((len(self.data_2d_array[5]) - 1) // 3 + 2)]
        j = 0
        for i in range(len(self.data_2d_array[5])):
            data = self.data_2d_array[6][i]
            Note = ""
            if data not in ['', 'WEATHER']:
                Note += data + " "
            data = self.data_2d_array[7][i]
            if data not in ['', 'LAYOUT']:
                Note += data + " "
            data = self.data_2d_array[5][i]
            if data not in ['', 'MOON']:
                Note += data
            if Note != "":
                self.Notes[int((j) / 3)].append(Note)
                j += 1

        for i in range(len(self.Notes)):
            for j in range(len(self.Notes[i])):
                try:
                    self.Notes[i][j] += ", " + self.Items[i][j] + " itms, " + self.Bees[i][j] + " bees"
                except IndexError:
                    pass
        return self.get_json()

    def get_json(self):
        self.data_dict = {}

        for quota_index, quota in enumerate(self.Quotas):
            self.data_dict[str(quota_index + 1)] = {
                "Day 1": self.Collected[quota_index][0] if len(self.Collected[quota_index]) > 0 else "",
                "Day 1_BL": self.BL[quota_index][0] if len(self.BL[quota_index]) > 0 else "",
                "Day 1_Note": self.Notes[quota_index][0] if len(self.Notes[quota_index]) > 0 else "",
                "Day 2": self.Collected[quota_index][1] if len(self.Collected[quota_index]) > 1 else "",
                "Day 2_BL": self.BL[quota_index][1] if len(self.BL[quota_index]) > 1 else "",
                "Day 2_Note": self.Notes[quota_index][1] if len(self.Notes[quota_index]) > 1 else "",
                "Day 3": self.Collected[quota_index][2] if len(self.Collected[quota_index]) > 2 else "",
                "Day 3_BL": self.BL[quota_index][2] if len(self.BL[quota_index]) > 2 else "",
                "Day 3_Note": self.Notes[quota_index][2] if len(self.Notes[quota_index]) > 2 else "",
                "Sell": self.Sold[quota_index] if len(self.Sold) > quota_index else "",
                "Sell_BL": "",
                "Sell_Note": "",
                "Day 1_Player1": self.tree_Deaths[0][quota_index][0] if len(self.tree_Deaths) > 0 else False,
                "Day 1_Player2": self.tree_Deaths[1][quota_index][0] if len(self.tree_Deaths) > 1 else False,
                "Day 1_Player3": self.tree_Deaths[2][quota_index][0] if len(self.tree_Deaths) > 2 else False,
                "Day 1_Player4": self.tree_Deaths[3][quota_index][0] if len(self.tree_Deaths) > 3 else False,
                "Day 2_Player1": self.tree_Deaths[0][quota_index][1] if len(self.tree_Deaths) > 0 else False,
                "Day 2_Player2": self.tree_Deaths[1][quota_index][1] if len(self.tree_Deaths) > 1 else False,
                "Day 2_Player3": self.tree_Deaths[2][quota_index][1] if len(self.tree_Deaths) > 2 else False,
                "Day 2_Player4": self.tree_Deaths[3][quota_index][1] if len(self.tree_Deaths) > 3 else False,
                "Day 3_Player1": self.tree_Deaths[0][quota_index][2] if len(self.tree_Deaths) > 0 else False,
                "Day 3_Player2": self.tree_Deaths[1][quota_index][2] if len(self.tree_Deaths) > 1 else False,
                "Day 3_Player3": self.tree_Deaths[2][quota_index][2] if len(self.tree_Deaths) > 2 else False,
                "Day 3_Player4": self.tree_Deaths[3][quota_index][2] if len(self.tree_Deaths) > 3 else False,
                "Profit Quota": quota,
                "Player Names": self.players
            }

        return self.data_dict
