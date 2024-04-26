from flask_sqlalchemy.session import Session
from loguru import logger

from bin.models.db_model import DbModel


class DbUtils:
    @staticmethod
    def update_in_db(objs: list[DbModel.Model], db_session: Session):
        logger.debug(f"Aktualizacja danych w bazie, liczba obiektów: {len(objs)}")
        try:
            for i in objs:
                db_session.merge(i)
            db_session.commit()
            logger.success("Zapis obiektów w bazie udany")
        except Exception as e:
            logger.error(e)
            raise e
