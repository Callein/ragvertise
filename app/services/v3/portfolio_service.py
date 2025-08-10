from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.ptfo_tag_merged_mv import PtfoTagMergedMV

class PortFolioServiceV3:
    @staticmethod
    def load_portfolio_data(db: Session) -> List[Dict]:
        """
        tb_ptfo_tag_merged_mv 로드
        """
        rows = db.query(PtfoTagMergedMV).all()
        grouped: Dict[int, Dict] = {}

        for row in rows:
            pid = row.PTFO_SEQNO
            if pid not in grouped:
                grouped[pid] = {
                    "PTFO_SEQNO":   row.PTFO_SEQNO,
                    "PTFO_NM":      row.PTFO_NM,
                    "PTFO_DESC":    row.PTFO_DESC,
                    "VIEW_LNK_URL": row.VIEW_LNK_URL,
                    "PRDN_STDO_NM": row.PRDN_STDO_NM,
                    "PRDN_COST":    row.PRDN_COST,
                    "PRDN_PERD":    row.PRDN_PERD,
                    "tags": []
                }
            if row.TAG_NM:
                grouped[pid]["tags"].append(row.TAG_NM)

        # 태그 중복 제거 및 정렬
        for data in grouped.values():
            data["tags"] = sorted(set(data["tags"]))

        return list(grouped.values())