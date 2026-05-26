from aiogram.fsm.context import FSMContext
import logging

async def show_screen(
  target,
  state: FSMContext,
  text: str,
  reply_markup=None,
  parse_mode: str | None = None,
  *,
  mode: str = "edit",
  keep_history: bool = False,
  disable_prev_kb: bool = True
):
    from aiogram.types import Message, CallbackQuery

    if isinstance(target, CallbackQuery):
      message = target.message
    else:
      message = target

    data = await state.get_data()
    last_id = data.get("last_message_id")

    # 1. отключаем старые кнопки
    if disable_prev_kb and last_id and not keep_history:
      try:
        await message.bot.edit_message_reply_markup(
          chat_id=message.chat.id,
          message_id=last_id,
          reply_markup=None
        )
      except:
        pass

    try:
      if mode == "edit":
        msg = await message.edit_text(
          text,
          reply_markup=reply_markup,
          parse_mode=parse_mode
        )

      elif mode == "replace":
        if last_id:
          try:
            await message.bot.delete_message(
              chat_id=message.chat.id,
              message_id=last_id
            )
          except:
            pass

          msg = await message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
          )

      else:  # mode == "new"
        msg = await message.answer(
          text,
          reply_markup=reply_markup,
          parse_mode=parse_mode
        )

    except Exception:
      # fallback если edit упал
      msg = await message.answer(
        text,
        reply_markup=reply_markup,
        parse_mode=parse_mode
      )

    await state.update_data(last_message_id=msg.message_id)
    return msg


async def show_success(target, state, text, kb):
  return await show_screen(
    target,
    state,
    f"✅ {text}",
    reply_markup=kb,
    mode="edit"
  )


async def show_error(target, state, text, kb):
  return await show_screen(
    target,
    state,
    f"❌ {text}",
    reply_markup=kb,
    mode="edit"
  )