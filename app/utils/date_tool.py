# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from zoneinfo import ZoneInfo


def get_seoul_time():
    return datetime.now(ZoneInfo("Asia/Seoul"))