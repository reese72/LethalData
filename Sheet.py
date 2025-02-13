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
        try:
            Out = [[] for _ in range((len(data_2d_array[idx]) - 1) // 3 + 2)]
            j = 0
            for i in range(len(data_2d_array[idx])):
                data = data_2d_array[idx][i]
                if not any(str(data).lower() in str(exclude).lower() for exclude in Exclude):
                    Out[int((j) / 3)].append(data)
                    j += 1
        except IndexError:
            Out = [[]]
        return Out

    def process_numbers(self, data_2d_array, idx):
        try:
            Out = [[] for _ in range((len(data_2d_array[idx]) - 1) // 3 + 2)]
            j = 0
            for i in range(len(data_2d_array[idx])):
                data = data_2d_array[idx][i]
                if self.is_number(data):
                    Out[int((j) / 3)].append(data)
                    j += 1
        except IndexError:
            Out = [[]]
            pass
        return Out

    def process_per_quota(self, data_2d_array, idx, Exclude):
        try:
            Out = []
            for data in data_2d_array[idx]:
                if self.is_number(data):
                    if not any(str(data).lower() in str(exclude).lower() for exclude in Exclude):
                        Out.append(data)
        except IndexError:
            Out = []
            pass
        return Out

    def process_all_data(self, file_path, format):
        if format == "maku":
            self.playoffset = 1
            self.QIdx = 1
            self.MoonIdx = 5
            self.WeatherIdx = 6
            self.LayoutIdx = 7
            self.ItemsIdx = 8
            self.BeesIdx = 9
            self.CollectedIdx = 10
            self.BLIdx = 11
            self.SoldIdx = 17
            self.PlayersIdx = 21
            self.NoteIdx = 25
        elif format == "dop":
            self.playoffset = 2
            self.QIdx = 2
            self.MoonIdx = 6
            self.WeatherIdx = 7
            self.LayoutIdx = 8
            self.ItemsIdx = 9
            self.BeesIdx = 9999
            self.CollectedIdx = 10
            self.BLIdx = 11
            self.SoldIdx = 15
            self.PlayersIdx = 16
            self.NoteIdx = 20
        elif format == "bread":
            self.playoffset = 2
            self.QIdx = 1
            self.MoonIdx = 6
            self.WeatherIdx = 7
            self.LayoutIdx = 9999
            self.ItemsIdx = 9999
            self.BeesIdx = 10000
            self.CollectedIdx = 8
            self.BLIdx = 12000
            self.SoldIdx = 12
            self.PlayersIdx = 9999
            self.NoteIdx = 16
        self.file_path = file_path
        self.data_2d_array = self.read_csv_to_2d_array()
        for data in self.data_2d_array[self.QIdx]:
            if self.is_number(data):
                self.Quotas.append(data)

        print(self.Quotas)

        self.Moon = self.process_data(self.data_2d_array, self.MoonIdx, ['', 'MOON'])
        self.Weather = self.process_data(self.data_2d_array, self.WeatherIdx, ['', 'WEATHER', 'CONDITION'])
        self.Layout = self.process_data(self.data_2d_array, self.LayoutIdx, ['', 'LAYOUT', 'Alt Layout'])
        self.Items = self.process_numbers(self.data_2d_array, self.ItemsIdx)
        self.Bees = self.process_numbers(self.data_2d_array, self.BeesIdx)
        self.Collected = self.process_numbers(self.data_2d_array, self.CollectedIdx)
        self.BL = self.process_numbers(self.data_2d_array, self.BLIdx)
        self.Sold = self.process_per_quota(self.data_2d_array, self.SoldIdx, [''])

        print(self.Moon)
        print(self.Weather)
        print(self.Layout)
        print(self.Items)
        print(self.Bees)
        print(self.Collected)
        print(self.BL)
        print(self.Sold)

        try:
            for i in range(4):
                self.players.append(self.data_2d_array[self.PlayersIdx + i][self.playoffset])
        except IndexError:
            pass


        self.tree_Deaths = [[[] for _ in range((len(self.data_2d_array[self.PlayersIdx]) - 1) // 3 + 2)] for _ in range(len(self.players))]
        try:
            for j in range(4):
                i = 0
                k = 0
                print(self.data_2d_array[self.PlayersIdx + j])
                for death in self.data_2d_array[self.PlayersIdx + j]:
                    if death in ['', 'M', 'S', 'X', ' TRUE ', ' FALSE ', ' X ', ' ']:
                        if i > (self.playoffset - 1):
                            if death == ' FALSE ' or death == '':
                                self.tree_Deaths[j][int((k) / 3)].append(False)
                            else:
                                self.tree_Deaths[j][int((k) / 3)].append(True)
                            k += 1
                    i += 1
        except IndexError:
            pass

        self.Notes = [[] for _ in range((len(self.data_2d_array[self.MoonIdx]) - 1) // 3 + 2)]
        j = 0
        for i in range(len(self.data_2d_array[self.MoonIdx])):
            Note = ""
            try:
                data = self.data_2d_array[self.NoteIdx][i]
                print(data)
                if (data not in ['Notes', 'NOTES', 'notes']) and data != "":
                    Note += data + ", "
            except IndexError:
                pass
            data = self.data_2d_array[self.WeatherIdx][i]
            if data not in ['', 'WEATHER', 'CONDITION', ' ', 'Weather']:
                Note += data + " "
            try:
                data = self.data_2d_array[self.LayoutIdx][i]
                if data == "FALSE":
                    data = "Facility"
                elif data == "TRUE":
                    data = "Mansion"
                if data not in ['', 'LAYOUT', 'Alt Layout', ' ', 'Layout']:
                    Note += data + " "
            except IndexError:
                Note += " "
            data = self.data_2d_array[self.MoonIdx][i]
            if data not in ['', 'MOON', 'Moon']:
                Note += data
            if Note != "" and not Note.isspace():
                self.Notes[int((j) / 3)].append(Note)
                j += 1
        try:
            for i in range(len(self.Notes)):
                for j in range(len(self.Notes[i])):
                    self.Notes[i][j] += ", " + self.Items[i][j] + " itms, " + self.Bees[i][j] + " bees"
        except IndexError:
            pass
        return self.get_json()

    def get_json(self):
        self.data_dict = {}

        for quota_index, quota in enumerate(self.Quotas):
            print(quota_index)
            print(quota)
            self.data_dict[str(quota_index + 1)] = {
                "Day 1": self.Collected[quota_index][0] if len(self.Collected[quota_index]) > 0 else "",
                "Day 1_BL": (self.BL[quota_index][0] if len(self.BL[quota_index]) > 0 else "") if len(self.BL) > quota_index else "",
                "Day 1_Note": self.Notes[quota_index][0] if len(self.Notes[quota_index]) > 0 else "",
                "Day 2": self.Collected[quota_index][1] if len(self.Collected[quota_index]) > 1 else "",
                "Day 2_BL": (self.BL[quota_index][1] if len(self.BL[quota_index]) > 1 else "") if len(self.BL) > quota_index else "",
                "Day 2_Note": self.Notes[quota_index][1] if len(self.Notes[quota_index]) > 1 else "",
                "Day 3": self.Collected[quota_index][2] if len(self.Collected[quota_index]) > 2 else "",
                "Day 3_BL": (self.BL[quota_index][2] if len(self.BL[quota_index]) > 2 else "") if len(self.BL) > quota_index else "",
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
        print(self.data_dict)

        return self.data_dict
