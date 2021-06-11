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
from unittest import TestCase

import pretend

from webob.multidict import MultiDict

from warehouse.admin.views import banners as views
from warehouse.banners.models import Banner

from ....common.db.banners import BannerFactory


class TestBannerList:
    def test_list_all_banners(self, db_request):
        [BannerFactory.create() for _ in range(5)]
        banners = db_request.db.query(Banner).order_by(Banner.begin.desc()).all()

        result = views.banner_list(db_request)

        assert result == {"banners": banners}


class TestCreateBanner:
    def test_serialize_form_to_create_banner(self, db_request):
        result = views.create_banner(db_request)

        assert len(result) == 1
        assert isinstance(result["form"], views.BannerForm)

    def test_serialize_form_errors_if_invalid_post(self, db_request):
        db_request.method = "POST"
        db_request.POST["name"] = ""
        db_request.POST["link_url"] = ""
        db_request.POST = MultiDict(db_request.POST)

        result = views.create_banner(db_request)

        assert len(result) == 1
        assert isinstance(result["form"], views.BannerForm)
        assert result["form"].errors

    def test_create_banner(self, db_request):
        db_request.method = "POST"
        db_request.POST["name"] = "Banner"
        db_request.POST["link_url"] = "https://newbanner.com"
        db_request.POST["text"] = "Bannert content"
        db_request.POST["begin"] = "2021-06-30"
        db_request.POST["end"] = "2021-07-30"
        db_request.POST = MultiDict(db_request.POST)
        db_request.session = pretend.stub(
            flash=pretend.call_recorder(lambda *a, **kw: None)
        )
        db_request.route_url = pretend.call_recorder(lambda r: "/admin/banners/")

        resp = views.create_banner(db_request)

        assert resp.status_code == 303
        assert resp.location == "/admin/banners/"
        assert db_request.session.flash.calls == [
            pretend.call("Added new banner 'Banner'", queue="success")
        ]
        assert db_request.route_url.calls == [pretend.call("admin.banner.list")]


class TestBannerForm(TestCase):
    def setUp(self):
        self.data = {
            "name": "Sample Banner",
            "text": "This should be the correct text",
            "link_url": "https://samplebanner.com",
            "begin": "2021-06-30",
            "end": "2021-07-30",
        }

    def test_required_fields(self):
        required_fields = self.data.keys()  # all fields are required

        form = views.BannerForm(data={})

        assert form.validate() is False
        assert len(form.errors) == len(required_fields)
        for field in required_fields:
            assert field in form.errors

    def test_valid_data(self):
        form = views.BannerForm(data=self.data)
        assert form.validate() is True

    def test_invalid_form_if_wrong_time_interval(self):
        self.data["begin"], self.data["end"] = self.data["end"], self.data["begin"]

        form = views.BannerForm(data=self.data)

        assert form.validate() is False
        assert "begin" in form.errors
        assert "end" in form.errors
