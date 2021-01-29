from sqlalchemy import Column, Integer, String
from . import database

class Subpart(database.Base):
     __tablename__ = 'cfr_subparts'

     subpart_id = Column(Integer, primary_key=True)
     subchapter = Column(String)
     part = Column(Integer)
     subpart = Column(String)

     def __repr__(self):
        return "<Subpart(subchapter='%s', part='%s', subpart='%s')>" % (
                             self.subchapter, self.part, self.subpart)