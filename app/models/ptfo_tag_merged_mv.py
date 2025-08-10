from sqlalchemy import Column, UniqueConstraint, Integer, String

from app.core.database import Base


class PtfoTagMergedMV(Base):
    __tablename__ = "tb_ptfo_tag_merged_mv"

    PTFO_SEQNO    = Column(Integer, primary_key=True)
    TAG_SEQNO     = Column(Integer, primary_key=True)
    PTFO_NM       = Column(String(50))
    PTFO_DESC     = Column(String(1000))
    TAG_NM        = Column(String(50))
    VIEW_LNK_URL  = Column(String(300))
    PRDN_STDO_NM  = Column(String(100))
    PRDN_COST     = Column(String(30))
    PRDN_PERD     = Column(String(50))

    __table_args__ = (
        UniqueConstraint('PTFO_SEQNO', 'TAG_SEQNO', name='ux_ptfo_tag_merged_mv'),
    )