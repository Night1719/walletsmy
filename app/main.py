from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy.exc import OperationalError

from .config import settings
from .database import engine
from .models import Base
from .routers import auth_routes, admin, surveys, public

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, description=settings.APP_DESCRIPTION)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, same_site="lax")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates


@app.on_event("startup")
def on_startup():
	try:
		Base.metadata.create_all(bind=engine)
	except OperationalError:
		# Tables will be created once DB is ready (e.g., after install.sh sets Postgres)
		pass


@app.get("/")
async def root(request: Request):
	return RedirectResponse(url="/surveys")


app.include_router(auth_routes.router)
app.include_router(admin.router)
app.include_router(surveys.router)
app.include_router(public.router)