import dash
import time
import dash_html_components as html
from dash.testing.application_runners import import_app


def test_001_dash(dash_duo):
    # load app
    app = import_app("dashboards.data_app")
    dash_duo.start_server(app)

    # when the app loads, no filters exist
    filters = dash_duo.find_elements(".filter")
    assert len(filters) == 0

    # the user can click a button to add a filter
    dash_duo.multiple_click("#add-filter", 1)

    # a filter appears, bringing the total number of filters to 1S
    filters = dash_duo.find_elements(".filter")
    assert len(filters) == 1

    # dash_duo.multiple_click("#remove-filter-1", 1)
    # filters = dash_duo.find_elements(".filter")
    # assert len(filters) == 0
    # time.sleep(0.5)
    # inputbox = dash_duo.find_element("#officer_input")
    # dash_duo.find_element("#data_html")
    # inputbox.send_keys("Feaman, Adam\n")
    # dash_duo.multiple_click("#submit", 1)
    # dash_duo.wait_for_contains_text("#officer_name", "Feaman")
    # dash_duo.wait_for_contains_text(
    #     "#officer-info", "No longer employed with the SLMPD"
    # )
