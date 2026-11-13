import asyncio
import logging
import random
import os
import pandas as pd
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "YOUR_BOT_TOKEN_HERE"
EXCEL_FILE = "tests_db.xlsx"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 4 ta interfeys tili uchun tarjimalar va matnlar
UI_TEXTS = {
    "uz": {
        "select_ui_lang": "🇺🇿 Interfeys tilini tanlang:",
        "main_menu": "🎯 Kerakli bo'limni tanlang:",
        "btn_school": "📚 Maktab fanlari (1-11 sinf)",
        "btn_languages": "🗣 Xorijiy tillar va O'zbek tili",
        "choose_grade": "📚 Sinfni tanlang (Yangi nashr darsliklari):",
        "choose_lang_section": "🗣 O'rganmoqchi bo'lgan tilingizni tanlang:",
        "choose_category": "📂 Bo'limni tanlang:",
        "btn_grammar": "✍️ Grammatika",
        "btn_vocabulary": "📖 So'z boyligi (Leksika)",
        "btn_general": "📊 Umumiy testlar",
        "choose_subj": "📖 Fanni tanlang:",
        "no_tests": "⚠️ Kechirasiz, bu yo'nalish bo'yicha testlar hali bazaga kiritilmagan.",
        "question": "❓ <b>Savol {curr}/{total}:</b>\n\n{q}\n\nA) {a}\nB) {b}\nC) {c}\nD) {d}",
        "finish": "🏁 <b>Test yakunlandi!</b>\n\n✅ To'g'ri javoblar: {score} / {total}\n📊 Natija: {percent}%",
        "restart": "🔄 Asosiy menyuga qaytish",
        "back": "🔙 Ortga"
    },
    "ru": {
        "select_ui_lang": "🇷🇺 Выберите язык интерфейса:",
        "main_menu": "🎯 Выберите нужный раздел:",
        "btn_school": "📚 Школьные предметы (1-11 классы)",
        "btn_languages": "🗣 Иностранные языки и узбекский",
        "choose_grade": "📚 Выберите класс (учебники нового издания):",
        "choose_lang_section": "🗣 Выберите язык для изучения:",
        "choose_category": "📂 Выберите раздел:",
        "btn_grammar": "✍️ Грамматика",
        "btn_vocabulary": "📖 Словарный запас",
        "btn_general": "📊 Общие тесты",
        "choose_subj": "📖 Выберите предмет:",
        "no_tests": "⚠️ Извините, тесты по этому направлению еще не добавлены.",
        "question": "❓ <b>Вопрос {curr}/{total}:</b>\n\n{q}\n\nA) {a}\nB) {b}\nC) {c}\nD) {d}",
        "finish": "🏁 <b>Тест завершен!</b>\n\n✅ Правильных ответов: {score} / {total}\n📊 Результат: {percent}%",
        "restart": "🔄 Главное меню",
        "back": "🔙 Назад"
    },
    "en": {
        "select_ui_lang": "🇬🇧 Select interface language:",
        "main_menu": "🎯 Select the required section:",
        "btn_school": "📚 School Subjects (Grades 1-11)",
        "btn_languages": "🗣 Foreign Languages & Uzbek",
        "choose_grade": "📚 Select Grade (New edition textbooks):",
        "choose_lang_section": "🗣 Select language to learn:",
        "choose_category": "📂 Select category:",
        "btn_grammar": "✍️ Grammar",
        "btn_vocabulary": "📖 Vocabulary",
        "btn_general": "📊 General Tests",
        "choose_subj": "📖 Select subject:",
        "no_tests": "⚠️ Sorry, tests for this section are not added yet.",
        "question": "❓ <b>Question {curr}/{total}:</b>\n\n{q}\n\nA) {a}\nB) {b}\nC) {c}\nD) {d}",
        "finish": "🏁 <b>Test completed!</b>\n\n✅ Correct answers: {score} / {total}\n📊 Score: {percent}%",
        "restart": "🔄 Main Menu",
        "back": "🔙 Back"
    },
    "de": {
        "select_ui_lang": "🇩🇪 Wählen Sie die Menüsprache:",
        "main_menu": "🎯 Wählen Sie den gewünschten Bereich:",
        "btn_school": "📚 Schulfächer (Klassen 1-11)",
        "btn_languages": "🗣 Fremdsprachen & Usbekisch",
        "choose_grade": "📚 Wählen Sie die Klasse (Neue Lehrbücher):",
        "choose_lang_section": "🗣 Wählen Sie die zu lernende Sprache:",
        "choose_category": "📂 Wählen Sie die Kategorie:",
        "btn_grammar": "✍️ Grammatik",
        "btn_vocabulary": "📖 Wortschatz",
        "btn_general": "📊 Allgemeine Tests",
        "choose_subj": "📖 Wählen Sie das Fach:",
        "no_tests": "⚠️ Entschuldigung, Tests für diesen Bereich sind noch nicht hinzugefügt.",
        "question": "❓ <b>Frage {curr}/{total}:</b>\n\n{q}\n\nA) {a}\nB) {b}\nC) {c}\nD) {d}",
        "finish": "🏁 <b>Test abgeschlossen!</b>\n\n✅ Richtige Antworten: {score} / {total}\n📊 Ergebnis: {percent}%",
        "restart": "🔄 Hauptmenü",
        "back": "🔙 Zurück"
    }
}

