from pram import DATA_PATH

import pandas as pd


def create_data_csv():

    content = {
        'id': [],
        'name': [],
        'img': [],
        'feature': []
    }

    data = pd.DataFrame(content)
    save_csv_data(data, DATA_PATH)


def save_csv_data(data, path):
    data.to_csv(path, encoding='utf-8', index=False)


def load_csv_data(path):
    return pd.read_csv(path)


class Data:

    def __init__(self):
        self.content = load_csv_data(DATA_PATH)

    def add_new_member(self, stu_id, stu_name, img, feature):

        new_content = {
            'id': stu_id,
            'name': stu_name,
            'img': img,
            'feature': feature
        }

        row = pd.Series(new_content)
        self.content = self.content.append(row, ignore_index=True)
        save_csv_data(self.content, DATA_PATH)

    def remove_member_by_id(self, stu_id):
        self.content = self.content.drop(self.content.index[self.content['id'] == stu_id])
        save_csv_data(self.content, DATA_PATH)
