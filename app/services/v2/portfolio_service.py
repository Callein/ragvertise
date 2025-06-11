from sqlalchemy.orm import Session

from app.models.ptfo_tag_merged import PtfoTagMerged


class PortFolioServiceV2:
    @staticmethod
    def load_portfolio_data(db: Session):
        rows = db.query(PtfoTagMerged).all()
        grouped_data = {}

        for row in rows:
            ptfo_seqno = row.PTFO_SEQNO
            if ptfo_seqno not in grouped_data:
                grouped_data[ptfo_seqno] = {
                    "PTFO_SEQNO": row.PTFO_SEQNO,
                    "PTFO_NM": row.PTFO_NM,
                    "PTFO_DESC": row.PTFO_DESC,
                    "tags": []
                }
            grouped_data[ptfo_seqno]["tags"].append(row.TAG_NM)

        return list(grouped_data.values())