# Yangi nashr darsliklari asosidagi maktab fanlari
SCHOOL_SUBJECTS = {
    "1-4": ["Ona tili va o'qish", "Matematika", "Tabiiy fanlar (Science)", "Tarbiya", "Ingliz tili"],
    "5-6": ["Ona tili", "Adabiyot", "Matematika", "Tabiiy fanlar (Science)", "Tarix", "Informatika", "Tarbiya", "Ingliz tili"],
    "7-11": ["Ona tili", "Adabiyot", "Algebra", "Geometriya", "Fizika", "Kimyo", "Biologiya", "Geografiya", "O'zbekiston tarixi", "Jahon tarixi", "Informatika", "Huquq asoslari"]
}

# 6 ta til (Xitoy, Ingliz, Rus, Nemis, Arab, O'zbek)
FOREIGN_LANGUAGES = {
    "lang_en": "🇬🇧 Ingliz tili (English)",
    "lang_ru": "🇷🇺 Rus tili (Русский)",
    "lang_de": "🇩🇪 Nemis tili (Deutsch)",
    "lang_zh": "🇨🇳 Xitoy tili (中文)",
    "lang_ar": "🇸🇦 Arab tili (العربية)",
    "lang_uz": "🇺🇿 O'zbek tili"
}

class TestState(StatesGroup):
    choosing_ui_lang = State()
    choosing_section = State()
    choosing_grade = State()
    choosing_lang_item = State()
    choosing_category = State()
    choosing_subject = State()
    solving_test = State()

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="ui_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ui_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="ui_en"),
         InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="ui_de")]
    ])
    await message.answer("🌐 Interfeys tilini tanlang / Select interface language:", reply_markup=keyboard)
    await state.set_state(TestState.choosing_ui_lang)

@dp.callback_query(F.data.startswith("ui_"))
async def process_ui_language(callback: types.CallbackQuery, state: FSMContext):
    ui_lang = callback.data.split("_")[1]
    await state.update_data(ui_lang=ui_lang)
    
    t = UI_TEXTS[ui_lang]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_school"], callback_data="section_school")],
        [InlineKeyboardButton(text=t["btn_languages"], callback_data="section_languages")]
    ])
    await callback.message.edit_text(t["main_menu"], reply_markup=keyboard)
    await state.set_state(TestState.choosing_section)

