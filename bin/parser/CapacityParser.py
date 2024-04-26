import entsoe.mappings
import pandas as pd


class CapacityParser:
    @staticmethod
    def get_neighbouring_bid_zone_symbols(code: str) -> list[str]:
        """
        Pobiera symbole sąsiednich bid zon względem @country
        :param code: kraj
        :return: lista symboli bid zon krajów sąsiadujących
        """
        if code in entsoe.mappings.NEIGHBOURS.keys():
            countries = entsoe.mappings.NEIGHBOURS[code]
            cc = CapacityParser.get_symbols(countries)
            return [x.code for x in cc]
        else:
            print('Niewlasciwy akronim nazwy kraju')
            raise ValueError

    @staticmethod
    def get_symbols(codes: list[str]) -> list[entsoe.Area]:
        return [getattr(entsoe.mappings.Area, i) for i in codes]

    @staticmethod
    def get_local_bid_zone_symbol(code: str) -> str:
        if code in entsoe.mappings.NEIGHBOURS.keys():
            local_bz = getattr(entsoe.mappings.Area, code)
            return local_bz
        else:
            print('Niewlasciwy akronim nazwy kraju')
            raise ValueError

    @staticmethod
    def get_request_day_ahead(start: pd.Timestamp, end: pd.Timestamp) -> ...:  # TODO: typ zwracany xml lub None
        return pd.date_range(start.date(), end.date(), freq='d')
        # try:
        #     response = user.client._base_request(params=params, start=start, end=end)
        #     if response.ok:
        #         response = parse_xml(response)
        #     return response
        # except Exception as e:
        #     print(e.__cause__)

#TODO: wygenerowac liste dat pomiedzy start/end

start = pd.Timestamp('20230416', tz='Europe/Warsaw')
end = pd.Timestamp('20230426', tz='Europe/Warsaw')
print(CapacityParser.get_request_day_ahead(start,end))
