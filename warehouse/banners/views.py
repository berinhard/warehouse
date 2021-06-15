import datetime

from pyramid.view import view_config

from warehouse.banners.models import Banner


@view_config(
    route_name="includes.db-banners",
    renderer="includes/banner-messages.html",
    uses_session=True,
    has_translations=True,
)
def list_banner_messages(request):
    # used to preview specific banner
    banner_id = request.params.get("single_banner")
    if banner_id:
        query = request.db.query(Banner).filter((Banner.id == banner_id))
    else:
        today = str(datetime.date.today())
        query = request.db.query(Banner).filter(
            (Banner.begin <= today) & (Banner.end >= today)
        )

    return {"banners": query.all()}
