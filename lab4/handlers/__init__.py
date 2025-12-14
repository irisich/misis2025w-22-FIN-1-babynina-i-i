from venv import create

from .cold_start import router as cold_start
from .main_menu import router as main_menu
from .start_dialog import router as start_dialog
from .create_recs import  router as create_recs

routers = [
    start_dialog,
    cold_start,
    main_menu,
    create_recs
]