from sqlalchemy import Column, Integer, String, CHAR
from app.core.database import Base


class PtfoTagMapp(Base):
    __tablename__ = "tb_ptfo_tag_mapp"

    PTFO_SEQNO = Column(Integer, primary_key=True)
    TAG_SEQNO = Column(Integer, primary_key=True)
    TAG_DSP_YN = Column(CHAR(1), nullable=True)
    WR_PER_NO = Column(Integer, nullable=True)
    WR_DTM = Column(String(14), nullable=True)