import random
import string
import datetime
from telegram.ext import CommandHandler
from shivu import application, user_collection

last_usage_time = {}
generated_codes = {}
sudo_user_ids = ["7370080350", "6916220465", "6916220465", "6916220465"]
log_sudo_user_id = ["6916220465", "7370080350"]

def generate_random_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

async def daily_code(update, context):
    user_id = update.effective_user.id

    if user_id in last_usage_time:
        last_time = last_usage_time[user_id]
        current_time = datetime.datetime.now()
        time_diff = current_time - last_time
        if time_diff.total_seconds() < 300:
            await update.message.reply_text("You can only use this command every 5 minutes.")
            return

    code = generate_random_code()
    amount = random.randint(10, 5000000000)
    quantity = 1

    last_usage_time[user_id] = datetime.datetime.now()
    generated_codes[code] = {'amount': amount, 'quantity': quantity}

    response_text = (
        f"<b>Your daily code:</b>\n"
        f"<code>{code}</code>\n"
        f"<b>Amount:</b> {amount}\n"
        f"<b>Quantity:</b> {quantity}"
    )
    await update.message.reply_html(response_text)

    log_text = (
        f"<b>Daily code generated by user {user_id}:</b>\n"
        f"<code>{code}</code>\n"
        f"<b>Amount:</b> {amount}\n"
        f"<b>Quantity:</b> {quantity}"
    )
    await context.bot.send_message(chat_id=log_sudo_user_id, text=log_text, parse_mode='HTML')

async def gen(update, context):
    if str(update.effective_user.id) not in sudo_user_ids:
        await update.message.reply_text("You are not authorized to generate codes.")
        return

    try:
        amount = float(context.args[0])
        quantity = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid usage. Usage: /gen <amount> <quantity>")
        return

    code = generate_random_code()
    generated_codes[code] = {'amount': amount, 'quantity': quantity}

    response_text = (
        f"<b>Generated code:</b>\n"
        f"<code>{code}</code>\n"
        f"<b>Amount:</b> {amount}\n"
        f"<b>Quantity:</b> {quantity}"
    )
    await update.message.reply_html(response_text)

    log_text = (
        f"<b>Code generated by user {update.effective_user.id}:</b>\n"
        f"<code>{code}</code>\n"
        f"<b>Amount:</b> {amount}\n"
        f"<b>Quantity:</b> {quantity}"
    )
    await context.bot.send_message(chat_id=log_sudo_user_id, text=log_text, parse_mode='HTML')

async def redeem(update, context):
    code = " ".join(context.args)
    user_id = update.effective_user.id

    if code in generated_codes:
        details = generated_codes[code]

        if details['quantity'] > 0:
            amount = details['amount']
            await user_collection.update_one(
                {'id': user_id},
                {'$inc': {'balance': float(amount)}}
            )

            details['quantity'] -= 1

            if details['quantity'] == 0:
                del generated_codes[code]

            await update.message.reply_text(
                f"Code redeemed successfully. {amount} tokens added to your balance. Remaining quantity: {details['quantity']}"
            )

            log_text = (
                f"<b>Code redeemed by user {user_id}:</b>\n"
                f"<code>{code}</code>\n"
                f"<b>Amount:</b> {amount}\n"
                f"<b>Remaining quantity:</b> {details['quantity']}"
            )
            await context.bot.send_message(chat_id=log_sudo_user_id, text=log_text, parse_mode='HTML')
        else:
            await update.message.reply_text("This code has already been redeemed the maximum number of times.")
    else:
        await update.message.reply_text("Invalid code.")

application.add_handler(CommandHandler("daily_code", daily_code))
application.add_handler(CommandHandler("gen", gen))
application.add_handler(CommandHandler("redeem", redeem))
