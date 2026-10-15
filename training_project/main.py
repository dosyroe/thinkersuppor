from app.ui import ShoeApp
import settings


if __name__ == "__main__":
    application = ShoeApp(module=settings.MODULE)
    application.mainloop()
