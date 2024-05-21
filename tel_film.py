import telebot
import requests
import random
from datetime import datetime

# Оновлення глобальних змінних
previous_project_type = None
previous_genre = None

# Replace this with your bot token from BotFather
BOT_TOKEN = "6858386752:AAG3h1S9JmQ5sHBn_MFtJWK5SSXhMg3fS7Q"

# Replace this with your TMDb API key
TMDB_API_KEY = "7137055f507a67f6df55cedd3f872542"

# Create a bot instance
bot = telebot.TeleBot(BOT_TOKEN)

# Define a dictionary to track user satisfaction for each chat
user_satisfaction = {}

# Define a dictionary to track chosen projects to avoid repetitions
chosen_projects = {}

# Define a dictionary of genres for each project type
genres = {
    "Фільм": ["Комедія", "Драма", "Трилер", "Фантастика", "Історичний", 'Бойовик', 'Вестерн', 'Військовий',
              "Детектив", 'Документальний', 'Жахи', 'Кримінал', 'Мелодрама', 'Музика', 'Мультфільм', 'Пригоди',
              'Сімейний', 'Телефільм', 'Фантастика', 'Фентезі'],
    "Серіал": ["Комедія", "Драма", "Детектив", "Фентезі", "Анімація", 'Дитячий', 'Вестерн', 'Екшн і Пригоди',
               'Документальний', 'Кримінал', 'Мильна опера', 'Мультфільм', 'Науково фантастичний', 'Новини',
               'Політика та війна', 'Реаліті-шоу', 'Сімейний', 'Ток-шоу']
}

# Define a dictionary of genre ids for TMDb API
genre_ids = {
    "Комедія": 35,
    "Драма": 18,
    "Трилер": 53,
    "Фантастика": 878,
    "Історичний": 36,
    "Детектив": 80,
    "Фентезі": 14,
    "Анімація": 16,
    "Дитячий": 10762,
    'Вестерн': 37,
    'Екшн і Пригоди': 10759,
    'Документальний': 99,
    'Кримінал': 80,
    'Мильна опера': 10766,
    'Мультфільм': 16,
    'Науково фантастичний': 878,
    'Новини': 10763,
    'Політика та війна': 10768,
    'Реаліті-шоу': 10764,
    'Сімейний': 10751,
    'Ток-шоу': 10767,
    'Бойовик': 28,
    'Військовий': 10752,
    'Жахи': 27,
    'Мелодрама': 10749,
    'Музика': 10402,
    'Пригоди': 12,
    'Спорт': 10757,
    'Телефільм': 10770,
    'Трилер': 53
}


# Define a function to get a random project from TMDb API by genre
def get_random_project(project_type, genre):
    # Define the current date in the required format
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Start with the first page
    page = 1

    while page <= 5:  # Limit the number of pages to 5 for example

        # Construct the API url with the primary_release_date.lte parameter
        url = f"https://api.themoviedb.org/3/discover/{project_type}?api_key={TMDB_API_KEY}&language=uk-UA&sort_by=popularity.desc&include_adult=false&include_video=false&page={page}&with_genres={genre_ids[genre]}&primary_release_date.lte={current_date}"

        # Make a request to the API
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the JSON data
            data = response.json()

            # Get the list of results
            results = data["results"]

            # Check if the list is not empty
            if results:
                # Filter out already chosen projects
                filtered_results = [result for result in results if
                                    result["id"] not in chosen_projects.get(project_type, [])]

                # Check if there are available projects after filtering
                if filtered_results:
                    # Pick a random result
                    result = random.choice(filtered_results)

                    # Get the title, overview, and id of the project
                    title = result["title"] if project_type == "movie" else result["name"]
                    overview = result["overview"]
                    project_id = result["id"]

                    # Add the chosen project to the list to avoid repetition
                    chosen_projects.setdefault(project_type, []).append(project_id)

                    # Return the title, overview, and id as a tuple
                    return title, overview, project_id
                else:
                    # Move to the next page if no available projects found on this page
                    page += 1
            else:
                # Move to the next page if no results found on this page
                page += 1
        else:
            # Return an error message if the API request fails
            return "Помилка при зверненні до TMDb API.", "", None

    # Return a message if all pages have been searched and no projects found
    return "Немає доступних проектів за вашими умовами.", "", None


# Define a function to clear chosen projects
def clear_chosen_projects(message):
    # Clear the chosen projects list
    chosen_projects.clear()
    bot.send_message(message.chat.id, "Список вибраних проектів порожній.")


