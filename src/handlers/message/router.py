from aiogram import Router

from src.handlers.middleware.auth import AuthMiddleware

router = Router()
router.message.middleware(AuthMiddleware())
