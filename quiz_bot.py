import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from collections import defaultdict
from datetime import date
import json
import os

# ──────────────────────────────────────────
#  봇 설정
# ──────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ──────────────────────────────────────────
#  상식 퀴즈 문제 목록 (난이도별)
# ──────────────────────────────────────────

# 🟢 쉬움
QUIZ_EASY = [
    {"question": "대한민국의 수도는?", "answer": "서울", "hint": "한강이 흐르는 도시예요 🌊"},
    {"question": "1년은 몇 개월인가요?", "answer": "12", "hint": "달력을 생각해보세요 📅"},
    {"question": "태양계에서 가장 큰 행성은?", "answer": "목성", "hint": "줄무늬가 있는 거대한 행성이에요 🪐"},
    {"question": "물의 화학식은?", "answer": "H2O", "hint": "수소 2개 + 산소 1개 💧"},
    {"question": "사람의 심장은 몇 개인가요?", "answer": "1", "hint": "가슴 왼쪽에 있어요 ❤️"},
    {"question": "무지개는 몇 가지 색인가요?", "answer": "7", "hint": "빨주노초파남보 🌈"},
    {"question": "지구에서 가장 높은 산은?", "answer": "에베레스트", "hint": "히말라야 산맥에 있어요 🏔️"},
    {"question": "사과는 무슨 색인가요? (가장 대표적인 색)", "answer": "빨간색", "hint": "신호등의 정지 색이에요 🍎"},
    {"question": "일주일은 며칠인가요?", "answer": "7", "hint": "월화수목금토일 📆"},
    {"question": "대한민국의 국화는?", "answer": "무궁화", "hint": "여름에 피는 꽃이에요 🌸"},
]

# 🟡 보통
QUIZ_NORMAL = [
    {"question": "빛의 속도는 초속 약 몇 km인가요?", "answer": "30만", "hint": "3 뒤에 0이 다섯 개예요 💡"},
    {"question": "인체에서 가장 큰 기관은?", "answer": "피부", "hint": "몸 전체를 감싸고 있어요 🧍"},
    {"question": "한글을 만든 조선의 왕은?", "answer": "세종대왕", "hint": "4대 왕이에요 👑"},
    {"question": "올림픽은 몇 년마다 열리나요?", "answer": "4", "hint": "동계와 하계 각각 4년마다 🏅"},
    {"question": "피카소의 국적은?", "answer": "스페인", "hint": "이베리아 반도에 있는 나라예요 🎨"},
    {"question": "DNA의 이중나선 구조를 발견한 해는?", "answer": "1953", "hint": "20세기 중반이에요 🧬"},
    {"question": "세계에서 인구가 가장 많은 나라는?", "answer": "인도", "hint": "2023년 기준으로 중국을 앞질렀어요 🌏"},
    {"question": "음속은 초속 약 몇 m인가요?", "answer": "340", "hint": "340m/s 정도예요 🔊"},
    {"question": "태양계 행성의 수는?", "answer": "8", "hint": "명왕성은 2006년에 제외됐어요 🪐"},
    {"question": "이순신 장군이 활약한 전쟁은?", "answer": "임진왜란", "hint": "1592년에 시작된 전쟁이에요 ⚔️"},
]

# 🔴 어려움
QUIZ_HARD = [
    {"question": "원소 주기율표에서 금의 원소 기호는?", "answer": "Au", "hint": "라틴어 Aurum에서 유래했어요 🥇"},
    {"question": "상대성 이론을 발표한 과학자는?", "answer": "아인슈타인", "hint": "E=mc² 공식으로 유명해요 🧠"},
    {"question": "조선시대 최초의 실학자로 불리는 인물은?", "answer": "이수광", "hint": "지봉유설을 저술했어요 📚"},
    {"question": "인류 최초로 달에 착륙한 우주인은?", "answer": "닐 암스트롱", "hint": "1969년 아폴로 11호를 탔어요 🚀"},
    {"question": "세계에서 가장 긴 강은?", "answer": "나일강", "hint": "아프리카에 있어요 🌊"},
    {"question": "셰익스피어의 4대 비극 중 하나가 아닌 것은?", "answer": "베니스의 상인", "hint": "4대 비극은 햄릿, 오셀로, 리어왕, 맥베스예요 🎭"},
    {"question": "노벨상을 두 번 수상한 최초의 인물은?", "answer": "마리 퀴리", "hint": "물리학상과 화학상을 받았어요 🔬"},
    {"question": "대한민국 헌법 제1조 1항은?", "answer": "대한민국은 민주공화국이다", "hint": "민주공화국으로 시작해요 🇰🇷"},
    {"question": "피타고라스 정리에서 빗변을 c라 할 때 공식은?", "answer": "a²+b²=c²", "hint": "직각삼각형에 적용돼요 📐"},
    {"question": "인터넷 WWW를 발명한 사람은?", "answer": "팀 버너스리", "hint": "1989년에 제안했어요 🌐"},
]