# Define a function to get the photo url of a project by id
def get_photo_url(project_type, project_id):
    # Construct the API url
    url = f"https://api.themoviedb.org/3/{project_type}/{project_id}/images?api_key={TMDB_API_KEY}"

    # Make a request to the API
    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()

        # Get the list of posters
        posters = data["posters"]

        # Check if the list is not empty
        if posters:
            # Pick a random poster
            poster = random.choice(posters)

            # Get the file path of the poster
            file_path = poster["file_path"]

            # Construct the photo url
            photo_url = f"https://image.tmdb.org/t/p/w500{file_path}"

            # Return the photo url
            return photo_url
        else:
            # Return an empty string
            return ""
    else:
        # Return an empty string
        return ""


# Define a function to ask user satisfaction
def ask_satisfaction(message):
    # Create a keyboard with two options
    satisfaction_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    satisfaction_keyboard.add("Так", "Ні")

    # Send a message asking for satisfaction
    bot.send_message(message.chat.id, "Чи вам сподобався цей проект?", reply_markup=satisfaction_keyboard)


# Додана функція для запиту користувачу щодо бажання подивитися наступний проект
def ask_next_project(message):
    # Створення клавіатури з двома варіантами
    next_project_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    next_project_keyboard.add("Продовжити перегляд", "Дивитись інше")

    # Відправлення повідомлення з запитом
    bot.send_message(message.chat.id, "Що ви хочете зробити далі?", reply_markup=next_project_keyboard)


# Define a function to ask user for a new project type
def ask_new_project_type(message):
    # Create a keyboard with two options
    project_type_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    project_type_keyboard.add("Фільм", "Серіал")

    # Send a message asking for a new project type
    bot.send_message(message.chat.id, "Оберіть новий Фільм чи Серіал:", reply_markup=project_type_keyboard)


def what_next(message):
    # Create a keyboard with two options
    project_type_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    project_type_keyboard.add("Продовжити перегляд", "Дивитись інше")


# Define a message handler for /start command
@bot.message_handler(commands=["start"])
def send_welcome(message):
    # Send a welcome message
    bot.send_message(message.chat.id,
                     "Привіт, я телеграм бот, який допоможе вам вибрати Фільму чи Серіалу. Будь ласка, виберіть тип проекту: фільм або серіал.")

    # Create a keyboard with two options
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Фільм", "Серіал")

    # Send the keyboard to the user
    bot.send_message(message.chat.id, "Виберіть один з варіантів:", reply_markup=keyboard)

# Define a function to continue searching for a project in the same genre
def continue_same_genre(message):
    # Remove the keyboard
    keyboard = telebot.types.ReplyKeyboardRemove()

    # Get the saved project information
    saved_project = user_satisfaction.get(message.chat.id)

    if saved_project:
        # Get the project type and genre of the saved project
        saved_project_type = "movie" if previous_project_type == "Фільм" else "tv"
        saved_genre = previous_genre

        # Get a new random project of the same genre
        new_project = get_random_project(saved_project_type, saved_genre)

        # Check if there are still available projects
        if new_project[0] != "Немає доступних проектів за вашими умовами.":
            # Get the title, overview, and id from the new project
            new_title, new_overview, new_id = new_project

            # Get the photo url of the new project by id
            new_photo_url = get_photo_url(saved_project_type, new_id)

            # Check if the photo url is not empty
            if new_photo_url:
                # Send the photo to the user
                bot.send_photo(message.chat.id, new_photo_url)

            # Send the title and overview of the new project to the user
            bot.send_message(message.chat.id, f"{new_title}\n\n{new_overview}", reply_markup=keyboard)

            # Save the new project for satisfaction tracking
            user_satisfaction[message.chat.id] = {"title": new_title, "overview": new_overview, "id": new_id}

            # Send a question about the new project satisfaction
            ask_satisfaction(message)
        else:
            # Send a message about the exhaustion of available projects
            bot.send_message(message.chat.id, "Вичерпано всі доступні проекти за вашими умовами.")
    else:
        # Send an error message
        bot.send_message(message.chat.id, "Не вдалося знайти збережений проект.")
def what_next(message):
    # Create a keyboard with two options
    next_steps_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    next_steps_keyboard.add("Продовжити перегляд", "Дивитись інше")

    # Send a message with the keyboard
    bot.send_message(message.chat.id, "Що робити далі?", reply_markup=next_steps_keyboard)


