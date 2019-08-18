import random
import experiments.constants as constants


class GridSpec:
    def __init__(self, n_rows, n_columns, charset_id):
        self.n_rows = n_rows
        self.n_columns = n_columns

        try:
            self.charset = constants.SUPPORTED_CHARSETS_DICT[charset_id]
        except KeyError:
            raise ValueError(
                'Invalid CharacterGrid Character Set: Must be one of {}'.format(','.join(
                    sorted(constants.SUPPORTED_CHARSETS_DICT.keys()))))

    def create_grid(self):
        chars = random.sample(self.charset, k=self.n_rows * self.n_columns)
        return [chars[i * self.n_columns:(i + 1) * self.n_columns] for i in range(self.n_rows)]