# 난이도 매핑
QUIZ_MAP = {
    "쉬움": ("🟢 쉬움", QUIZ_EASY),
    "보통": ("🟡 보통", QUIZ_NORMAL),
    "어려움": ("🔴 어려움", QUIZ_HARD),
}

# 전체 문제 (자동퀴즈용)
QUIZ_DATA = QUIZ_EASY + QUIZ_NORMAL + QUIZ_HARD

# ──────────────────────────────────────────
#  상태 관리
# ──────────────────────────────────────────
# { channel_id: { "question": ..., "answer": ..., "hint": ..., "hint_used": bool, "task": asyncio.Task } }
active_quizzes: dict = {}

# { guild_id: { user_id: score } }
LEADERBOARD_FILE = "leaderboard.json"

def _load_leaderboard() -> dict:
    """파일에서 리더보드 불러오기"""
    if not os.path.exists(LEADERBOARD_FILE):
        return {}
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # JSON 키는 문자열이라 int로 변환
        return {int(g): {int(u): s for u, s in users.items()} for g, users in raw.items()}
    except Exception:
        return {}

def _save_leaderboard():
    """리더보드를 파일에 저장"""
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[리더보드 저장 오류] {e}")

# 시작 시 파일에서 불러오기
_raw = _load_leaderboard()
leaderboard: dict = defaultdict(lambda: defaultdict(int))
for g, users in _raw.items():
    for u, s in users.items():
        leaderboard[g][u] = s

TIMEOUT_SECONDS = 30  # 제한 시간 (초)
AUTO_QUIZ_INTERVAL = 3 * 60  # 자동 퀴즈 간격 (3분, 초 단위)

# { user_id: 연속 정답 횟수 }
combo: dict = defaultdict(int)

# { guild_id: { "channel_id": int, "diff_key": str } }  — 자동 퀴즈 설정
auto_quiz_channels: dict = {}

# { guild_id: asyncio.Task }  — 서버별 자동 퀴즈 루프 태스크
auto_quiz_tasks: dict = {}

# ──────────────────────────────────────────
#  오늘의 퀴즈 전용
# ──────────────────────────────────────────
DAILY_QUIZ_DATA = [
    {"question": "🌟 [오늘의 퀴즈] 세계에서 가장 작은 나라는?", "answer": "바티칸", "hint": "이탈리아 로마 안에 있어요 🇻🇦"},
    {"question": "🌟 [오늘의 퀴즈] 인간의 뼈는 몇 개인가요?", "answer": "206", "hint": "성인 기준이에요 🦴"},
    {"question": "🌟 [오늘의 퀴즈] 전기를 발명한 사람은?", "answer": "에디슨", "hint": "발명왕으로 불려요 💡"},
    {"question": "🌟 [오늘의 퀴즈] 지구의 자전 주기는?", "answer": "24시간", "hint": "하루와 같아요 🌍"},
    {"question": "🌟 [오늘의 퀴즈] 가장 가벼운 원소는?", "answer": "수소", "hint": "원자번호 1번이에요 ⚛️"},
    {"question": "🌟 [오늘의 퀴즈] 대한민국 최초의 대통령은?", "answer": "이승만", "hint": "1948년에 취임했어요 🇰🇷"},
    {"question": "🌟 [오늘의 퀴즈] 만유인력의 법칙을 발견한 과학자는?", "answer": "뉴턴", "hint": "사과가 떨어지는 걸 보고 발견했다고 해요 🍎"},
]

# { guild_id: { "date": date, "used_by": set(user_id), "q_index": int } }
daily_quiz_state: dict = {}