@dp.callback_query(F.data == "section_school")
async def process_section_school(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    t = UI_TEXTS[data["ui_lang"]]
    
    buttons, row = [], []
    for grade in range(1, 12):
        row.append(InlineKeyboardButton(text=f"{grade}-sinf", callback_data=f"grade_{grade}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t["back"], callback_data="back_to_main")])
    
    await callback.message.edit_text(t["choose_grade"], reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(TestState.choosing_grade)

@dp.callback_query(F.data == "section_languages")
async def process_section_languages(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    t = UI_TEXTS[data["ui_lang"]]
    
    buttons = []
    for code, name in FOREIGN_LANGUAGES.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=code)])
    buttons.append([InlineKeyboardButton(text=t["back"], callback_data="back_to_main")])
    
    await callback.message.edit_text(t["choose_lang_section"], reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(TestState.choosing_lang_item)

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ui_lang = data.get("ui_lang", "uz")
    t = UI_TEXTS[ui_lang]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_school"], callback_data="section_school")],
        [InlineKeyboardButton(text=t["btn_languages"], callback_data="section_languages")]
    ])
    await callback.message.edit_text(t["main_menu"], reply_markup=keyboard)
    await state.set_state(TestState.choosing_section)

@dp.callback_query(F.data.startswith("grade_"))
async def process_grade(callback: types.CallbackQuery, state: FSMContext):
    grade = int(callback.data.split("_")[1])
    data = await state.get_data()
    t = UI_TEXTS[data["ui_lang"]]
    await state.update_data(grade=grade, subject_type="school")
    
    if grade <= 4:
        subjects = SCHOOL_SUBJECTS["1-4"]
    elif grade <= 6:
        subjects = SCHOOL_SUBJECTS["5-6"]
    else:
        subjects = SCHOOL_SUBJECTS["7-11"]
        
    buttons = [[InlineKeyboardButton(text=subj, callback_data=f"subj_{idx}")] for idx, subj in enumerate(subjects)]
    buttons.append([InlineKeyboardButton(text=t["back"], callback_data="section_school")])
    await state.update_data(available_subjects=subjects)
    
    await callback.message.edit_text(f"📖 {grade}-sinf fanlari:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(TestState.choosing_subject)

@dp.callback_query(F.data.startswith("lang_"))
async def process_foreign_language(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data # masalan: lang_en, lang_zh
    data = await state.get_data()
    t = UI_TEXTS[data["ui_lang"]]
    await state.update_data(lang_code=lang_code, grade=0, subject_type="foreign")
    
    # Xorijiy tillar uchun bo'limlar: Grammatika, So'z boyligi, Umumiy
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_grammar"], callback_data="cat_grammar")],
        [InlineKeyboardButton(text=t["btn_vocabulary"], callback_data="cat_vocab")],
        [InlineKeyboardButton(text=t["btn_general"], callback_data="cat_general")],
        [InlineKeyboardButton(text=t["back"], callback_data="section_languages")]
    ])
    await callback.message.edit_text(t["choose_category"], reply_markup=keyboard)
    await state.set_state(TestState.choosing_category)

@dp.callback_query(F.data.startswith("cat_"))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.split("_")[1] # grammar, vocab, general
    data = await state.get_data()
    t = UI_TEXTS[data["ui_lang"]]
    lang_code = data["lang_code"]
    
    # Bazadan yuklash (subject = lang_code + "_" + cat, masalan: lang_en_grammar)
    subject_key = f"{lang_code}_{cat}"
    questions = load_tests(0, subject_key)
    
    if not questions:
        await callback.answer(t["no_tests"], show_alert=True)
        return
        
    await state.update_data(questions=questions, current_idx=0, score=0)
    await send_question(callback.message, state)
    await state.set_state(TestState.solving_test)

@dp.callback_query(F.data.startswith("subj_"))
async def process_subject(callback: types.CallbackQuery, state: FSMContext):
    subj_idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    t = UI_TEXTS[data["ui_lang"]]
    grade = data["grade"]
    subject = data["available_subjects"][subj_idx]
    
    questions = load_tests(grade, subject)
    if not questions:
        await callback.answer(t["no_tests"], show_alert=True)
        return
        
    await state.update_data(questions=questions, current_idx=0, score=0)
    await send_question(callback.message, state)
    await state.set_state(TestState.solving_test)

def load_tests(grade: int, subject: str):
    if not os.path.exists(EXCEL_FILE):
        return []
    try:
        df = pd.read_excel(EXCEL_FILE)
        filtered = df[(df['grade'] == grade) & (df['subject'].astype(str).str.strip() == str(subject).strip())]
        questions = filtered.to_dict('records')
        random.shuffle(questions)
        return questions[:10]  # Har safar 10 tadan tasodifiy savol
    except Exception as e:
        logging.error(f"Excel o'qishda xato: {e}")
        return []

async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    t = UI_TEXTS[data["ui_lang"]]
    idx = data["current_idx"]
    questions = data["questions"]
    
    if idx >= len(questions):
        total = len(questions)
        score = data["score"]
        percent = round((score / total) * 100) if total > 0 else 0
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["restart"], callback_data="back_to_main")]
        ])
        await message.edit_text(
            t["finish"].format(score=score, total=total, percent=percent),
            parse_mode="HTML",
            reply_markup=kb
        )
        return
        
    q_data = questions[idx]
    text = t["question"].format(
        curr=idx + 1, total=len(questions),
        q=q_data['question'], a=q_data['opt_a'], b=q_data['opt_b'], c=q_data['opt_c'], d=q_data['opt_d']
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A", callback_data="ans_A"),
         InlineKeyboardButton(text="B", callback_data="ans_B")],
        [InlineKeyboardButton(text="C", callback_data="ans_C"),
         InlineKeyboardButton(text="D", callback_data="ans_D")]
    ])
    await message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.startswith("ans_"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    chosen = callback.data.split("_")[1]
    data = await state.get_data()
    idx = data["current_idx"]
    correct = str(data["questions"][idx]["correct"]).strip().upper()
    
    score = data["score"] + (1 if chosen == correct else 0)
    await state.update_data(current_idx=idx + 1, score=score)
    await send_question(callback.message, state)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
