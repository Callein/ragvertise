from sqlalchemy import Column, Integer, String
from app.core.database import Base

class PtfoInfo(Base):
    __tablename__ = "tb_ptfo_info"
    PTFO_SEQNO = Column(Integer, primary_key=True, index=True)
    PTFO_NM = Column(String(50))
    PTFO_DESC = Column(String(1000))

    VIEW_LNK_URL = Column(String(300))                              # 비디오 링크 URL
    PRDN_STDO_NM = Column(String(100))                              # 업체명(제작스튜디오명)
    PRDN_COST = Column(String(30))                                  # 제작비
    PRDN_PERD      = Column(String(50))                             # 제작기간