def _get_daily_quiz(guild_id: int) -> dict:
    """오늘 날짜 기준으로 고정된 문제를 반환 (날짜 바뀌면 자동 갱신)"""
    today = date.today()
    state = daily_quiz_state.get(guild_id)

    if state is None or state["date"] != today:
        # 날짜가 바뀌었거나 처음이면 오늘 날짜 seed로 문제 선택
        idx = today.toordinal() % len(DAILY_QUIZ_DATA)
        daily_quiz_state[guild_id] = {
            "date": today,
            "used_by": set(),
            "q_index": idx,
        }

    q = DAILY_QUIZ_DATA[daily_quiz_state[guild_id]["q_index"]]
    return q

# ──────────────────────────────────────────
#  봇 준비
# ──────────────────────────────────────────
@bot.event
async def on_ready():
    # 리더보드 파일 없으면 빈 파일 미리 생성
    if not os.path.exists(LEADERBOARD_FILE):
        _save_leaderboard()
        print(f"📁 {LEADERBOARD_FILE} 파일 생성 완료")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {bot.user} 로그인 완료! 슬래시 커맨드 {len(synced)}개 동기화됨")
    except Exception as e:
        print(f"❌ 커맨드 동기화 실패: {e}")


# ──────────────────────────────────────────
#  /quiz  —  퀴즈 시작
# ──────────────────────────────────────────
@bot.tree.command(name="quiz", description="상식 퀴즈를 시작합니다!")
@app_commands.describe(난이도="쉬움 / 보통 / 어려움 (기본: 랜덤)")
@app_commands.choices(난이도=[
    app_commands.Choice(name="🟢 쉬움", value="쉬움"),
    app_commands.Choice(name="🟡 보통", value="보통"),
    app_commands.Choice(name="🔴 어려움", value="어려움"),
])
async def quiz(interaction: discord.Interaction, 난이도: app_commands.Choice[str] = None):
    channel_id = interaction.channel_id

    if channel_id in active_quizzes:
        await interaction.response.send_message(
            "⚠️ 이미 퀴즈가 진행 중이에요! 먼저 맞춰보세요 😊", ephemeral=True
        )
        return

    if 난이도 is None:
        # 랜덤 난이도
        diff_key = random.choice(["쉬움", "보통", "어려움"])
    else:
        diff_key = 난이도.value

    diff_label, pool = QUIZ_MAP[diff_key]
    q = random.choice(pool)

    # 난이도별 점수
    score_map = {"쉬움": 1, "보통": 2, "어려움": 4}
    base_score = score_map[diff_key]

    active_quizzes[channel_id] = {
        "question": q["question"],
        "answer": q["answer"],
        "hint": q["hint"],
        "hint_used": False,
        "task": None,
        "diff_label": diff_label,
        "base_score": base_score,
    }

    color_map = {"쉬움": discord.Color.green(), "보통": discord.Color.gold(), "어려움": discord.Color.red()}
    embed = discord.Embed(
        title=f"🧠 상식 퀴즈! [{diff_label}]",
        description=f"**{q['question']}**",
        color=color_map[diff_key],
    )
    embed.set_footer(text=f"⏱️ {TIMEOUT_SECONDS}초 안에 채팅으로 답을 입력하세요! | /hint 로 힌트 | 정답 시 +{base_score}점")

    await interaction.response.send_message(embed=embed)

    # 타임아웃 태스크 — channel_id만 넘기고 내부에서 get_channel 사용
    task = asyncio.create_task(_quiz_timeout(channel_id))
    active_quizzes[channel_id]["task"] = task


async def _quiz_timeout(channel_id):
    try:
        await asyncio.sleep(TIMEOUT_SECONDS)
        if channel_id not in active_quizzes:
            return
        answer = active_quizzes[channel_id]["answer"]
        del active_quizzes[channel_id]

        channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)

        embed = discord.Embed(
            title="⏰ 시간 초과!",
            description=f"아무도 맞추지 못했어요...\n정답은 **{answer}** 였습니다!",
            color=discord.Color.red(),
        )
        await channel.send(embed=embed)
    except (discord.Forbidden, discord.NotFound):
        # 채널 접근 권한 없음 또는 채널 없음 — 상태만 정리
        active_quizzes.pop(channel_id, None)
    except asyncio.CancelledError:
        pass  # 정답을 맞춰서 취소된 경우, 정상 종료


