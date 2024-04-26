import pandas as pd

from bin.models.Generation import Generation


class GenerationParser:
    @staticmethod
    def to_obj(country: str, row: pd.DataFrame) -> list[Generation]:
        records = list()
        for j, r in row.iterrows():
            for idx in r.index:
                unit = str(idx[0])
                country = str(country)
                fuel = str(idx[1])
                code = str(idx[3])
                try:
                    generation = int(row.loc[j, idx])
                except:
                    generation = 0
                res = Generation(dt=j, unit=unit, country=country, code=code, fuel=fuel,
                                 generation=generation)
                records.append(res)
        return records
