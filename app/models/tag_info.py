from sqlalchemy import Column, Integer, String

from app.core.database import Base

class TagInfo(Base):
    __tablename__ = "tb_tag_info"
    TAG_SEQNO = Column(Integer, primary_key=True, index=True)
    TAG_NM = Column(String(50))
