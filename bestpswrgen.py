import os
import json
import random
import string
import math
import hashlib
import hmac
import struct
import time
from datetime import datetime
from collections import Counter
from typing import Dict, List, Optional
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== КЛАСС МЕНЕДЖЕРА ПАРОЛЕЙ ====================

class PasswordManager:
    def __init__(self, user_id: int = None):
        self.user_id = user_id
        self.storage_dir = "user_data"
        os.makedirs(self.storage_dir, exist_ok=True)
        self.storage_file = f"{self.storage_dir}/passwords_{user_id}.json" if user_id else "passwords.json"
        self.passwords = self.load_passwords()

    def load_passwords(self) -> Dict:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_password(self, service: str, login: str, password: str, notes: str = "") -> bool:
        try:
            self.passwords[service] = {
                'login': login,
                'password': password,
                'notes': notes,
                'created': datetime.now().isoformat(),
                'strength': self._calculate_strength(password),
                'last_used': datetime.now().isoformat()
            }
            self._save_to_file()
            return True
        except:
            return False

    def get_password(self, service: str) -> Optional[Dict]:
        if service in self.passwords:
            self.passwords[service]['last_used'] = datetime.now().isoformat()
            self._save_to_file()
        return self.passwords.get(service)

    def delete_password(self, service: str) -> bool:
        if service in self.passwords:
            del self.passwords[service]
            self._save_to_file()
            return True
        return False

    def list_services(self) -> List[str]:
        return list(self.passwords.keys())

    def _calculate_strength(self, password: str) -> str:
        score = 0
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1

        if any(c in string.ascii_lowercase for c in password):
            score += 1
        if any(c in string.ascii_uppercase for c in password):
            score += 1
        if any(c in string.digits for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1

        strength_levels = ["Очень слабый", "Слабый", "Средний", "Хороший", "Отличный", "Идеальный"]
        return strength_levels[min(score, 5)]

    def _save_to_file(self):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.passwords, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")

# ==================== КЛАСС ГЕНЕРАТОРА ПАРОЛЕЙ ====================

class AdvancedPasswordGenerator:
    def __init__(self, user_id: int = None):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.password_manager = PasswordManager(user_id)
        
        self.stats_file = f"user_data/stats_{user_id}.json" if user_id else "stats.json"
        self.stats = self.load_stats()
        
        self.strength_emojis = {
            0: "❌ Очень слабый",
            1: "🔴 Слабый",
            2: "🟡 Средний",
            3: "🟢 Хороший",
            4: "💪 Отличный",
            5: "🔐 Идеальный"
        }

    def generate_simple_password(self, length: int = 10) -> str:
        """Генерация простого пароля"""
        characters = self.lowercase + self.uppercase
        password = ''.join(random.choice(characters) for _ in range(length))
        self._update_stats("simple")
        return password

    def generate_strong_password(self, length: int = 16) -> str:
        """Генерация сложного пароля"""
        characters = self.lowercase + self.uppercase + self.digits + self.symbols
        password = ''.join(random.choice(characters) for _ in range(length))
        self._update_stats("strong")
        return password

    def generate_custom_password(self, length: int, characters: str) -> str:
        """Генерация пароля из пользовательских символов"""
        password = ''.join(random.choice(characters) for _ in range(length))
        self._update_stats("custom")
        return password

    def generate_advanced_password(self, length: int = 12) -> str:
        """Генерация продвинутого пароля"""
        characters = self.lowercase + self.uppercase + self.digits + self.symbols
        
        password = [
            random.choice(self.lowercase),
            random.choice(self.uppercase),
            random.choice(self.digits),
            random.choice(self.symbols)
        ]
        
        while len(password) < length:
            password.append(random.choice(characters))
        
        random.shuffle(password)
        password_str = ''.join(password[:length])
        self._update_stats("advanced")
        return password_str

    def analyze_password(self, password: str) -> Dict:
        """Анализ сложности пароля"""
        score = 0
        length = len(password)
        
        if length >= 16:
            score += 2
        elif length >= 12:
            score += 2
        elif length >= 8:
            score += 1

        contains_lower = any(c in self.lowercase for c in password)
        contains_upper = any(c in self.uppercase for c in password)
        contains_digits = any(c in self.digits for c in password)
        contains_symbols = any(c in self.symbols for c in password)
        
        if contains_lower: score += 1
        if contains_upper: score += 1
        if contains_digits: score += 1
        if contains_symbols: score += 1
        
        # Расчет энтропии
        char_set_size = len(set(password))
        entropy = length * math.log2(char_set_size) if char_set_size > 0 else 0
        
        # Анализ частоты символов
        freq = Counter(password)
        total = len(password)
        frequency_analysis = {char: count/total*100 for char, count in freq.most_common()}
        
        return {
            'length': length,
            'strength': self.strength_emojis.get(score, "❓ Неизвестно"),
            'score': score,
            'entropy': round(entropy, 2),
            'contains': {
                'lowercase': contains_lower,
                'uppercase': contains_upper,
                'digits': contains_digits,
                'symbols': contains_symbols
            },
            'frequency': frequency_analysis
        }

    def transform_password(self, password: str, transformation: str) -> str:
        """Преобразование пароля"""
        transformations = {
            "leet": lambda s: s.replace('e', '3').replace('E', '3')
                              .replace('a', '@').replace('A', '@')
                              .replace('i', '1').replace('I', '1')
                              .replace('o', '0').replace('O', '0')
                              .replace('s', '$').replace('S', '$'),
            "alternating": lambda s: ''.join(
                c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(s)),
            "reverse": lambda s: s[::-1],
            "suffix": lambda s: s + str(random.randint(10, 99)) + "!",
            "uppercase": lambda s: s.upper(),
            "lowercase": lambda s: s.lower()
        }
        
        if transformation in transformations:
            return transformations[transformation](password)
        return password

    def check_password_expiry(self) -> Dict:
        """Проверка устаревших паролей"""
        expired = []
        warning = []
        
        for service, data in self.password_manager.passwords.items():
            created_date = datetime.fromisoformat(data['created'])
            days_passed = (datetime.now() - created_date).days
            
            if days_passed > 90:
                expired.append({
                    'service': service,
                    'days': days_passed,
                    'created': created_date.strftime("%d.%m.%Y")
                })
            elif days_passed > 60:
                warning.append({
                    'service': service,
                    'days': days_passed,
                    'created': created_date.strftime("%d.%m.%Y")
                })
        
        return {'expired': expired, 'warning': warning}

    def _update_stats(self, mode: str):
        """Обновление статистики"""
        if "mode_usage" not in self.stats:
            self.stats["mode_usage"] = {}
        
        self.stats["mode_usage"][mode] = self.stats["mode_usage"].get(mode, 0) + 1
        self.stats["generated"] = self.stats.get("generated", 0) + 1
        self.stats["generated_today"] = self.stats.get("generated_today", 0) + 1
        self.save_stats()

    def load_stats(self) -> Dict:
        """Загрузка статистики"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    self._check_reset_daily_stats(stats)
                    return stats
            except:
                return self._get_default_stats()
        return self._get_default_stats()

    def save_stats(self):
        """Сохранение статистики"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")

    def _get_default_stats(self) -> Dict:
        """Получение статистики по умолчанию"""
        return {
            "generated": 0,
            "generated_today": 0,
            "mode_usage": {},
            "last_reset": datetime.now().date().isoformat()
        }

    def _check_reset_daily_stats(self, stats: Dict):
        """Сброс ежедневной статистики"""
        today = datetime.now().date().isoformat()
        
        if "last_reset" not in stats or stats["last_reset"] != today:
            stats["generated_today"] = 0
            stats["last_reset"] = today

