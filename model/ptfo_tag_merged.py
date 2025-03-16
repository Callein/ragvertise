from sqlalchemy import Column, Integer, String

from util.database import Base

class PtfoTagMerged(Base):
    __tablename__ = "tb_ptfo_tag_merged"
    PTFO_SEQNO = Column(Integer, primary_key=True, index=True)
    TAG_SEQNO = Column(Integer, primary_key=True, index=True)
    PTFO_NM = Column(String(50))
    PTFO_DESC = Column(String(1000))
    TAG_NM = Column(String(50))