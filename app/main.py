from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy.exc import OperationalError

from .config import settings
from .database import engine, SessionLocal
from .models import Base, User
from .routers import auth_routes, admin, surveys, public
from .auth import hash_password

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, description=settings.APP_DESCRIPTION)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, same_site="lax")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates


@app.on_event("startup")
def on_startup():
	try:
		Base.metadata.create_all(bind=engine)
		# Ensure default admin exists on first run
		db = SessionLocal()
		try:
			any_user = db.query(User.id).first()
			if not any_user:
				admin = User(username="Admin", email=None, password_hash=hash_password("R2b9rfo8"), role="admin", is_active=True)
				db.add(admin)
				db.commit()
		except Exception:
			pass
		finally:
			db.close()
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