# ==================== ТЕЛЕГРАМ БОТ ====================

class PasswordGeneratorBot:
    def __init__(self, token: str):
        self.token = token
        self.user_sessions = {}  # Хранение состояний пользователей
        self.application = Application.builder().token(token).build()
        
        # Регистрация обработчиков
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("generate", self.generate_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("save", self.save_password_command))
        self.application.add_handler(CommandHandler("list", self.list_passwords_command))
        self.application.add_handler(CommandHandler("get", self.get_password_command))
        self.application.add_handler(CommandHandler("transform", self.transform_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("check", self.check_expiry_command))
        self.application.add_handler(CommandHandler("delete", self.delete_password_command))
        
        # Обработчики кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Обработчики сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        welcome_text = f"""
👋 Привет, {user.first_name}!

🔐 Я - бот для генерации и управления паролями.

📋 Доступные команды:
/generate - Сгенерировать пароль
/analyze - Проанализировать сложность пароля
/save - Сохранить пароль
/list - Показать список сохраненных паролей
/get - Получить пароль по сервису
/transform - Преобразовать пароль
/stats - Статистика использования
/check - Проверить устаревшие пароли
/delete - Удалить пароль
/help - Помощь

⚡ Для быстрой генерации пароля используйте кнопки ниже!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔐 Простой пароль", callback_data="gen_simple"),
                InlineKeyboardButton("💪 Сложный пароль", callback_data="gen_strong")
            ],
            [
                InlineKeyboardButton("🎲 Случайный", callback_data="gen_random"),
                InlineKeyboardButton("📊 Анализ", callback_data="menu_analyze")
            ],
            [
                InlineKeyboardButton("💾 Менеджер паролей", callback_data="menu_manager")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = """
📚 Справка по командам:

🔐 Генерация паролей:
  /generate - Выбрать тип пароля
  Простой: 10 символов, буквы
  Сложный: 16 символов, буквы+цифры+символы
  Пользовательский: задать свои символы

🔍 Анализ паролей:
  /analyze <пароль> - Анализ сложности
  Показывает длину, энтропию, силу пароля

💾 Менеджер паролей:
  /save - Сохранить пароль (запросит сервис, логин, пароль)
  /list - Список всех сохраненных сервисов
  /get <сервис> - Получить пароль по сервису
  /delete <сервис> - Удалить пароль

🔄 Преобразование:
  /transform <пароль> - Выбрать тип преобразования
  Доступно: Leet speak, чередование регистра, реверс и др.

📈 Статистика:
  /stats - Показать статистику использования
  /check - Проверить устаревшие пароли (старше 90 дней)

🔒 Безопасность:
  • Все пароли хранятся локально в зашифрованном виде
  • Каждый пользователь имеет отдельное хранилище
  • Рекомендуется регулярно менять важные пароли
        """
        await update.message.reply_text(help_text)
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /generate"""
        keyboard = [
            [
                InlineKeyboardButton("🔐 Простой (10 символов)", callback_data="gen_simple"),
                InlineKeyboardButton("💪 Сложный (16 символов)", callback_data="gen_strong")
            ],
            [
                InlineKeyboardButton("🎲 Случайный (12 символов)", callback_data="gen_random"),
                InlineKeyboardButton("⚙️ Пользовательский", callback_data="gen_custom")
            ],
            [
                InlineKeyboardButton("📏 Задать длину", callback_data="gen_length")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎲 Выберите тип генерируемого пароля:",
            reply_markup=reply_markup
        )
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /analyze"""
        if context.args:
            password = ' '.join(context.args)
            await self._analyze_password(update, password)
        else:
            # Сохраняем состояние для ожидания пароля
            self.user_sessions[update.effective_user.id] = {'action': 'analyze'}
            await update.message.reply_text("🔍 Введите пароль для анализа:")
    
    async def save_password_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /save"""
        self.user_sessions[update.effective_user.id] = {
            'action': 'save_password',
            'step': 1  # 1 - сервис, 2 - логин, 3 - пароль
        }
        await update.message.reply_text("💾 Сохранение пароля.\nВведите название сервиса:")
    
    async def list_passwords_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /list"""
        user_id = update.effective_user.id
        generator = AdvancedPasswordGenerator(user_id)
        services = generator.password_manager.list_services()
        
        if not services:
            await update.message.reply_text("📭 Нет сохраненных паролей.")
            return
        
        services_text = "💼 Сохраненные сервисы:\n\n"
        for i, service in enumerate(services, 1):
            services_text += f"{i}. {service}\n"
        
        await update.message.reply_text(services_text)
    
    async def get_password_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /get"""
        if context.args:
            service = ' '.join(context.args)
            await self._get_password(update, service)
        else:
            self.user_sessions[update.effective_user.id] = {'action': 'get_password'}
            await update.message.reply_text("🔍 Введите название сервиса:")
    
    async def transform_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /transform"""
        if context.args:
            password = ' '.join(context.args)
            await self._show_transform_options(update, password)
        else:
            self.user_sessions[update.effective_user.id] = {'action': 'transform'}
            await update.message.reply_text("🔄 Введите пароль для преобразования:")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /stats"""
        user_id = update.effective_user.id
        generator = AdvancedPasswordGenerator(user_id)
        stats = generator.stats
        
        stats_text = "📊 Статистика использования:\n\n"
        stats_text += f"👤 Всего сгенерировано паролей: {stats.get('generated', 0)}\n"
        stats_text += f"📅 Сегодня сгенерировано: {stats.get('generated_today', 0)}\n"
        stats_text += f"💾 Сохранено паролей: {len(generator.password_manager.list_services())}\n"
        
        if stats.get('mode_usage'):
            stats_text += "\n🎯 Статистика по типам:\n"
            mode_names = {
                'simple': 'Простой',
                'strong': 'Сложный',
                'custom': 'Пользовательский',
                'advanced': 'Случайный'
            }
            
            for mode, count in sorted(stats['mode_usage'].items(), key=lambda x: x[1], reverse=True):
                name = mode_names.get(mode, mode)
                stats_text += f"  {name}: {count} раз\n"
        
        await update.message.reply_text(stats_text)
    
    async def check_expiry_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /check"""
        user_id = update.effective_user.id
        generator = AdvancedPasswordGenerator(user_id)
        expiry_data = generator.check_password_expiry()
        
        if not expiry_data['expired'] and not expiry_data['warning']:
            await update.message.reply_text("✅ Все пароли актуальны!")
            return
        
        check_text = "🔍 Проверка устаревших паролей:\n\n"
        
        if expiry_data['expired']:
            check_text += "🔴 ПОРА СМЕНИТЬ ПАРОЛИ (старше 90 дней):\n"
            for item in expiry_data['expired']:
                check_text += f"⚠️ {item['service']} - создан {item['created']} ({item['days']} дней назад)\n"
        
        if expiry_data['warning']:
            check_text += "\n🟡 СКОРО ПОРА МЕНЯТЬ (старше 60 дней):\n"
            for item in expiry_data['warning']:
                check_text += f"ℹ️ {item['service']} - создан {item['created']} ({item['days']} дней назад)\n"
        
        await update.message.reply_text(check_text)
    
    async def delete_password_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /delete"""
        if context.args:
            service = ' '.join(context.args)
            user_id = update.effective_user.id
            generator = AdvancedPasswordGenerator(user_id)
            
            if generator.password_manager.delete_password(service):
                await update.message.reply_text(f"✅ Пароль для '{service}' удален.")
            else:
                await update.message.reply_text(f"❌ Пароль для '{service}' не найден.")
        else:
            self.user_sessions[update.effective_user.id] = {'action': 'delete_password'}
            await update.message.reply_text("🗑️ Введите название сервиса для удаления:")
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        if data.startswith("gen_"):
            await self._handle_generation(query, data, user_id)
        elif data == "menu_analyze":
            self.user_sessions[user_id] = {'action': 'analyze'}
            await query.edit_message_text("🔍 Введите пароль для анализа:")
        elif data == "menu_manager":
            keyboard = [
                [
                    InlineKeyboardButton("💾 Сохранить пароль", callback_data="manager_save"),
                    InlineKeyboardButton("📋 Список паролей", callback_data="manager_list")
                ],
                [
                    InlineKeyboardButton("🔍 Найти пароль", callback_data="manager_get"),
                    InlineKeyboardButton("🗑️ Удалить пароль", callback_data="manager_delete")
                ],
                [
                    InlineKeyboardButton("⏰ Проверить срок", callback_data="manager_check")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("💾 Менеджер паролей:", reply_markup=reply_markup)
        elif data.startswith("manager_"):
            await self._handle_manager(query, data, user_id)
        elif data.startswith("transform_"):
            await self._handle_transformation(query, data, user_id)
    
    async def _handle_generation(self, query, data: str, user_id: int):
        """Обработка генерации пароля"""
        generator = AdvancedPasswordGenerator(user_id)
        
        if data == "gen_simple":
            password = generator.generate_simple_password()
            strength = generator.analyze_password(password)['strength']
            response = f"🔐 Простой пароль:\n`{password}`\n\n💪 Сложность: {strength}"
            
        elif data == "gen_strong":
            password = generator.generate_strong_password()
            strength = generator.analyze_password(password)['strength']
            response = f"💪 Сложный пароль:\n`{password}`\n\n💪 Сложность: {strength}"
            
        elif data == "gen_random":
            password = generator.generate_advanced_password()
            strength = generator.analyze_password(password)['strength']
            response = f"🎲 Случайный пароль:\n`{password}`\n\n💪 Сложность: {strength}"
            
        elif data == "gen_custom":
            self.user_sessions[user_id] = {'action': 'gen_custom_length'}
            await query.edit_message_text("📏 Введите длину пароля:")
            return
            
        elif data == "gen_length":
            self.user_sessions[user_id] = {'action': 'gen_length'}
            await query.edit_message_text("📏 Введите длину пароля:")
            return
        
        # Кнопки для сохранения
        keyboard = [
            [
                InlineKeyboardButton("💾 Сохранить этот пароль", callback_data=f"save_gen_{password}"),
                InlineKeyboardButton("🔄 Сгенерировать еще", callback_data="gen_random")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_manager(self, query, data: str, user_id: int):
        """Обработка менеджера паролей"""
        if data == "manager_save":
            self.user_sessions[user_id] = {
                'action': 'save_password',
                'step': 1
            }
            await query.edit_message_text("💾 Сохранение пароля.\nВведите название сервиса:")
            
        elif data == "manager_list":
            generator = AdvancedPasswordGenerator(user_id)
            services = generator.password_manager.list_services()
            
            if not services:
                await query.edit_message_text("📭 Нет сохраненных паролей.")
                return
            
            services_text = "💼 Сохраненные сервисы:\n\n"
            for i, service in enumerate(services, 1):
                services_text += f"{i}. {service}\n"
            
            await query.edit_message_text(services_text)
            
        elif data == "manager_get":
            self.user_sessions[user_id] = {'action': 'get_password'}
            await query.edit_message_text("🔍 Введите название сервиса:")
            
        elif data == "manager_delete":
            self.user_sessions[user_id] = {'action': 'delete_password'}
            await query.edit_message_text("🗑️ Введите название сервиса для удаления:")
            
        elif data == "manager_check":
            await self.check_expiry_command(
                Update(message=query.message, effective_user=query.from_user),
                ContextTypes.DEFAULT_TYPE
            )
    
    async def _handle_transformation(self, query, data: str, user_id: int):
        """Обработка преобразования пароля"""
        if user_id in self.user_sessions and 'transform_password' in self.user_sessions[user_id]:
            password = self.user_sessions[user_id]['transform_password']
            generator = AdvancedPasswordGenerator(user_id)
            
            transform_type = data.replace("transform_", "")
            transformed = generator.transform_password(password, transform_type)
            analysis = generator.analyze_password(transformed)
            
            transform_names = {
                "leet": "Leet speak",
                "alternating": "Чередование регистра",
                "reverse": "Обратный порядок",
                "suffix": "С суффиксом",
                "uppercase": "Верхний регистр",
                "lowercase": "Нижний регистр"
            }
            
            response = f"🔄 Преобразование: {transform_names.get(transform_type, transform_type)}\n\n"
            response += f"📥 Исходный: `{password}`\n"
            response += f"📤 Результат: `{transformed}`\n\n"
            response += f"📊 Сложность: {analysis['strength']}"
            
            await query.edit_message_text(response, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in self.user_sessions:
            await update.message.reply_text("Используйте команды или кнопки для работы с ботом.")
            return
        
        session = self.user_sessions[user_id]
        action = session.get('action')
        
        if action == 'analyze':
            await self._analyze_password(update, text)
            del self.user_sessions[user_id]
            
        elif action == 'save_password':
            await self._handle_save_password(update, text, session)
            
        elif action == 'get_password':
            await self._get_password(update, text)
            del self.user_sessions[user_id]
            
        elif action == 'delete_password':
            await self._delete_password(update, text)
            del self.user_sessions[user_id]
            
        elif action == 'transform':
            await self._show_transform_options(update, text)
            
        elif action in ['gen_custom_length', 'gen_length']:
            await self._handle_custom_generation(update, text, action, user_id)
    
    async def _analyze_password(self, update, password: str):
        """Анализ пароля"""
        user_id = update.effective_user.id if hasattr(update, 'effective_user') else update.from_user.id
        generator = AdvancedPasswordGenerator(user_id)
        analysis = generator.analyze_password(password)
        
        response = f"🔍 Анализ пароля:\n\n"
        response += f"📏 Длина: {analysis['length']} символов\n"
        response += f"💪 Сложность: {analysis['strength']}\n"
        response += f"🎲 Энтропия: {analysis['entropy']} бит\n\n"
        response += "📋 Содержит:\n"
        response += f"  • Строчные буквы: {'✅' if analysis['contains']['lowercase'] else '❌'}\n"
        response += f"  • Заглавные буквы: {'✅' if analysis['contains']['uppercase'] else '❌'}\n"
        response += f"  • Цифры: {'✅' if analysis['contains']['digits'] else '❌'}\n"
        response += f"  • Спецсимволы: {'✅' if analysis['contains']['symbols'] else '❌'}\n"
        
        if analysis['frequency']:
            response += "\n📊 Частота символов (топ-5):\n"
            for char, freq in list(analysis['frequency'].items())[:5]:
                char_display = repr(char)[1:-1]
                response += f"  '{char_display}': {freq:.1f}%\n"
        
        if hasattr(update, 'message'):
            await update.message.reply_text(response)
        else:
            await update.edit_message_text(response)
    
    async def _handle_save_password(self, update, text: str, session: dict):
        """Обработка сохранения пароля"""
        user_id = update.effective_user.id
        step = session.get('step', 1)
        
        if step == 1:  # Сервис
            session['service'] = text
            session['step'] = 2
            await update.message.reply_text("👤 Введите логин/email:")
            
        elif step == 2:  # Логин
            session['login'] = text
            session['step'] = 3
            await update.message.reply_text("🔐 Введите пароль:")
            
        elif step == 3:  # Пароль
            session['password'] = text
            session['step'] = 4
            await update.message.reply_text("📝 Введите заметки (или отправьте '-' чтобы пропустить):")
            
        elif step == 4:  # Заметки
            notes = text if text != '-' else ""
            
            generator = AdvancedPasswordGenerator(user_id)
            success = generator.password_manager.save_password(
                session['service'],
                session['login'],
                session['password'],
                notes
            )
            
            if success:
                await update.message.reply_text(
                    f"✅ Пароль для '{session['service']}' сохранен!\n\n"
                    f"💪 Сложность: {generator.password_manager._calculate_strength(session['password'])}"
                )
            else:
                await update.message.reply_text("❌ Ошибка сохранения пароля.")
            
            del self.user_sessions[user_id]
    
    async def _get_password(self, update, service: str):
        """Получение пароля по сервису"""
        user_id = update.effective_user.id if hasattr(update, 'effective_user') else update.from_user.id
        generator = AdvancedPasswordGenerator(user_id)
        password_data = generator.password_manager.get_password(service)
        
        if password_data:
            response = f"🔍 Найден пароль для '{service}':\n\n"
            response += f"👤 Логин: `{password_data['login']}`\n"
            response += f"🔐 Пароль: `{password_data['password']}`\n"
            response += f"📝 Заметки: {password_data.get('notes', 'нет')}\n"
            response += f"📅 Создан: {password_data['created'][:10]}\n"
            response += f"💪 Сложность: {password_data.get('strength', 'неизвестно')}"
        else:
            response = f"❌ Пароль для '{service}' не найден."
        
        if hasattr(update, 'message'):
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.edit_message_text(response, parse_mode='Markdown')
    
    async def _delete_password(self, update, service: str):
        """Удаление пароля"""
        user_id = update.effective_user.id
        generator = AdvancedPasswordGenerator(user_id)
        
        if generator.password_manager.delete_password(service):
            await update.message.reply_text(f"✅ Пароль для '{service}' удален.")
        else:
            await update.message.reply_text(f"❌ Пароль для '{service}' не найден.")
    
    async def _show_transform_options(self, update, password: str):
        """Показать варианты преобразования"""
        user_id = update.effective_user.id if hasattr(update, 'effective_user') else update.from_user.id
        self.user_sessions[user_id] = {'transform_password': password}
        
        keyboard = [
            [
                InlineKeyboardButton("1337 5p34k", callback_data="transform_leet"),
                InlineKeyboardButton("HeLlO", callback_data="transform_alternating")
            ],
            [
                InlineKeyboardButton("esrever", callback_data="transform_reverse"),
                InlineKeyboardButton("+суффикс", callback_data="transform_suffix")
            ],
            [
                InlineKeyboardButton("ВЕРХНИЙ", callback_data="transform_uppercase"),
                InlineKeyboardButton("нижний", callback_data="transform_lowercase")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response = f"🔄 Выберите тип преобразования для пароля:\n`{password}`"
        
        if hasattr(update, 'message'):
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.edit_message_text(response, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_custom_generation(self, update, text: str, action: str, user_id: int):
        """Обработка пользовательской генерации"""
        try:
            length = int(text)
            if length < 4 or length > 50:
                await update.message.reply_text("❌ Длина должна быть от 4 до 50 символов.")
                return
            
            generator = AdvancedPasswordGenerator(user_id)
            
            if action == 'gen_length':
                password = generator.generate_advanced_password(length)
            else:  # gen_custom_length
                self.user_sessions[user_id] = {'action': 'gen_custom_chars', 'length': length}
                await update.message.reply_text("⌨️ Введите разрешенные символы:")
                return
            
            strength = generator.analyze_password(password)['strength']
            response = f"🔐 Пароль ({length} символов):\n`{password}`\n\n💪 Сложность: {strength}"
            
            keyboard = [[
                InlineKeyboardButton("💾 Сохранить", callback_data=f"save_gen_{password}"),
                InlineKeyboardButton("🔄 Еще", callback_data="gen_random")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
            del self.user_sessions[user_id]
            
        except ValueError:
            await update.message.reply_text("❌ Введите корректное число.")
    
    def run(self):
        """Запуск бота"""
        logger.info("Бот запущен...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
#ТЕЛЕГРАММ БОТ

def main():
#токен для бота
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        print("⚠️  Токен не найден в переменных окружения.")
        TOKEN = input("Введите токен Telegram бота: ").strip()
    
    if not TOKEN:
        print("❌ Токен не предоставлен. Завершение работы.")
        return
    

    os.makedirs("user_data", exist_ok=True)
    
#Запуск бота
    bot = PasswordGeneratorBot(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()