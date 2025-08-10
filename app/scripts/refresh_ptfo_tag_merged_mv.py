from sqlalchemy import inspect
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import engine, Base, SessionLocal
from app.models.ptfo_info import PtfoInfo
from app.models.ptfo_tag_merged_mv import PtfoTagMergedMV
from app.models.tag_info import TagInfo
from app.models.ptfo_tag_mapp import PtfoTagMapp


def ensure_table_exists():
    inspector = inspect(engine)
    if "tb_ptfo_tag_merged_mv" not in inspector.get_table_names():
        print("tb_ptfo_tag_merged_mv 테이블이 존재하지 않아 생성합니다.")
        Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------
# 리프레시 (전체 재적재 방식: TRUNCATE → INSERT SELECT)
# ---------------------------------------------------------------------

def refresh_merged_mv_truncate_insert():
    db: Session = SessionLocal()
    try:
        # 테이블 비우기
        from sqlalchemy import text
        db.execute(text(f"TRUNCATE TABLE {PtfoTagMergedMV.__tablename__}"))

        rows = (
            db.query(
                PtfoInfo.PTFO_SEQNO,
                TagInfo.TAG_SEQNO,
                PtfoInfo.PTFO_NM,
                PtfoInfo.PTFO_DESC,
                TagInfo.TAG_NM,
                PtfoInfo.VIEW_LNK_URL,
                PtfoInfo.PRDN_STDO_NM,
                PtfoInfo.PRDN_COST,
                PtfoInfo.PRDN_PERD,
            )
            .join(PtfoTagMapp, PtfoInfo.PTFO_SEQNO == PtfoTagMapp.PTFO_SEQNO)
            .join(TagInfo, PtfoTagMapp.TAG_SEQNO == TagInfo.TAG_SEQNO)
            .filter(PtfoTagMapp.TAG_DSP_YN == 'Y')
            .all()
        )

        payload = [
            dict(
                PTFO_SEQNO=r[0],
                TAG_SEQNO=r[1],
                PTFO_NM=r[2],
                PTFO_DESC=r[3],
                TAG_NM=r[4],
                VIEW_LNK_URL=r[5],
                PRDN_STDO_NM=r[6],
                PRDN_COST=r[7],
                PRDN_PERD=r[8],
            ) for r in rows
        ]
        if payload:
            db.bulk_insert_mappings(PtfoTagMergedMV, payload)

        db.commit()
        print(f"tb_ptfo_tag_merged_mv 리프레시 완료 (재적재): {len(payload)}건")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# ---------------------------------------------------------------------
# 리프레시 (증분 UPSERT 방식)
# ---------------------------------------------------------------------
def refresh_merged_mv_upsert():
    """
    갱신량이 적고 락을 최소화하고 싶을 때. ON DUPLICATE KEY UPDATE 사용.
    """
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(
                PtfoInfo.PTFO_SEQNO,
                TagInfo.TAG_SEQNO,
                PtfoInfo.PTFO_NM,
                PtfoInfo.PTFO_DESC,
                TagInfo.TAG_NM,
                PtfoInfo.VIEW_LNK_URL,
                PtfoInfo.PRDN_STDO_NM,
                PtfoInfo.PRDN_COST,
                PtfoInfo.PRDN_PERD,
            )
            .join(PtfoTagMapp, PtfoInfo.PTFO_SEQNO == PtfoTagMapp.PTFO_SEQNO)
            .join(TagInfo, PtfoTagMapp.TAG_SEQNO == TagInfo.TAG_SEQNO)
            .filter(PtfoTagMapp.TAG_DSP_YN == 'Y')
            .all()
        )

        # MySQL 전용 UPSERT (executemany)
        sql = f"""
        INSERT INTO {PtfoTagMergedMV.__tablename__} (
            PTFO_SEQNO, TAG_SEQNO, PTFO_NM, PTFO_DESC, TAG_NM,
            VIEW_LNK_URL, PRDN_STDO_NM, PRDN_COST, PRDN_PERD
        ) VALUES (
            %(PTFO_SEQNO)s, %(TAG_SEQNO)s, %(PTFO_NM)s, %(PTFO_DESC)s, %(TAG_NM)s,
            %(VIEW_LNK_URL)s, %(PRDN_STDO_NM)s, %(PRDN_COST)s, %(PRDN_PERD)s
        )
        ON DUPLICATE KEY UPDATE
            PTFO_NM = VALUES(PTFO_NM),
            PTFO_DESC = VALUES(PTFO_DESC),
            TAG_NM = VALUES(TAG_NM),
            VIEW_LNK_URL = VALUES(VIEW_LNK_URL),
            PRDN_STDO_NM = VALUES(PRDN_STDO_NM),
            PRDN_COST = VALUES(PRDN_COST),
            PRDN_PERD = VALUES(PRDN_PERD);
        """

        payload = [
            dict(
                PTFO_SEQNO=r[0],
                TAG_SEQNO=r[1],
                PTFO_NM=r[2],
                PTFO_DESC=r[3],
                TAG_NM=r[4],
                VIEW_LNK_URL=r[5],
                PRDN_STDO_NM=r[6],
                PRDN_COST=r[7],
                PRDN_PERD=r[8],
            ) for r in rows
        ]
        if payload:
            db.execute(sql, payload)  # SQLAlchemy 1.4+: executemany 지원

        db.commit()
        print(f"tb_ptfo_tag_merged_mv 리프레시 완료 (UPSERT): {len(payload)}건")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------
if __name__ == "__main__":
    ensure_table_exists()
    refresh_merged_mv_truncate_insert()
    # refresh_merged_mv_upsert()