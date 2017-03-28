from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

engine = create_engine('sqlite:////home/lemon/code/python/xldigest/xldigest/'
                       'db.sqlite')


class SeriesItem(Base):
    __tablename__ = 'series_item'
    name = Column(String)
    series = Column(Integer, ForeignKey('series.id'))
    start_date = Column(Date)
    end_date = Column(Date)


class Series(Base):
    __tablename__ = 'series'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    first_series_item = Column(Date)
    last_series_item = Column(Date)
    series_items = relationship("SeriesItem")


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    returnitems = relationship("ReturnItem")

    def __repr__(self):
        return "<Project(name='{0}')>".format(self.name)


class Quarter(Base):
    __tablename__ = 'quarters'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class DatamapItem(Base):
    __tablename__ = 'datamap_items'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    bicc_sheet = Column(String)
    bicc_cellref = Column(String)
    gmpp_sheet = Column(String)
    gmpp_cellref = Column(String)
    bicc_ver_form = Column(String)
    return_items = relationship("ReturnItem")

    def __repr__(self):
        return "<DatamapItem('{}')>".format(self.key[0:15])


class ReturnItem(Base):
    __tablename__ = 'returns'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    quarter_id = Column(Integer, ForeignKey('quarters.id'))
    datamap_item_id = Column(Integer, ForeignKey('datamap_items.id'))
    value = Column(String)

    def __repr__(self):
        return ("<ReturnItem(Project: {0}, Quarter for {1}, "
                "for DMI: {2}>").format(self.project_id, self.quarter_id,
                                        self.datamap_item_id)


Base.metadata.create_all(engine)