# Define a message handler for text messages
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global previous_project_type, previous_genre

    # Отримуємо вибір користувача
    choice = message.text

    # Перевіряємо, чи вибір є допустимим
    if choice in ["Фільм", "Серіал"]:
        # Прибираємо клавіатуру
        keyboard = telebot.types.ReplyKeyboardRemove()

        # Відправляємо підтвердження
        bot.send_message(message.chat.id, f"Ви вибрали {choice}. Тепер виберіть жанр проекту.", reply_markup=keyboard)

        # Створюємо клавіатуру з жанрами для обраного типу проекту
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*genres[choice])

        # Відправляємо клавіатуру користувачу
        bot.send_message(message.chat.id, "Виберіть один з варіантів:", reply_markup=keyboard)

        # Зберігаємо вибір користувача для подальшого використання
        previous_project_type = choice
    elif choice in genres["Фільм"] or choice in genres["Серіал"]:
        # Прибираємо клавіатуру
        keyboard = telebot.types.ReplyKeyboardRemove()

        # Отримуємо тип проекту від вибору користувача
        project_type = "movie" if choice == "Фільм" else "tv"

        # Зберігаємо вибір користувача для подальшого використання
        previous_genre = choice

        # Отримуємо випадковий проект від API TMDb за жанром
        project = get_random_project(project_type, choice)

        # Отримуємо назву, огляд та id проекту
        title, overview, project_id = project

        # Отримуємо URL фото проекту за його id
        photo_url = get_photo_url(project_type, project_id)

        # Перевіряємо, чи URL фото не порожній
        if photo_url:
            # Відправляємо фото користувачеві
            bot.send_photo(message.chat.id, photo_url)

        # Відправляємо назву та огляд проекту користувачеві
        bot.send_message(message.chat.id, f"{title}\n\n{overview}", reply_markup=keyboard)

        # Зберігаємо поточний проект для відстеження задоволення користувача
        user_satisfaction[message.chat.id] = {"title": title, "overview": overview, "id": project_id}

        # Запитуємо користувача про його задоволення проектом
        ask_satisfaction(message)
    elif choice.lower() == 'ні':
        # Прибираємо клавіатуру
        keyboard = telebot.types.ReplyKeyboardRemove()

        # Отримуємо збережений проект
        saved_project = user_satisfaction.get(message.chat.id)

        if saved_project:
            # Отримуємо тип та жанр збереженого проекту
            saved_project_type = "movie" if previous_project_type == "Фільм" else "tv"
            saved_genre = previous_genre

            # Отримуємо новий випадковий проект того ж жанру
            new_project = get_random_project(saved_project_type, saved_genre)

            # Перевіряємо, чи є доступні проекти
            if new_project[0] != "Немає доступних проектів за вашими умовами.":
                # Отримуємо назву, огляд та id нового проекту
                new_title, new_overview, new_id = new_project

                # Отримуємо URL фото нового проекту за його id
                new_photo_url = get_photo_url(saved_project_type, new_id)

                # Перевіряємо, чи URL фото не порожній
                if new_photo_url:
                    # Відправляємо фото користувачеві
                    bot.send_photo(message.chat.id, new_photo_url)

                # Відправляємо назву та огляд нового проекту користувачеві
                bot.send_message(message.chat.id, f"{new_title}\n\n{new_overview}", reply_markup=keyboard)

                # Зберігаємо новий проект для відстеження задоволення користувача
                user_satisfaction[message.chat.id] = {"title": new_title, "overview": new_overview, "id": new_id}

                # Запитуємо користувача про його задоволення новим проектом
                ask_satisfaction(message)
            else:
                # Відправляємо повідомлення про вичерпання доступних проектів
                bot.send_message(message.chat.id, "Вичерпано всі доступні проекти за вашими умовами.")
        else:
            # Відправляємо повідомлення про помилку
            bot.send_message(message.chat.id, "Не вдалося знайти збережений проект.")
    elif choice.lower() == 'так' and previous_project_type and previous_genre:
        # Ask what to do next
        what_next(message)
    elif choice == "Продовжити перегляд" or choice == "Дивитись інше":
        # Check if the choice is valid
        if choice == "Продовжити перегляд":
            continue_same_genre(message)
        elif choice == "Дивитись інше":
            ask_new_project_type(message)
    else:
        # Send an error message
        bot.send_message(message.chat.id, "Будь ласка, виберіть один з варіантів на клавіатурі.")


# Start polling for updates
bot.polling()
