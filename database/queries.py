
from database.models import User, Matches
from database.base import Database


class Queries(Database):

    def get_user_db(self, user_id):
        data = self.session.query(User).filter(User.user_id == user_id).one_or_none()
        data = self.row_to_dict(data)
        return data

    @staticmethod
    def row_to_dict(row):
        d = {}
        for column in row.__table__.columns:
            d[column.name] = int(getattr(row, column.name))
        return d

    def get_matches(self, user_id):
        matches = self.session.query(Matches.match_id).filter(Matches.user_id == user_id).limit(1).all()
        i = 0
        for match_tuple in matches:
            matches[i] = match_tuple[0]
            i += 1
        for m_id in matches:
            self.session.query(Matches).filter(Matches.match_id == m_id).update({'seen': Matches.seen + 1})
            self.session.commit()
        return matches
