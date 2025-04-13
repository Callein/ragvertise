from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.models.ptfo_info import PtfoInfo
from app.models.tag_info import TagInfo
from app.models.ptfo_tag_mapp import PtfoTagMapp
from app.models.ptfo_tag_merged import PtfoTagMerged

from app.core.database import SessionLocal
from app.core.database import engine, Base


inspector = inspect(engine)
if "tb_ptfo_tag_merged" not in inspector.get_table_names():
    print("tb_ptfo_tag_merged 테이블이 존재하지 않아 생성합니다.")
    Base.metadata.create_all(bind=engine)


def populate_merged_table():
    db: Session = SessionLocal()

    try:
        db.query(PtfoTagMerged).delete()
        db.commit()

        joins = (
            db.query(
                PtfoInfo.PTFO_SEQNO,
                PtfoInfo.PTFO_NM,
                PtfoInfo.PTFO_DESC,
                TagInfo.TAG_SEQNO,
                TagInfo.TAG_NM
            )
            .join(PtfoTagMapp, PtfoInfo.PTFO_SEQNO == PtfoTagMapp.PTFO_SEQNO)
            .join(TagInfo, PtfoTagMapp.TAG_SEQNO == TagInfo.TAG_SEQNO)
            .filter(PtfoTagMapp.TAG_DSP_YN == 'Y')
            .all()
        )

        for ptfo_seq, ptfo_nm, ptfo_desc, tag_seq, tag_nm in joins:
            merged = PtfoTagMerged(
                PTFO_SEQNO=ptfo_seq,
                PTFO_NM=ptfo_nm,
                PTFO_DESC=ptfo_desc,
                TAG_SEQNO=tag_seq,
                TAG_NM=tag_nm
            )
            db.add(merged)

        db.commit()
        print(f"merged 테이블 생성 완료: 총 {len(joins)}건")

    finally:
        db.close()


if __name__ == "__main__":
    populate_merged_table()