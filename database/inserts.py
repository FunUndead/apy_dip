from sqlalchemy import exists, and_
from database.base import Database
from database.models import User, Matches


class Inserts(Database):

    def insert_matches(self, data, user_id: int):
        for match in data['response']['items']:
            if match['is_closed'] is False:
                if not self.check_match_exists(match['id'], user_id):
                    self.session.add(Matches(user_id=user_id, match_id=match['id'], seen=0))
                    self.session.commit()

    def insert_data(self, userinfo: dict):
        if not self.check_user_exists(userinfo['user_id']):
            user = User(**userinfo)
            self.session.add(user)
            self.session.commit()

    def check_user_exists(self, user_id: int) -> bool:
        is_exists = self.session.query(exists().where(User.user_id == user_id)).scalar()
        return is_exists

    def check_match_exists(self, match_id: int, user_id: int) -> bool:
        is_exists = self.session.query(exists().where(and_(Matches.match_id == match_id, Matches.user_id == user_id))).scalar()
        return is_exists
