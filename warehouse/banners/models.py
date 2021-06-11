# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import date

from sqlalchemy import Column, Date, String, Text
from sqlalchemy_utils.types.url import URLType

from warehouse import db
from warehouse.utils.attrs import make_repr


class Banner(db.Model):
    __tablename__ = "banners"
    __repr__ = make_repr("text")
    DEFAULT_FA_ICON = "fa-comment-alt"

    # internal name
    name = Column(String, nullable=False)

    # banner display configuration
    text = Column(Text, nullable=False)
    link_url = Column(URLType, nullable=False)
    link_label = Column(String, nullable=False)
    fa_icon = Column(String, nullable=False, default=DEFAULT_FA_ICON)

    # dates to control visibility
    begin = Column(Date, nullable=False)
    end = Column(Date, nullable=False)

    @property
    def is_live(self):
        return self.begin <= date.today() <= self.end
