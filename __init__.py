from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from .models import appmaker


def root_factory(request):
    conn = get_connection(request)
    #print "Running Appmaker"
    return appmaker(conn.root())


def main(global_config, **settings):
    
    print __file__
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=root_factory, settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_google_login')

    config.add_static_view("static",              "static",                 cache_max_age=3600)
    config.add_static_view("graphics",            "/static/graphics",       cache_max_age=1000000)
    config.add_static_view("javascript",          "/static/javascript",     cache_max_age=3600)
    config.add_static_view("css",                 "/static/css",            cache_max_age=3600)
    config.add_static_view("svg",                 "/static/svg",            cache_max_age=3600)
        
    config.add_route("thisEqualsThat",            "/thisEqualsThat")
    config.add_route("thisEqualsThat_iframe",     "/thisEqualsThat_iframe")
    config.add_route("thisEqualsThat_bertonbeil", "/thisEqualsThat_bertonbeil")

    config.add_route("testData",                  "/testData")
    
    config.add_route("inputFieldAltered",         "/inputFieldAltered")
    config.add_route("getModelClasses",           "/getModelClasses")
    config.add_route("getClassInstance",          "/getClassInstance")
    config.add_route("setBottomModel",            "/setBottomModel")
    
    config.add_route("initialise",                "/intialise")

    config.add_route("getEmbedURL",                "/getEmbedURL")

    #google connect
    #config.add_route("googleConnect",         "/googleConnect")
    config.add_route("googleConnect/login",               "/googleConnect/login")
    config.add_route("googleConnect/gotCredentials",      "/googleConnect/gotCredentials")
    config.add_route("googleConnect/credentialsCheck",    "/googleConnect/credentialsCheck")
    config.add_route("googleConnect/getSheets",           "/googleConnect/getSheets")
    config.add_route("googleConnect/getCellRange",        "/googleConnect/getCellRange")

    config.add_route("scottishParliament/votingModel",    "scottishParliament/votingModel")
    config.add_route("scottishParliament/data",           "scottishParliament/data")
    config.add_route("scottishParliament/updateSwings",   "scottishParliament/updateSwings")


    
    config.scan()
    return config.make_wsgi_app()
