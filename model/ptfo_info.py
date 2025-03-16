from sqlalchemy import Column, Integer, String

from util.database import Base

class PtfoInfo(Base):
    __tablename__ = "tb_ptfo_info"
    PTFO_SEQNO = Column(Integer, primary_key=True, index=True)
    PTFO_NM = Column(String(50))
    PTFO_DESC = Column(String(1000))
