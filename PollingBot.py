import logging
from datetime import datetime, timezone

from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    PollAnswerHandler,
    PollHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

token = '1691123609:AAED96Yb-mhgf84rP_P8vOxpDqG3QxsnY-0'#봇토큰
chat_id = '-443191914'#뿌릴 단톡방 id



def poll(update: Update, context: CallbackContext) -> None:
    """Sends a predefined poll for command handler"""
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = context.bot.send_poll(
        update.effective_chat.id,
        # chat_id,
        "How are you?",
        questions,
        is_anonymous=False,

    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            # "chat_id": update.effective_chat.id,
            "chat_id": chat_id,

            "answers": 0,
        }
    }
    context.bot_data.update(payload)

def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} feels {answer_string}!",
        parse_mode=ParseMode.HTML,
    )
    context.bot_data[poll_id]["answers"] += 1


    votes_dict = context.bot_data.copy()
    if votes_dict[poll_id]["answers"] == 1:
        votes_dict[poll_id]["selected_option"] = []
        for i in range(len(questions)):
            votes_dict[poll_id]["selected_option"].append(0)
    votes_dict[poll_id]["selected_option"][selected_options[0]] +=1
    votes_dict[poll_id]["last_update_utc"] = datetime.now(timezone.utc).timestamp()
    print(votes_dict)



    # Close poll after three participants voted
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token = token)
    dispatcher = updater.dispatcher

    # 여기서, 내가 원하는 컨디션을 받았을 때
    if datetime.today().day == 21: #예시 조건. 우리의 예에서는 가격이 평가절하 되었을 때 가 되겠지요.
        #이 밑으로 원하는 투표를 진행합니다.
        questions = ["Good", "Really good", "Fantastic", "Great"]
        message = updater.bot.send_poll(

            chat_id,
            "abc",
            questions,
            is_anonymous= False
        )
        payload = {
            message.poll.id: {
                "questions": questions,
                "message_id": message.message_id,
                # "chat_id": update.effective_chat.id,
                "chat_id": chat_id,

                "answers": 0,
            }
        }
    #투표 정보가 payload에 담기면, 투표 결과를 저장하기 위해 밑에 핸들러에다가 전달하게 됩니다.
    dispatcher.bot_data.update(payload)
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer)) #투표 결과는 receive_poll_answer 이 함수의 votes_dict로 저장해두면 좋을 것 같아서 print구문 넣어뒀습니다ㅠㅠ

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    # updater.idle()


if __name__ == '__main__':
    main()