# ──────────────────────────────────────────
#  /hint  —  힌트
# ──────────────────────────────────────────
@bot.tree.command(name="hint", description="현재 퀴즈의 힌트를 봅니다 (점수 -1)")
async def hint(interaction: discord.Interaction):
    channel_id = interaction.channel_id

    if channel_id not in active_quizzes:
        await interaction.response.send_message(
            "❓ 진행 중인 퀴즈가 없어요. `/quiz` 로 시작하세요!", ephemeral=True
        )
        return

    quiz_data = active_quizzes[channel_id]

    if quiz_data["hint_used"]:
        await interaction.response.send_message(
            f"💡 힌트: **{quiz_data['hint']}**\n*(이미 힌트를 사용했어요)*",
            ephemeral=False,
        )
        return

    quiz_data["hint_used"] = True
    embed = discord.Embed(
        title="💡 힌트!",
        description=quiz_data["hint"],
        color=discord.Color.blue(),
    )
    embed.set_footer(text="힌트를 사용하면 정답 시 점수가 1점 차감됩니다")
    await interaction.response.send_message(embed=embed)


# ──────────────────────────────────────────
#  /leaderboard  —  리더보드
# ──────────────────────────────────────────
@bot.tree.command(name="leaderboard", description="서버 퀴즈 랭킹을 확인합니다")
async def show_leaderboard(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    scores = leaderboard.get(guild_id, {})

    if not scores:
        await interaction.response.send_message(
            "📋 아직 점수가 없어요. `/quiz` 로 게임을 시작하세요!", ephemeral=True
        )
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    medals = ["🥇", "🥈", "🥉"]

    embed = discord.Embed(title="🏆 퀴즈 리더보드", color=discord.Color.purple())

    lines = []
    for i, (user_id, score) in enumerate(sorted_scores[:10]):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        try:
            user = await bot.fetch_user(user_id)
            name = user.display_name
        except Exception:
            name = f"유저{user_id}"
        lines.append(f"{medal} {name} — **{score}점**")

    embed.description = "\n".join(lines)
    await interaction.response.send_message(embed=embed)


# ──────────────────────────────────────────
#  /score  —  내 점수
# ──────────────────────────────────────────
@bot.tree.command(name="score", description="내 퀴즈 점수를 확인합니다")
async def my_score(interaction: discord.Interaction):
    score = leaderboard[interaction.guild_id][interaction.user.id]
    await interaction.response.send_message(
        f"🎯 {interaction.user.mention}님의 점수: **{score}점**", ephemeral=True
    )


# ──────────────────────────────────────────
#  채팅 메시지로 정답 체크
# ──────────────────────────────────────────
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    channel_id = message.channel.id
    if channel_id not in active_quizzes:
        await bot.process_commands(message)
        return

    quiz_data = active_quizzes[channel_id]
    correct_answer = quiz_data["answer"].strip()
    user_answer = message.content.strip()

    # 슬래시 커맨드는 정답 판정 제외
    if user_answer.startswith("/"):
        await bot.process_commands(message)
        return

    # 정답 판정 (대소문자·공백 무시)
    if user_answer.replace(" ", "").lower() == correct_answer.replace(" ", "").lower():
        # 타임아웃 태스크 취소
        if quiz_data["task"]:
            quiz_data["task"].cancel()
        del active_quizzes[channel_id]

        # 점수 계산 (오늘의퀴즈면 보너스 +5점)
        is_daily = quiz_data.get("is_daily", False)
        if is_daily:
            base_score = 5
            combo[message.author.id] = 0  # 오늘의퀴즈는 콤보 미적용
        else:
            base_score = quiz_data.get("base_score", 2)
            if quiz_data["hint_used"]:
                base_score = max(1, base_score - 1)

            # 콤보 처리
            combo[message.author.id] += 1
            current_combo = combo[message.author.id]
            combo_bonus = 0
            combo_msg = ""
            if current_combo == 2:
                combo_bonus = 1
                combo_msg = "🔥 2콤보! +1점 보너스!"
            elif current_combo == 3:
                combo_bonus = 2
                combo_msg = "🔥🔥 3콤보! +2점 보너스!"
            elif current_combo == 4:
                combo_bonus = 3
                combo_msg = "🔥🔥🔥 4콤보! +3점 보너스!"
            elif current_combo >= 5:
                combo_bonus = 5
                combo_msg = f"💥 {current_combo}콤보!! +5점 보너스!"
            base_score += combo_bonus

        leaderboard[message.guild.id][message.author.id] += base_score
        _save_leaderboard()  # 파일에 즉시 저장

        combo_text = f"\n{combo_msg}" if not is_daily and combo_msg else ""
        embed = discord.Embed(
            title="🎉 정답!" if not is_daily else "🌟 오늘의 퀴즈 정답!",
            description=(
                f"{message.author.mention}님이 맞췄어요!\n"
                f"정답: **{correct_answer}**\n"
                f"획득 점수: **+{base_score}점**"
                + (" *(힌트 사용으로 -1점)*" if quiz_data["hint_used"] and not is_daily else "")
                + (" 🌟 *오늘의 퀴즈 보너스!*" if is_daily else "")
                + combo_text
            ),
            color=discord.Color.orange() if is_daily else discord.Color.green(),
        )
        total = leaderboard[message.guild.id][message.author.id]
        combo_footer = f" | 🔥 {combo[message.author.id]}콤보 진행중!" if not is_daily and combo[message.author.id] >= 2 else ""
        embed.set_footer(text=f"누적 점수: {total}점{combo_footer} | /quiz 로 다음 문제!")
        await message.channel.send(embed=embed)

    else:
        # 틀리면 콤보 초기화
        if combo[message.author.id] >= 2:
            await message.reply(f"아, 아니에요...! 😳 {combo[message.author.id]}콤보가 끊겼어요...💦", mention_author=False)
        else:
            wrong_responses = [
                "아, 아니에요...! 다시 생각해봐요 😳",
                "으으... 그건 아닌데... 힌트 쓸래요? `/hint` 💦",
                "흐엥... 틀렸어요... 좀 더 생각해봐요 🥺",
                "어, 어... 아닌 것 같은데요...! 😖",
                "으... 아니에요... 다시 해봐요...! 🙈",
                "저, 정답이 아니에요...! 힌트 줄까요? 💧",
            ]
            await message.reply(random.choice(wrong_responses), mention_author=False)
        combo[message.author.id] = 0

    await bot.process_commands(message)


# ──────────────────────────────────────────
#  /오늘의퀴즈  —  하루 1번 특별 문제
# ──────────────────────────────────────────
@bot.tree.command(name="오늘의퀴즈", description="하루에 한 번 도전할 수 있는 특별 퀴즈! (정답 시 +5점)")
async def daily_quiz(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    user_id = interaction.user.id
    channel_id = interaction.channel_id

    q = _get_daily_quiz(guild_id)
    state = daily_quiz_state[guild_id]

    # 오늘 이미 참여했는지 확인
    if user_id in state["used_by"]:
        await interaction.response.send_message(
            f"⏳ {interaction.user.mention}님은 오늘의 퀴즈에 이미 참여하셨어요!\n내일 자정 이후 다시 도전하세요!",
            ephemeral=True,
        )
        return

    # 채널에 이미 활성 퀴즈가 있으면 막기
    if channel_id in active_quizzes:
        await interaction.response.send_message(
            "⚠️ 이미 진행 중인 퀴즈가 있어요! 먼저 끝내주세요 😊", ephemeral=True
        )
        return

    # 참여 기록
    state["used_by"].add(user_id)

    active_quizzes[channel_id] = {
        "question": q["question"],
        "answer": q["answer"],
        "hint": q["hint"],
        "hint_used": False,
        "task": None,
        "is_daily": True,
        "daily_user": user_id,
    }

    embed = discord.Embed(
        title="🌟 오늘의 퀴즈!",
        description=f"**{q['question']}**",
        color=discord.Color.orange(),
    )
    embed.add_field(name="보너스", value="정답 시 **+5점** 획득!", inline=False)
    embed.set_footer(text=f"⏱️ {TIMEOUT_SECONDS}초 안에 채팅으로 답을 입력하세요! | /hint 로 힌트")

    await interaction.response.send_message(embed=embed)

    task = asyncio.create_task(_quiz_timeout(channel_id))
    active_quizzes[channel_id]["task"] = task


# ──────────────────────────────────────────
#  자동 퀴즈 루프
# ──────────────────────────────────────────
async def _auto_quiz_loop(guild_id: int):
    """3분마다 지정 채널에 자동으로 퀴즈를 올리는 루프"""
    while True:
        try:
            cfg = auto_quiz_channels.get(guild_id)
            if cfg is None:
                break

            channel_id = cfg["channel_id"]
            diff_key = cfg["diff_key"]

            # 이미 해당 채널에 퀴즈가 진행 중이면 스킵
            if channel_id in active_quizzes:
                await asyncio.sleep(AUTO_QUIZ_INTERVAL)
                continue

            channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)

            # 난이도 선택
            if diff_key == "랜덤":
                actual_diff = random.choice(["쉬움", "보통", "어려움"])
            else:
                actual_diff = diff_key
            diff_label, pool = QUIZ_MAP[actual_diff]
            q = random.choice(pool)

            score_map = {"쉬움": 1, "보통": 2, "어려움": 4}
            base_score = score_map[actual_diff]
            color_map = {"쉬움": discord.Color.green(), "보통": discord.Color.gold(), "어려움": discord.Color.red()}

            active_quizzes[channel_id] = {
                "question": q["question"],
                "answer": q["answer"],
                "hint": q["hint"],
                "hint_used": False,
                "task": None,
                "diff_label": diff_label,
                "base_score": base_score,
            }

            embed = discord.Embed(
                title=f"⏰ 자동 퀴즈 타임! [{diff_label}]",
                description=f"**{q['question']}**",
                color=color_map[actual_diff],
            )
            embed.set_footer(text=f"⏱️ {TIMEOUT_SECONDS}초 안에 채팅으로 답을 입력하세요! | /hint 로 힌트 | 정답 시 +{base_score}점")
            await channel.send(embed=embed)

            task = asyncio.create_task(_quiz_timeout(channel_id))
            active_quizzes[channel_id]["task"] = task

        except asyncio.CancelledError:
            break
        except (discord.Forbidden, discord.NotFound):
            auto_quiz_channels.pop(guild_id, None)
            break
        except Exception as e:
            print(f"[자동퀴즈 오류] {e}")

        await asyncio.sleep(AUTO_QUIZ_INTERVAL)


# ──────────────────────────────────────────
#  /자동퀴즈  —  자동 퀴즈 설정 / 해제
# ──────────────────────────────────────────
@bot.tree.command(name="자동퀴즈", description="지정 채널에 3분마다 자동으로 퀴즈를 올립니다")
@app_commands.describe(채널="퀴즈를 올릴 채널을 선택하세요", 난이도="출제할 난이도 (기본: 랜덤)")
@app_commands.choices(난이도=[
    app_commands.Choice(name="🎲 랜덤", value="랜덤"),
    app_commands.Choice(name="🟢 쉬움", value="쉬움"),
    app_commands.Choice(name="🟡 보통", value="보통"),
    app_commands.Choice(name="🔴 어려움", value="어려움"),
])
async def auto_quiz(interaction: discord.Interaction, 채널: discord.TextChannel = None, 난이도: app_commands.Choice[str] = None):
    guild_id = interaction.guild_id

    # 채널 없이 입력 → 자동퀴즈 해제
    if 채널 is None:
        if guild_id in auto_quiz_channels:
            auto_quiz_channels.pop(guild_id)
            task = auto_quiz_tasks.pop(guild_id, None)
            if task:
                task.cancel()
            await interaction.response.send_message("⏹️ 자동 퀴즈를 해제했어요!")
        else:
            await interaction.response.send_message(
                "❓ 자동 퀴즈가 설정되어 있지 않아요.\n`/자동퀴즈 #채널` 로 설정하세요!", ephemeral=True
            )
        return

    diff_key = 난이도.value if 난이도 else "랜덤"

    # 기존 루프 취소 후 새로 시작
    old_task = auto_quiz_tasks.pop(guild_id, None)
    if old_task:
        old_task.cancel()

    auto_quiz_channels[guild_id] = {"channel_id": 채널.id, "diff_key": diff_key}
    task = asyncio.create_task(_auto_quiz_loop(guild_id))
    auto_quiz_tasks[guild_id] = task

    diff_label = QUIZ_MAP[diff_key][0] if diff_key != "랜덤" else "🎲 랜덤"
    embed = discord.Embed(
        title="✅ 자동 퀴즈 설정 완료!",
        description=f"{채널.mention} 채널에 **3분마다** [{diff_label}] 퀴즈가 올라와요!",
        color=discord.Color.green(),
    )
    embed.set_footer(text="해제하려면 /자동퀴즈 (채널 없이) 입력")
    await interaction.response.send_message(embed=embed)


# ──────────────────────────────────────────
#  /상점  —  포인트로 아이템 구매
# ──────────────────────────────────────────
SHOP_ITEMS = {
    "타임아웃": {
        "desc": "다른 유저를 3분간 타임아웃 시킵니다 😈",
        "price": 100,
        "emoji": "🔇",
    },
}

@bot.tree.command(name="상점", description="퀴즈 점수로 구매할 수 있는 상점입니다")
async def shop(interaction: discord.Interaction):
    my_score = leaderboard[interaction.guild_id][interaction.user.id]

    embed = discord.Embed(
        title="🛒 퀴즈 상점",
        description=f"현재 내 점수: **{my_score}점**",
        color=discord.Color.blurple(),
    )
    for name, item in SHOP_ITEMS.items():
        affordable = "✅ 구매 가능" if my_score >= item["price"] else "❌ 점수 부족"
        embed.add_field(
            name=f"{item['emoji']} {name} — {item['price']}점",
            value=f"{item['desc']}\n{affordable}\n`/구매 {name} @유저`",
            inline=False,
        )
    embed.set_footer(text="퀴즈를 맞춰서 점수를 모아보세요!")
    await interaction.response.send_message(embed=embed)


# ──────────────────────────────────────────
#  /구매  —  아이템 사용
# ──────────────────────────────────────────
@bot.tree.command(name="구매", description="상점 아이템을 구매해 사용합니다")
@app_commands.describe(아이템="구매할 아이템 이름", 대상="아이템을 사용할 유저")
@app_commands.choices(아이템=[
    app_commands.Choice(name="🔇 타임아웃 (100점) — 상대방을 3분간 타임아웃", value="타임아웃"),
])
async def buy(interaction: discord.Interaction, 아이템: app_commands.Choice[str], 대상: discord.Member):
    guild_id = interaction.guild_id
    buyer = interaction.user
    item_key = 아이템.value
    item = SHOP_ITEMS[item_key]

    # 자기 자신에게 사용 방지
    if 대상.id == buyer.id:
        await interaction.response.send_message("❌ 자기 자신에게는 사용할 수 없어요!", ephemeral=True)
        return

    # 봇에게 사용 방지
    if 대상.bot:
        await interaction.response.send_message("❌ 봇에게는 사용할 수 없어요!", ephemeral=True)
        return

    my_score = leaderboard[guild_id][buyer.id]

    # 점수 확인
    if my_score < item["price"]:
        await interaction.response.send_message(
            f"❌ 점수가 부족해요!\n필요 점수: **{item['price']}점** | 현재 점수: **{my_score}점**",
            ephemeral=True,
        )
        return

    # 타임아웃 처리
    if item_key == "타임아웃":
        try:
            import datetime
            await 대상.timeout(datetime.timedelta(minutes=3), reason=f"퀴즈 상점: {buyer.display_name}님이 사용")
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ 봇에게 타임아웃 권한이 없어요!\n서버 설정에서 봇에게 **멤버 타임아웃** 권한을 주세요.",
                ephemeral=True,
            )
            return
        except Exception as e:
            await interaction.response.send_message(f"❌ 오류 발생: {e}", ephemeral=True)
            return

        # 점수 차감 및 저장
        leaderboard[guild_id][buyer.id] -= item["price"]
        _save_leaderboard()

        embed = discord.Embed(
            title="🔇 타임아웃 발동!",
            description=(
                f"{buyer.mention}님이 **{item['price']}점**을 사용해서\n"
                f"{대상.mention}님을 **3분간 타임아웃** 시켰어요! 😈"
            ),
            color=discord.Color.dark_red(),
        )
        remaining = leaderboard[guild_id][buyer.id]
        embed.set_footer(text=f"{buyer.display_name}님 남은 점수: {remaining}점")
        await interaction.response.send_message(embed=embed)


# ──────────────────────────────────────────
#  봇 실행
# ──────────────────────────────────────────
if __name__ == "__main__":
    TOKEN = "MTQ5MjM2MTc0NTczMjQ3MjkzNA.GhCe06.1b6Mq-Df25cZivQ0svXfBBBChGwxFk_4SlCYac"  # ← Discord Developer Portal에서 발급
    bot.run(TOKEN)